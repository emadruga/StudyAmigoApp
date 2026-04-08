# Plano de Migração SAv2: Autenticação via Clerk

## Contexto

O sistema atual (SAv1) autentica alunos com `username` + `senha` via bcrypt. Isso gerou proliferação de contas duplicadas por esquecimento de senha. O SAv2 substitui esse mecanismo por autenticação via **Clerk** (email), rodando em paralelo com produção em `/opt/studyamigo_v2/` até o cutover final.

### Estado atual (SAv1)

| Aspecto | Detalhe |
|---|---|
| `admin.db` schema | `user_id`, `username`, `name`, `password_hash` — sem email |
| Autenticação | `POST /login` com username + bcrypt |
| Sessões | Flask-Session filesystem (`flask_session/`) |
| Bancos por aluno | `user_dbs/user_{user_id}.db` |
| Alunos canônicos | 64 (definidos em `server_v2/bases/curated_student_roster_v2.csv`) |

### Decisões de design

- Os `user_id` de produção (SAv1) são mantidos no SAv2 — sem renumeração
- A coluna `ID` do CSV é a **matrícula** do aluno (ex: `4056`), guardada no `admin.db` do SAv2 como campo informativo, mas **não** usada como `user_id`
- `username` e `password_hash` removidos do schema — autenticação passa a ser 100% via Clerk
- `POST /register` removido do backend; novos alunos são criados pelo professor via Clerk Dashboard
- Duplicatas com 0 reviews e 0 cards novos são descartadas (não migradas)
- Todos os endpoints existentes (`/decks`, `/cards`, `/review`, etc.) permanecem inalterados — continuam usando `session['user_id']`

---

## Arquivos de referência

| Arquivo | Descrição |
|---|---|
| `server_v2/bases/curated_student_roster_v2.csv` | Roster canônico: 64 alunos com `ID` (matrícula), `Email`, `Nome`, `Curso`, `Caminho`, `Tier` |
| `server_v2/bases/email_mapping.csv` | **A ser criado na Fase 0**: mapeia `email` → `prod_user_id` |
| `server_v2/scripts/` | Scripts de migração (criados nas fases abaixo) |
| `server_v2/docs/` | Esta documentação |

---

## Fase 0 — Mapeamento e limpeza de duplicatas

**Objetivo:** Construir `email_mapping.csv`, que é o artefato central da migração. Cada linha diz: "o aluno com este email tem seus dados no banco `user_{prod_user_id}.db` de produção".

Não há renumeração de IDs: os `user_id` de produção são herdados diretamente pelo SAv2.

### 0.1 — Listar todos os usuários de produção com contagem de atividade

```bash
python server/tools/manage_users.py --list-dupes --production
```

Para cada nome do CSV, identificar qual(is) `user_id` de produção correspondem. Anotar:
- `prod_user_id` com mais cards/reviews → conta canônica
- demais → duplicatas descartáveis (se tiverem 0 reviews e 0 novos cards)

### 0.2 — Construir `email_mapping.csv`

Formato esperado:

```
email,prod_user_id,matricula,nome,curso,caminho,tier
amandasilvadonascimentosilva@gmail.com,87,4000,Amanda Silva do Nascimento,Metrologia,,
alineekaua2020@gmail.com,107,4056,Kauã Alves da Silva de França,Metrologia,A,Tier 1
...
```

Regras:
- 1 linha por aluno canônico (64 linhas)
- `prod_user_id` = `user_id` em produção com mais atividade
- Alunos sem conta em produção (nunca fizeram login): `prod_user_id` = `NULL`
- `matricula` = coluna `ID` do CSV (informativa, não vira `user_id`)

### 0.3 — Listar duplicatas descartáveis

Alunos com múltiplas contas onde a(s) conta(s) extra(s) têm 0 reviews E 0 novos cards → listar `prod_user_id` extras para exclusão futura. Não é necessário deletar agora; simplesmente não serão migrados.

