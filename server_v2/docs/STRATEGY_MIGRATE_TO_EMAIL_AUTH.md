# Estratégia de Branching e PRs — Migração SAv1.5 (Auth por Email)

## ⚠️ Ambientes — Nunca Confundir

| Ambiente | Containers | Porta | Diretório EC2 | Propósito |
|---|---|---|---|---|
| **SA-v1 (produção)** | `flashcard_server`, `flashcard_client` | 8081 | `/opt/study-amigo/server` | Alunos em uso — **NÃO TOCAR** |
| **SAv1.5 (staging)** | `v15_server`, `v15_client` | 8082 | `/opt/study-amigo-v15/server` | Testes da migração de email |

**Regra absoluta:** Toda alteração de código, banco e `.env` para SAv1.5 vai EXCLUSIVAMENTE em:
- Código local: `server/app.py` (este repositório, branch atual)
- EC2: `/opt/study-amigo-v15/server/`
- Container: `v15_server` / `v15_client`

**Nunca** tocar em `flashcard_server`, `flashcard_client`, ou `/opt/study-amigo/` ao trabalhar na SAv1.5.

---

## Contexto

Este documento define a estratégia de controle de versão para a migração SAv1.5, descrita em detalhe em `PLAN_MIGRATE_TO_EMAIL_AUTH.md`. O objetivo é implementar autenticação por email e troca de senha sem quebrar a produção durante o desenvolvimento.

---

## Estratégia: 1 branch de feature + 2 Pull Requests

### Branch único: `feat/email-auth`

```
main  ──────────────────────────────────────────────────────────────────► (produção)
         \                          ▲                          ▲
          feat/email-auth ──────────┼──────────────────────────┼──────►
           (scripts/infra)     PR 1 → main              PR 2 → main
           (backend/frontend)  (sem risco, cedo)         (cutover final)
```

**Por que um branch único, não um por fase?**

- As fases 2, 3 e 4 têm dependências cruzadas (backend + frontend mudam juntos)
- Fazer merge parcial (só backend, sem frontend) em `main` colocaria produção em estado inconsistente
- O servidor paralelo (porta 8082) já isola o risco — o branch inteiro fica lá até validar

---

## Quando abrir Pull Requests

### PR 1 — Scripts e infra (sem código de app)

**Quando:** Assim que os scripts estiverem prontos
**O que inclui:**

- `server_v2/scripts/setup_parallel_server.sh`
- `server_v2/docker-compose.v1.5.yml`
- `maintenance/index.html`
- `server_v2/scripts/add_email_to_admin_db.py`
- `server_v2/scripts/smoke_test.py`

**Por que PR aqui:** Scripts são revisáveis independentemente do código de app. Não afetam produção. Podem ser mergeados em `main` com segurança porque são ferramentas, não código executável pelo servidor.

**Gatilhos obrigatórios antes de abrir o PR 1:**

```
[ ] add_email_to_admin_db.py --dry-run passa sem erros contra cache local do admin.db
[ ] setup_parallel_server.sh sobe containers v1.5 em :8082 sem erro
[ ] curl http://54.152.109.26:8082 retorna 200 (frontend carrega)
```

---

### PR 2 — Backend + Frontend (cutover)

**Quando:** Após o servidor paralelo validar tudo
**O que inclui:**

- `server/app.py` (login por email, register salva email, `POST /change-password`)
- `server/test_api_v1.5.py`
- `server/test_race_condition/test_frontend_flow.py` (atualizado com `--url`)
- `client/src/components/LoginForm.jsx`
- `client/src/components/ChangePasswordForm.jsx`
- `client/src/pages/AuthPage.jsx`
- `client/src/i18n/*.json`
- `server/requirements.txt` (`dnspython`)

**Este PR é o cutover.** Merge → deploy → produção vira SAv1.5.

**Gatilhos obrigatórios antes de abrir o PR 2:**