**Critério de descarte:**
```sql
-- Na conta duplicada:
SELECT count(*) FROM revlog;   -- deve ser 0
SELECT count(*) FROM notes;    -- deve ser 0
```

**Entregável:** `server_v2/bases/email_mapping.csv` completo e revisado.

---

## Fase 1 — Novo schema `admin.db`

**Objetivo:** Definir e criar o schema do SAv2, sem `username` e sem `password_hash`.

### 1.1 — DDL do novo `admin.db`

```sql
CREATE TABLE users (
    user_id    INTEGER PRIMARY KEY,  -- mesmo user_id de produção (herdado do SAv1)
    email      TEXT UNIQUE NOT NULL, -- chave de autenticação via Clerk
    name       TEXT NOT NULL,
    matricula  TEXT,                 -- ID do CSV (informativo, ex: "4056")
    clerk_id   TEXT UNIQUE,          -- preenchido no primeiro login (NULL até então)
    curso      TEXT,                 -- Metrologia | SegCiber | Biotecnologia
    caminho    TEXT,                 -- A | B | C
    tier       TEXT                  -- Tier 1 | Tier 2
);
```

### 1.2 — Script: `server_v2/scripts/create_v2_admin_db.py`

Lê `email_mapping.csv` e cria `server_v2/server/admin.db` com os 64 alunos. Todos os `clerk_id` iniciam como `NULL`.

**Validações embutidas no script:**
- Nenhum email duplicado
- Nenhum `user_id` duplicado
- Nenhuma matrícula duplicada
- Contagem final deve ser exatamente 64 linhas

**Execução:**
```bash
python server_v2/scripts/create_v2_admin_db.py \
  --mapping server_v2/bases/email_mapping.csv \
  --output server_v2/server/admin.db
```

---

## Fase 2 — Scripts de migração de bancos de alunos

**Objetivo:** Copiar os bancos Anki de produção para o SAv2. Como os `user_id` são mantidos, os nomes dos arquivos não mudam: `user_{prod_user_id}.db` → `user_{prod_user_id}.db`.

### 2.1 — Script: `server_v2/scripts/migrate_user_dbs.py`

Lê `email_mapping.csv` e para cada aluno com `prod_user_id` não-nulo:

1. Baixa `user_dbs/user_{prod_user_id}.db` do EC2 via SCP
2. Salva como `server_v2/server/user_dbs/user_{prod_user_id}.db` (nome idêntico)
3. Valida integridade: conta de cards e reviews antes/depois deve bater

Alunos com `prod_user_id = NULL`: cria banco Anki vazio via a função `get_user_db_path()` existente no momento do primeiro login.

**Execução:**
```bash
python server_v2/scripts/migrate_user_dbs.py \
  --mapping server_v2/bases/email_mapping.csv \
  --prod-host 54.152.109.26 \
  --prod-key ~/.ssh/study-amigo-aws \
  --prod-userdb /opt/study-amigo/server/user_dbs/ \
  --output-dir server_v2/server/user_dbs/
```

### 2.2 — Script: `server_v2/scripts/validate_migration.py`

Verifica pós-migração:

| Verificação | Critério |
|---|---|
| Contagem de alunos | Exatamente 64 em `admin.db` |
| Bancos presentes | `user_{prod_user_id}.db` existe para todos com `prod_user_id` não-nulo |
| Integridade por aluno | Soma de cards e reviews bate com produção |
| Sem `clerk_id` duplicado | Todos `NULL` antes do primeiro login |
| Emails únicos | Nenhum email aparece duas vezes |

**Execução:**
```bash
python server_v2/scripts/validate_migration.py \
  --mapping server_v2/bases/email_mapping.csv \
  --v2-db server_v2/server/admin.db \
  --v2-userdb server_v2/server/user_dbs/ \
  --prod-host 54.152.109.26 \
  --prod-key ~/.ssh/study-amigo-aws
```

---

## Fase 3 — Modificações no backend (branch `v2`)

**Objetivo:** Substituir autenticação por senha por validação de JWT do Clerk. Mínimo de mudanças no restante do código.