```
Nível 1 — unitário (roda localmente, sem servidor):
[ ] python -m unittest server/test_supermemo_2.py -v       → 100% pass (inalterado)
[ ] python -m unittest server/test_api_v1.5.py -v          → 100% pass
    cobre: login por email, POST /change-password (sucesso, senha errada,
           senha curta, sem sessão), aba Cadastro retorna erro via API

Nível 2 — smoke (roda contra servidor paralelo em :8082):
[ ] python server_v2/scripts/smoke_test.py \
      --url http://54.152.109.26:8082                      → 100% pass

Nível 3 — concorrência (roda contra servidor paralelo em :8082):
[ ] python server/test_race_condition/test_frontend_flow.py \
      --url http://54.152.109.26:8082                      → sem race conditions

Infra (pré-requisito de ambiente):
[ ] IAM role da instância EC2 tem permissão ses:SendEmail para identity/noreply@metads.app
[ ] server/.env contém: SES_SENDER_EMAIL, SES_AWS_REGION, APP_BASE_URL
[ ] docker compose restart server após atualizar .env

Dados (pré-requisito de infra):
[ ] add_email_to_admin_db.py --production executado com sucesso
[ ] Zero usuários com email NULL no admin.db de produção
```

---

## Fluxo completo

```
# Hoje
git checkout -b feat/email-auth

# Desenvolvimento (dias 1-3)
  → scripts de infra + smoke_test.py     → commit
  → docker-compose paralelo              → commit
  → backend: app.py                      → commit
  → frontend: 3 componentes              → commit
  → test_api_v1.5.py + atualizar         →  commit
    test_frontend_flow.py (--url)

# Gatilhos PR 1 (smoke de infra):
  → add_email_to_admin_db.py --dry-run   OK
  → setup_parallel_server.sh em :8082    OK
  → curl :8082 retorna 200               OK

# PR 1: mergeado cedo, sem risco
  feat/email-auth → main  (scripts/infra + smoke_test.py)

# Validação (dia 3-4) — gatilhos PR 2:
  → test_supermemo_2.py                  100% pass (local)
  → test_api_v1.5.py                     100% pass (local)
  → smoke_test.py --url :8082            100% pass
  → test_frontend_flow.py --url :8082    sem race conditions
  → add_email_to_admin_db.py --production OK
  → zero emails NULL no admin.db         confirmado

# PR 2: cutover
  feat/email-auth → main  (app.py + frontend + testes)
  → deploy produção
  → manutenção desativada
```

---

## Variação mais conservadora (opcional)

Se quiser ainda mais segurança, pode usar **dois branches**:

```
main
  └── feat/email-auth-infra    → PR 1 (scripts, sem app)
  └── feat/email-auth-app      → PR 2 (backend + frontend, cutover)
```

Dado que o servidor paralelo já é o mecanismo principal de segurança, um branch único com dois PRs é suficiente e menos burocrático. Os dois branches só fazem sentido se a equipe for maior ou se o repositório exigir revisão de código por pares antes de qualquer merge em `main`.

---

## Regras de proteção

| Regra | Detalhe |
|---|---|
| `main` nunca quebra produção | Nenhum commit direto em `main` — só via PR |
| PR 2 tem pré-requisito obrigatório | Checklist Fase 5 do plano 100% verde antes do merge |
| Servidor paralelo é a staging | Toda validação ocorre em `:8082`, nunca em `:80` |
| Dados de produção protegidos | `add_email_to_admin_db.py` roda com `--dry-run` primeiro, sempre |
| `main` nunca recebe PR 2 sem emails populados | Rodar `add_email_to_admin_db.py --production` **antes** do deploy do `app.py` novo |
| Ambiente configurado antes do deploy | IAM role EC2 com `ses:SendEmail` + `SES_SENDER_EMAIL`, `SES_AWS_REGION`, `APP_BASE_URL` no `server/.env` |

---

## Entregáveis de teste a criar

| Entregável | Onde | Nível | Quando |
|---|---|---|---|
| `smoke_test.py` | `server_v2/scripts/` | Smoke (HTTP) | Junto com PR 1 |
| `test_api_v1.5.py` | `server/` | Unitário | Antes do PR 2 |
| `test_frontend_flow.py` (atualizar) | `server/test_race_condition/` | Concorrência | Antes do PR 2 |

---

## Resumo de decisões

| Decisão | Escolha |
|---|---|
| Branches | 1 único: `feat/email-auth` |
| PRs | 2: infra primeiro, app no cutover |
| Gatilho do PR 1 | Smoke de infra: dry-run + :8082 no ar + curl 200 |
| Gatilho do PR 2 | 3 níveis de teste 100% verdes + emails populados em produção |
| Proteção de `main` | Nunca mergear PR 2 sem servidor paralelo validado |
| Mecanismo de staging | Servidor paralelo EC2 porta `8082` |