### 3.1 — Novo endpoint: `POST /auth/clerk`

Substitui `POST /login`. Lógica:

```
1. Recebe { clerk_token: "<jwt>" } no body
2. Verifica JWT com a chave pública do Clerk (CLERK_PEM_PUBLIC_KEY no .env)
3. Extrai email e sub (clerk_id) do payload do token
4. SELECT * FROM users WHERE email = ?
5. Se não encontrado → 403 (aluno não cadastrado)
6. Se encontrado e clerk_id é NULL → UPDATE users SET clerk_id = ? WHERE email = ?
7. Se encontrado e clerk_id != sub → 403 (email pertence a outra conta Clerk)
8. session['user_id'] = user_id
9. Retorna { userId, name, email, curso, matricula }
```

### 3.2 — Remover endpoints legados

| Endpoint | Ação |
|---|---|
| `POST /login` | Remover |
| `POST /register` | Remover |
| `POST /logout` | Manter inalterado |

### 3.3 — Controle de novos registros via Clerk

O Clerk é a única porta de entrada para novos alunos. O controle é feito em duas camadas:

**Camada 1 — Clerk Dashboard (configuração):**

No Clerk Dashboard → **User & Authentication → Email, Phone, Username**:
- Desabilitar **"Allow users to sign up"**

Com isso, o componente `<SignIn>` não exibe o link "Sign up" e tentativas diretas de criar conta são bloqueadas pelo Clerk. Apenas o professor pode criar contas via Dashboard.

**Camada 2 — Backend SAv2 (defesa em profundidade):**

O `POST /auth/clerk` já rejeita qualquer email não presente no `admin.db` com `403`, independente de ter conta Clerk válida. Isso garante que mesmo se a configuração do Clerk for alterada por engano, nenhum aluno não cadastrado consegue acessar o sistema.

**Ciclo de turmas:**

| Momento | Ação no Clerk Dashboard |
|---|---|
| Início de novo ano letivo | Reabilitar "Allow users to sign up" temporariamente para a nova turma se cadastrar; ou criar as contas manualmente |
| Após onboarding da turma concluído | Desabilitar "Allow users to sign up" novamente |
| SAv2 em operação normal | Sign-up desabilitado; apenas logins de alunos já cadastrados |

> **Nota:** Para a próxima turma, além de reabilitar o sign-up no Clerk, será necessário popular o `admin.db` com os emails dos novos alunos antes de liberar o acesso — o backend continua como guardião final.

### 3.4 — Dependência Python

```
pip install PyJWT cryptography
```

Verificação do JWT do Clerk é feita com `PyJWT` usando a chave pública RS256 disponível no Clerk Dashboard.

### 3.5 — Variáveis de ambiente novas (`.env`)

```env
CLERK_PEM_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
```

Não é necessária a `CLERK_SECRET_KEY` para apenas verificar tokens JWT.

### 3.6 — Todos os outros endpoints: sem alteração

O decorator `@login_required` continua verificando `session['user_id']`. Nenhum outro endpoint precisa mudar.

---

## Fase 4 — Modificações no frontend (branch `v2`)

**Objetivo:** Integrar Clerk React SDK, substituindo as telas de login/registro.

### 4.1 — Instalar SDK

```bash
cd client && npm install @clerk/clerk-react
```

### 4.2 — `client/src/main.jsx`

Envolver a aplicação com `<ClerkProvider>`:

```jsx
import { ClerkProvider } from '@clerk/clerk-react';

<ClerkProvider publishableKey={import.meta.env.VITE_CLERK_PUBLISHABLE_KEY}>
  <App />
</ClerkProvider>
```

### 4.3 — Variável de ambiente

```env
# client/.env.production
VITE_CLERK_PUBLISHABLE_KEY=pk_live_...
```

### 4.4 — `client/src/api/axiosConfig.js`

Adicionar interceptor para injetar o JWT em todo request autenticado:

```js
// Antes de cada request, obter token fresco do Clerk e injetar no header
Authorization: Bearer <clerk_jwt>
```

O token expira a cada ~60s; o interceptor deve sempre chamar `getToken()` para obter um token válido.

### 4.5 — Substituir páginas de login/registro

- `LoginPage.jsx` → substituída por componente `<SignIn>` do Clerk
- `RegisterPage.jsx` → removida (registro controlado pelo professor via Clerk Dashboard)
- Após login bem-sucedido no Clerk, o frontend chama `POST /auth/clerk` com o token para criar a sessão Flask

---

## Fase 5 — Infraestrutura paralela no EC2

**Objetivo:** Subir SAv2 em portas alternativas sem interferir com produção, usando a mesma arquitetura de containers do SAv1.

### 5.1 — Arquitetura de containers (idêntica ao SAv1)

O SAv2 replica o padrão do SAv1: dois containers (`server` + `client`) orquestrados por Docker Compose, com bind-mount do diretório `./server` para persistir os bancos SQLite no host.

| Aspecto | SAv1 | SAv2 |
|---|---|---|
| Diretório no EC2 | `/opt/study-amigo/` | `/opt/studyamigo_v2/` |
| Compose file | `docker-compose.yml` | `docker-compose.yml` (no branch `v2`) |
| Container servidor | `flashcard_server` | `flashcard_server_v2` |
| Container cliente | `flashcard_client` | `flashcard_client_v2` |
| Porta pública | `80` | `8081` (temporário; vira `80` no cutover) |
| Bind-mount | `./server:/app` | `./server:/app` (igual) |

### 5.2 — Estrutura de diretórios no EC2

```
/opt/studyamigo_v2/
├── server/
│   ├── admin.db          ← novo schema (sem username/password_hash)
│   ├── user_dbs/         ← bancos com mesmos user_id de produção
│   ├── flask_session/
│   └── .env              ← SECRET_KEY + CLERK_PEM_PUBLIC_KEY
├── client/
└── docker-compose.yml    ← containers v2 (porta 8081)
```

### 5.3 — Terraform (`server_v2/aws_terraform/`)

Os scripts Terraform do SAv2 serão muito parecidos com os do SAv1 em `server/aws_terraform/`, com as seguintes diferenças:

| Arquivo | Diferença em relação ao SAv1 |
|---|---|
| `variables.tf` | `project_name` default `"study-amigo-v2"`; adiciona variável `clerk_pem_public_key` (sensitive) |
| `main.tf` | Idêntico ao SAv1 — mesma VPC, subnet, SG, AMI Ubuntu ARM64, EC2 `t4g.micro` |
| `user_data.sh` | Clona branch `v2`; escreve `CLERK_PEM_PUBLIC_KEY` no `.env`; porta do client mapeada para `80:80` desde o início (SAv2 é o sistema principal) |
| `terraform.tfvars.example` | Adiciona `clerk_pem_public_key = "..."` |

> **Nota:** Os arquivos `server_v2/aws_terraform/` **ainda não existem** — serão criados na Fase 5 com base nos originais de `server/aws_terraform/`, aplicando apenas as diferenças acima.

### 5.4 — Deploy paralelo (fase de testes, antes do cutover)

Durante a fase de testes, SAv2 coexiste com SAv1 no mesmo EC2:

```bash
# No EC2 — subir SAv2 na porta 8081 sem afetar SAv1 na porta 80
sudo mkdir /opt/studyamigo_v2
cd /opt/studyamigo_v2
sudo git clone <repo> .
sudo git checkout v2

# Copiar admin.db e user_dbs/ migrados (resultado da Fase 2)
# Preencher server/.env com SECRET_KEY e CLERK_PEM_PUBLIC_KEY

sudo docker compose up -d
```

### 5.5 — Deploy definitivo (pós-cutover via Terraform)

Após validação, o SAv2 pode ser provisionado em instância dedicada via Terraform:

```bash
cd server_v2/aws_terraform
cp terraform.tfvars.example terraform.tfvars
# Editar terraform.tfvars com chaves reais
terraform init
terraform apply
```

O `user_data.sh` faz o bootstrap completo: instala Docker, clona branch `v2`, configura `.env` e sobe os containers automaticamente.

---

## Fase 6 — Testes antes do cutover

### 6.1 — Smoke tests funcionais

- [ ] Login de 3 alunos reais via Clerk no SAv2 (porta 8081)
- [ ] Confirmar que cards aparecem corretamente (mesmos dados de produção)
- [ ] Fazer revisão completa e verificar que `revlog` foi gravado no banco correto
- [ ] Tentar login com email não cadastrado → deve receber 403
- [ ] Verificar que `clerk_id` foi preenchido no `admin.db` após primeiro login

### 6.2 — Validação de mapeamento

- [ ] Re-executar `validate_migration.py` no ambiente SAv2 do EC2
- [ ] Confirmar que não há `user_id` apontando para banco errado

### 6.3 — Teste de regressão backend

```bash
# Rodar suite de testes existente apontando para SAv2
python -m unittest server/test_api.py -v
```

---

## Fase 7 — Cutover

### 7.1 — Pré-cutover

1. Comunicar alunos: janela de manutenção (ex: domingo de madrugada)
2. Re-executar `migrate_user_dbs.py` para capturar reviews das últimas horas de produção
3. Re-executar `validate_migration.py` para confirmar consistência final

### 7.2 — Cutover

```bash
# No EC2: redirecionar Nginx porta 80 → SAv2 (porta 8081)
sudo nano /etc/nginx/sites-available/studyamigo
# Alterar proxy_pass de :8080 para :8081
sudo nginx -t && sudo systemctl reload nginx
```

### 7.3 — Pós-cutover

- Manter `/opt/study-amigo/` (SAv1) de pé por **2 semanas** em modo só-leitura
- Monitorar logs do `flashcard_server_v2` por 48h
- Após confirmação sem incidentes: `sudo docker compose -f /opt/study-amigo/docker-compose.yml down`

---

## Sequência e dependências

```
Fase 0  ──────────────────────────────────────┐
(email_mapping.csv)                           │
        │                                     │
        ├── Fase 1 (schema)                   │
        │       │                             │
        │       ├── Fase 2 (migrate_dbs) ◄───┘
        │       │
        │       ├── Fase 3 (backend v2)
        │       │
        │       └── Fase 4 (frontend v2)
        │               │
        │               └── Fase 5 (infra EC2)
        │                       │
        │                       └── Fase 6 (testes)
        │                               │
        └───────────────────────────────└── Fase 7 (cutover)
```

Fases 2, 3 e 4 podem correr em paralelo após Fase 1 concluída.

---

## Checklist de entregáveis por fase

| Fase | Entregável | Status |
|---|---|---|
| 0 | `server_v2/bases/email_mapping.csv` | pendente |
| 1 | `server_v2/scripts/create_v2_admin_db.py` | pendente |
| 1 | `server_v2/server/admin.db` (novo schema) | pendente |
| 2 | `server_v2/scripts/migrate_user_dbs.py` | pendente |
| 2 | `server_v2/scripts/validate_migration.py` | pendente |
| 2 | `server_v2/server/user_dbs/` populado | pendente |
| 3 | `server/app.py` com `POST /auth/clerk` | pendente |
| 3 | `server/requirements.txt` com `PyJWT` | pendente |
| 4 | `client` com `@clerk/clerk-react` integrado | pendente |
| 5 | `docker-compose.yml` no branch `v2` (containers `_v2`, porta `8081`) | pendente |
| 5 | `server_v2/aws_terraform/` (baseado em `server/aws_terraform/`) | pendente |
| 5 | SAv2 rodando em `:8081` no EC2 | pendente |
| 6 | Smoke tests passando | pendente |
| 7 | Nginx apontando para SAv2 | pendente |
| 7 | SAv1 desligado | pendente |
