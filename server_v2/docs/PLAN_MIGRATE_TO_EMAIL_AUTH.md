# Plano SAv1.5: Migração para Autenticação por Email + Troca de Senha

## Contexto

Alternativa mais simples ao plano Clerk (`PLAN_MIGRATE_TO_CLERK_AUTH.md`). Resolve os dois problemas imediatos sem dependências externas, sem nova infraestrutura e sem migração de bancos:

| Problema | Solução |
|---|---|
| Alunos com múltiplas contas | Login passa a ser por email único — impossível criar duas contas com o mesmo email |
| Aluno esquece senha e cria conta nova | Aba "Trocar Senha" permite auto-atendimento sem precisar do professor |

**Sem mudanças em:** infra, Docker, Terraform, bancos Anki, sessões Flask, endpoints de decks/cards/review.

---

## Fase 0 — Mapeamento email → user_id canônico

**Objetivo:** Construir `server_v2/bases/email_mapping_v1.5.csv` — o insumo que o script `add_email_to_admin_db.py` (Fase 1) usará para fazer os `UPDATE`. Sem esse arquivo, o script não tem como saber qual `user_id` de produção corresponde a cada email do CSV.

### 0.1 — Algoritmo de seleção de conta canônica

Para cada aluno com múltiplas contas em produção, a conta que "sobrevive" (recebe o email) é determinada por esta ordem de prioridade:

```
1. Maior número de revisões (revlog)     ← critério principal
2. Maior número de cards (notes)         ← desempate se revisões iguais
3. Maior user_id (conta mais recente)    ← desempate final
```

Contas descartadas (as demais do grupo) não recebem email e não são deletadas agora — ficam órfãs no `admin.db` até uma limpeza futura.

### 0.2 — Decisões aplicadas (dados de produção em 2026-04-08)

Resultado de `python server/tools/manage_users.py --list-dupes --production`:

| Aluno | user_id canônico | Motivo | Descartar |
|---|---|---|---|
| Ana Luiza Camilo da Silva | **62** | 348 rev vs 0 | 50 |
| Anthony Lucas Muniz Dos Santos | **92** | 400 rev vs 12/0/0 | 88, 114, 116 |
| Arthur Alves do Nascimento | **49** | 4 rev vs 0 | 32 |
| Bruno dos Santos Lima | **104** | 50 rev vs 14/6 | 40, 91 |
| João Ricardo Rocha de Carvalho | **47** | 112 rev vs 1 | 59 |
| Lucas da Silva Santos | **101** | 273 rev vs 0 | 60 |
| Mateus Da Silva Lima | **82** | 13 rev vs 0 | 115 |
| Matheus Dias Gomes | **71** | 132 rev vs 0/0 | 44, 69 |
| Victor Anderson Reis | **117** ⚠️ | 0 rev ambos; `117` tem mais cards (112 vs 109) | 43 |

> **⚠️ Victor Anderson Reis:** ambas as contas têm 0 revisões. Escolha do professor necessária antes de prosseguir. Sugestão: `117` (mais cards, mais recente).

### 0.3 — Formato do `email_mapping_v1.5.csv`

```
email,prod_user_id,nome,curso
anthonylucas2911@gmail.com,92,Anthony Lucas Muniz Dos Santos,SegCiber
analuiza101115@gmail.com,62,Ana Luiza Camilo da Silva,Metrologia
arthuralvesnas@gmail.com,49,Arthur Alves do Nascimento,Biotecnologia
bsantos1460@gmail.com,104,Bruno dos Santos Lima,SegCiber
joaoricardocarvalho4@gmail.com,47,João Ricardo Rocha de Carvalho,SegCiber
luqqs1p@gmail.com,101,Lucas da Silva Santos,SegCiber
mateuslimapatricio@gmail.com,82,Mateus Ferreira Patrício,SegCiber
marcosgomesdevasconcelos@gmail.com,71,Matheus Dias Gomes,Biotecnologia
reisbgk7@gmail.com,117,Victor Anderson Reid,Metrologia
...  (64 linhas no total, uma por aluno canônico)
```

Os alunos sem duplicatas têm seu `prod_user_id` identificado cruzando `Nome` do CSV com `name` do `admin.db` de produção — processo manual ou semi-automatizado.

### 0.4 — Construção do mapeamento completo

Para os alunos **sem duplicatas** (a maioria), o cruzamento `nome_csv → user_id` pode ser feito assim:

```bash
# Baixar cache local do admin.db de produção
python server/tools/manage_users.py --list-dupes --production > /tmp/prod_users.txt

# Ou consultar diretamente:
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  "sudo docker exec flashcard_server python3 -c \"
import sqlite3, json
conn = sqlite3.connect('/app/admin.db')
rows = conn.execute('SELECT user_id, username, name FROM users ORDER BY name').fetchall()
print(json.dumps([dict(zip([\'user_id\',\'username\',\'name\'], r)) for r in rows]))
\""
```

Com a lista de todos os usuários e o CSV em mãos, preencher `email_mapping_v1.5.csv` manualmente (ou com um script auxiliar de matching por nome).

**Entregável:** `server_v2/bases/email_mapping_v1.5.csv` revisado e aprovado pelo professor antes de prosseguir para a Fase 1.

---

## Estado atual relevante

### Backend (`server/app.py`)

```python
# admin.db — schema atual
CREATE TABLE users (
    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    name          TEXT NOT NULL,
    password_hash TEXT NOT NULL
    -- sem coluna email
)

# POST /login — autentica por username
SELECT * FROM users WHERE username = ?

# POST /register — cria conta com username + name + password
# (email existe no RegisterForm do frontend mas NÃO é salvo no backend)
```

### Frontend (`client/src/`)

| Arquivo | Estado atual |
|---|---|
| `components/LoginForm.jsx` | Campo `username` + `password`; chama `POST /login` |
| `components/RegisterForm.jsx` | Campos `username`, `name`, `email`, `groupCode`, `password`, `confirmPassword`; chama `POST /register` — mas `email` não é persistido no backend |
| `pages/AuthPage.jsx` | Duas abas: "Login" e "Cadastro" |
| `components/Header.jsx` | Exibe `user.name \|\| user.username` no topo |

---

## Escopo das mudanças

### Backend — 5 alterações em `server/app.py`

1. **Migração de schema** — adicionar coluna `email`
2. **`POST /login`** — trocar `WHERE username=?` por `WHERE email=?`
3. **`POST /register`** — salvar `email`; validar formato + MX record; manter `username` como alias gerado automaticamente
4. **`POST /change-password`** — endpoint novo
5. **`requirements.txt`** — adicionar `dnspython`

### Frontend — 4 alterações em `client/src/`

1. **`LoginForm.jsx`** — campo `username` vira `email`
2. **`AuthPage.jsx`** — aba "Cadastro" desabilitada (greyed out); adicionar aba "Trocar Senha"
3. **`ChangePasswordForm.jsx`** — componente novo (3 campos)
4. **Chaves i18n** — adicionar traduções para novos textos

### Script de migração — 1 script

1. **`server_v2/scripts/add_email_to_admin_db.py`** — popula `email` no `admin.db` de produção a partir do CSV

---

## Validação de email no registro

A validação é feita em duas camadas complementares, sem envio de email e sem dependências pesadas.

### Camada 1 — Regex no frontend (já existe)

`RegisterForm.jsx` já possui:

```js
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
```

Rejeita entradas claramente inválidas (`foo`, `foo@`, `@bar.com`) imediatamente no browser, antes de qualquer chamada ao backend. **Já implementado — nenhuma mudança necessária.**

### Camada 2 — MX record check no backend (a implementar)

Verifica se o **domínio do email tem servidor de email configurado**, consultando o DNS. Não envia nada — é uma consulta de leitura pura. Custo: ~100ms de latência apenas no momento do registro.

```python
# requirements.txt: adicionar dnspython
import dns.resolver

def domain_has_mx(email: str) -> bool:
    domain = email.split('@')[1]
    try:
        dns.resolver.resolve(domain, 'MX')
        return True
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout):
        return False
```

Chamada em `POST /register`:
```python
if not domain_has_mx(email):
    return jsonify({"error": "Domínio de email inválido ou inexistente"}), 400
```

**Exemplos do que isso rejeita:**
- `joao@dominiofalso123xyz.com` → domínio não existe (NXDOMAIN)
- `joao@localhost` → sem MX record
- `joao@gmail.con` (typo) → domínio não existe

**Exemplos do que isso aceita corretamente:**
- `joao@gmail.com` ✓
- `joao@hotmail.com` ✓
- `joao@icloud.com` ✓ (Maria Clara do CSV usa `@icloud.com`)

### Por que não usar confirmação por email?

Enviar um link de confirmação garante 100% que o aluno tem acesso ao email, mas exige: configuração de SMTP, lógica de token com expiração, e página de confirmação. Para uma turma pequena onde o professor conhece todos os alunos, o custo operacional não se justifica. A combinação regex + MX cobre 99% dos erros de digitação.

### Dependência nova

```
# server/requirements.txt
dnspython>=2.4.0
```

Leve (~500KB), sem side effects, amplamente usada.

---

## Fase 1 — Migração do schema `admin.db`

### 1.1 — Alteração de schema

```sql
ALTER TABLE users ADD COLUMN email TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);
```

A coluna começa nullable para permitir a migração gradual. Após popular todos os emails via script, pode-se adicionar `NOT NULL` se desejado.

### 1.2 — Script: `server_v2/scripts/add_email_to_admin_db.py`

Lê `server_v2/bases/email_mapping_v1.5.csv` e opera em **duas passagens**:

**Passagem 1 — validação MX de todos os emails** (nenhum `UPDATE` executado):
1. Para cada linha do CSV, extrai o domínio do email
2. Consulta MX record via DNS (com cache por domínio — ver abaixo)
3. Acumula lista de falhas

**Passagem 2 — inserção** (só ocorre se zero domínios falharam):
1. Busca no `admin.db` o `user_id` correspondente pelo `prod_user_id` do CSV
2. Faz `UPDATE users SET email = ? WHERE user_id = ?`
3. Reporta: emails preenchidos, alunos não encontrados

Se qualquer domínio falhar na Passagem 1, o script **aborta sem tocar no banco**, imprime o relatório de falhas e solicita correção do CSV.

**Requer:** `server_v2/bases/email_mapping_v1.5.csv` da Fase 0 (mapeamento `email → prod_user_id`).

#### Validação MX com cache de domínio

Para evitar consultas DNS redundantes, o script mantém um dicionário de domínios já consultados. Se `joe@gmail.com` já foi validado, `mary@gmail.com` pula a consulta DNS e reaproveita o resultado em cache.

```python
import dns.resolver

mx_cache: dict[str, bool] = {}  # { "gmail.com": True, "dominiofalso.com": False }

def domain_has_mx_cached(email: str) -> bool:
    domain = email.split('@')[1].lower()
    if domain in mx_cache:
        return mx_cache[domain]  # cache hit — sem nova consulta DNS
    try:
        dns.resolver.resolve(domain, 'MX')
        mx_cache[domain] = True
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout):
        mx_cache[domain] = False
    return mx_cache[domain]
```

#### Relatório da Passagem 1 (sempre impresso)

```
=== Relatório de validação MX ===
Domínios únicos consultados: 7
  gmail.com        OK
  hotmail.com      OK
  icloud.com       OK
  outlook.com      OK
  ufrj.br          OK
  cefet-rj.edu.br  OK
  dominiofalso.xyz OK
```

Se houver falhas:

```
⚠️  DOMÍNIOS COM FALHA NO MX:
  ──────────────────────────────────────────────────
  dominioerrado.com  →  aluno: João da Silva  (user_id 42)
  typo.comm          →  aluno: Ana Souza      (user_id 17)
  ──────────────────────────────────────────────────
  Total com falha: 2

❌ Nenhum email foi inserido. Corrija os emails acima no CSV e execute novamente.
```

Se todos os domínios passarem:

```
✅ Todos os 7 domínios validados. Inserindo 64 emails no banco...
✅ Concluído.
```

**Motivo do design all-or-nothing**: garante que o professor possa corrigir o CSV e reexecutar com confiança — o banco nunca fica em estado parcialmente migrado.

**Execução (local, contra cache):**
```bash
python server_v2/scripts/add_email_to_admin_db.py \
  --csv server_v2/bases/curated_student_roster_v2.csv \
  --db ~/.cache/studyamigo/YYYYMMDD/admin.db \
  --dry-run   # ver o que seria alterado sem executar
```

**Execução (produção):**
```bash
python server_v2/scripts/add_email_to_admin_db.py \
  --csv server_v2/bases/curated_student_roster_v2.csv \
  --production \
  --prod-host 54.152.109.26 \
  --prod-key ~/.ssh/study-amigo-aws
```

---

## Fase 2 — Backend: modificações em `server/app.py`

### 2.1 — `POST /login`: trocar username por email

**Antes:**
```python
username = data['username']
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
```

**Depois:**
```python
email = data['email'].strip().lower()
cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
```

Manter `session['username']` para compatibilidade com logs existentes — usar `user['username']` que continua no banco.

### 2.2 — `POST /register`: salvar email, gerar username automaticamente

O campo `username` deixa de ser preenchido pelo aluno. O backend gera um username interno automaticamente (ex: primeiros 8 chars do email antes do `@`), apenas para manter o campo preenchido no schema legado.

```python
email = data['email'].strip().lower()
# Validar unicidade de email
cursor.execute("SELECT user_id FROM users WHERE email = ?", (email,))
if cursor.fetchone():
    return jsonify({"error": "Email já cadastrado"}), 409

# Gerar username interno (não exposto ao usuário)
username = email.split('@')[0][:10]
# Garantir unicidade do username gerado
# (adicionar sufixo numérico se necessário)
```

> **Nota:** `POST /register` permanece funcional mas a aba de Cadastro fica desabilitada no frontend para a turma atual. Reabilitar no próximo ano letivo.

### 2.3 — `POST /change-password`: endpoint novo

```
Rota:    POST /change-password
Auth:    @login_required (usuário deve estar logado)
Body:    { current_password, new_password, confirm_password }

Lógica:
1. Buscar user_id da sessão
2. SELECT password_hash FROM users WHERE user_id = ?
3. bcrypt.checkpw(current_password) → se falhar: 401
4. Validar new_password (10–20 chars)
5. Validar new_password == confirm_password
6. new_hash = bcrypt.hashpw(new_password)
7. UPDATE users SET password_hash = ? WHERE user_id = ?
8. Retornar 200 { message: "Senha alterada com sucesso" }
```

Nenhuma dependência nova — `bcrypt` já está em `requirements.txt`.

---

## Fase 3 — Frontend: modificações em `client/src/`

### 3.1 — `LoginForm.jsx`

Única mudança: campo `username` vira `email`.

```jsx
// Antes
const [username, setUsername] = useState('');
<input type="text" ... value={username} onChange={...} />
await api.post('/login', { username, password });

// Depois
const [email, setEmail] = useState('');
<input type="email" ... value={email} onChange={...} />
await api.post('/login', { email, password });
```

### 3.2 — `ChangePasswordForm.jsx` (componente novo)

Três campos: `currentPassword`, `newPassword`, `confirmPassword`.
Chama `POST /change-password`. Exibe mensagem de sucesso inline (sem redirecionar).

```jsx
// Estrutura
<form onSubmit={handleSubmit}>
  <input type="password" name="currentPassword" ... />
  <input type="password" name="newPassword" ... />     // min 10, max 20
  <input type="password" name="confirmPassword" ... />
  <button type="submit">Trocar Senha</button>
</form>
```

### 3.3 — `AuthPage.jsx`: 3 abas, Cadastro desabilitado

**Antes:** 2 abas — "Login" | "Cadastro"

**Depois:** 3 abas — "Login" | ~~"Cadastro"~~ (desabilitada) | "Trocar Senha"

```jsx
// Aba Cadastro — greyed out, não clicável
<button
  style={{ ...inactiveTabStyles, opacity: 0.4, cursor: 'not-allowed' }}
  disabled
  title="Novos cadastros estão temporariamente desativados"
>
  {t('auth.register')}
</button>

// Aba Trocar Senha
<button
  style={activeTab === 'change-password' ? activeTabStyles : inactiveTabStyles}
  onClick={() => setActiveTab('change-password')}
>
  {t('auth.changePassword')}
</button>

// Renderização condicional
{activeTab === 'login' && <LoginForm ... />}
{activeTab === 'change-password' && <ChangePasswordForm />}
```

> **Nota:** A aba "Trocar Senha" aparece mesmo antes do login. O endpoint `POST /change-password` usa `@login_required` — se o aluno não estiver logado, recebe 401 e o formulário exibe "Faça login primeiro para trocar a senha".

### 3.4 — Chaves i18n

Adicionar nos arquivos de tradução (`client/src/i18n/`):

```json
{
  "auth": {
    "changePassword": "Trocar Senha",
    "currentPassword": "Senha atual",
    "newPassword": "Nova senha",
    "confirmNewPassword": "Confirmar nova senha",
    "changePasswordButton": "Alterar senha",
    "changePasswordSuccess": "Senha alterada com sucesso!",
    "errors": {
      "wrongCurrentPassword": "Senha atual incorreta",
      "registerDisabled": "Novos cadastros estão temporariamente desativados"
    }
  }
}
```

---

## Fase 4 — Servidor paralelo no EC2

Mesmo que o SAv1.5 seja uma mudança cirúrgica sobre SAv1, a estratégia adotada é subir um **servidor paralelo** antes de cortar o tráfego de produção. Isso permite validar com alunos reais sem risco.

### 4.1 — Estrutura no EC2

```
/opt/studyamigo_v1.5/       ← clone do branch v1.5
├── server/
│   ├── admin.db             ← cópia do admin.db de produção + coluna email populada
│   ├── user_dbs/            ← symlink ou cópia dos bancos existentes (mesmos user_id)
│   ├── flask_session/
│   └── .env
├── client/
└── docker-compose.yml       ← containers _v1.5, porta 8082
```

### 4.2 — Docker Compose paralelo

| Serviço | Container | Porta host |
|---|---|---|
| `server` | `flashcard_server_v1.5` | interno `:8000` |
| `client` | `flashcard_client_v1.5` | `:8082` |

### 4.3 — Deploy do servidor paralelo

```bash
# No EC2
sudo mkdir /opt/studyamigo_v1.5
cd /opt/studyamigo_v1.5
sudo git clone <repo> .
sudo git checkout v1.5

# Copiar admin.db com email já populado (resultado da Fase 1)
sudo cp /opt/study-amigo/server/admin.db server/admin.db
# Copiar bancos Anki (mesmos user_id — cópia simples)
sudo cp -r /opt/study-amigo/server/user_dbs/ server/user_dbs/
# Copiar .env
sudo cp /opt/study-amigo/server/.env server/.env

sudo docker compose up -d
```

### 4.4 — Cutover (após validação)

```bash
# Nginx aponta porta 80 → v1.5 (porta 8082)
sudo nano /etc/nginx/sites-available/studyamigo
# Alterar proxy_pass de :8080 para :8082
sudo nginx -t && sudo systemctl reload nginx
```

SAv1 original fica de pé em modo só-leitura por 1 semana antes de ser desligado.

---

## Fase 5 — Testes do servidor paralelo

### 5.1 — Estado atual dos testes

| Script | Localização | Cobre | Status para SAv1.5 |
|---|---|---|---|
| `test_api.py` | `server/tools/` | Register, login, decks, cards, review, logout | **Desatualizado** — usa `username` no login; precisa de update |
| `test_frontend_flow.py` | `server/test_race_condition/` | Fluxo completo login→deck→card sob concorrência | **Desatualizado** — usa `username`; IP hardcoded |
| `test_session_race.py` | `server/test_race_condition/` | Colisão de sessões com múltiplos usuários | Compatível, mas IP hardcoded |
| `test_supermemo_2.py` | `server/test_supermemo_2/` | Algoritmo SM-2 | Inalterado — compatível |
| `validate_migration.py` | `server/tools/` | Integridade do `admin.db` pós-migração de usuários | Não cobre SAv1.5 |

### 5.2 — Gaps identificados

**Gap 1 — `test_api.py` usa `username` no login**

Os helpers `_register_user()` e `_login_user()` passam `username`. Após a mudança para email, esses testes quebram. Precisam ser atualizados para passar `email`.

**Gap 2 — Nenhum teste cobre `POST /change-password`**

Endpoint novo, sem cobertura. Casos necessários:
- Senha atual correta → 200
- Senha atual errada → 401
- Nova senha muito curta (< 10 chars) → 400
- Nova senha == senha atual → opcional, pode ser permitido
- Sem sessão ativa → 401

**Gap 3 — IP hardcoded nos testes de race condition**

`test_frontend_flow.py` e `test_session_race.py` têm `BASE_URL = "http://54.226.152.231"` hardcoded. Para apontar ao servidor paralelo SAv1.5 em `:8082`, precisam aceitar `--url` como argumento.

### 5.3 — Scripts a criar

| Script | Localização | Descrição |
|---|---|---|
| `test_api_v1.5.py` | `server_v2/scripts/` | `test_api.py` atualizado para email + testes de `POST /change-password` |
| `smoke_test.py` | `server_v2/scripts/` | Smoke test HTTP parametrizável com `--url`; roda contra qualquer servidor (paralelo ou produção) |

### 5.4 — Execução dos testes contra o servidor paralelo

```bash
# Smoke test contra servidor paralelo (porta 8082)
python server_v2/scripts/smoke_test.py --url http://54.152.109.26:8082

# Suite completa de API (in-process, aponta para branch v1.5)
cd server && python -m unittest server_v2/scripts/test_api_v1.5.py -v

# Teste de race condition contra servidor paralelo
python server/test_race_condition/test_frontend_flow.py --url http://54.152.109.26:8082
```

### 5.5 — Checklist de validação pré-cutover

- [ ] Login com email funciona para 2-3 alunos reais no servidor paralelo (porta 8082)
- [ ] Login com username antigo retorna erro claro (não "senha errada")
- [ ] Aba "Cadastro" aparece desabilitada e não clicável
- [ ] Troca de senha com senha atual correta → sucesso
- [ ] Troca de senha com senha atual errada → erro 401
- [ ] Novo login com senha trocada funciona
- [ ] Aluno sem sessão tenta trocar senha → mensagem "faça login primeiro"
- [ ] Cards de aluno real aparecem corretamente (dados migrados de produção)
- [ ] Revisão completa gravada no `revlog` do banco correto
- [ ] `smoke_test.py` passa 100% contra porta 8082
- [ ] Emails duplicados no CSV foram resolvidos antes do deploy

---

## Fase 6 — Deploy em produção

```bash
# 1. Commit e push do branch v1.5
git add server/app.py client/src/components/LoginForm.jsx \
        client/src/components/ChangePasswordForm.jsx \
        client/src/pages/AuthPage.jsx
git commit -m "feat: auth por email + troca de senha"
git push origin v1.5

# 2. Aplicar migração de schema em produção
python server_v2/scripts/add_email_to_admin_db.py \
  --csv server_v2/bases/curated_student_roster_v2.csv \
  --production ...

# 3. Restart servidor (bind-mount, sem rebuild)
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  "cd /opt/study-amigo && sudo git pull origin v1.5 && \
   sudo docker compose restart server"

# 4. Rebuild cliente (mudança de frontend requer novo build)
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  "cd /opt/study-amigo && sudo docker compose up -d --build client"
```

```bash
# 1. Commit e push
git add server/app.py client/src/components/LoginForm.jsx \
        client/src/components/ChangePasswordForm.jsx \
        client/src/pages/AuthPage.jsx
git commit -m "feat: auth por email + troca de senha"
git push origin main

# 2. Aplicar migração de schema em produção
python server_v2/scripts/add_email_to_admin_db.py \
  --csv server_v2/bases/curated_student_roster_v2.csv \
  --production ...

# 3. Restart servidor (bind-mount, sem rebuild)
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  "cd /opt/study-amigo && sudo git pull origin main && \
   sudo docker compose restart server"

# 4. Rebuild cliente (mudança de frontend requer novo build)
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  "cd /opt/study-amigo && sudo docker compose up -d --build client"
```

---

## Sequência resumida

```
Fase 0: Mapeamento email → user_id (email_mapping_v1.5.csv) — aprovação do professor
    ↓
Fase 1: Schema (add_email_to_admin_db.py usa o CSV da Fase 0)
    ↓
Fase 2: Backend (app.py) — mudanças + testes unitários
    ↓ paralelo com Fase 2
Fase 3: Frontend (LoginForm, ChangePasswordForm, AuthPage, i18n)
    ↓
Fase 4: Servidor paralelo no EC2 (porta 8082)
    ↓
Fase 5: Testes contra servidor paralelo (smoke_test.py + test_api_v1.5.py)
    ↓
Fase 6: Cutover (Nginx → porta 8082 → produção)
```

---

## Checklist de entregáveis

| Fase | Entregável | Arquivo | Status |
|---|---|---|---|
| 0 | Decisão sobre Victor Anderson Reis | professor | pendente |
| 0 | Mapeamento email → user_id | `server_v2/bases/email_mapping_v1.5.csv` | pendente |
| 1 | Script de migração de email | `server_v2/scripts/add_email_to_admin_db.py` | pendente |
| 1 | Schema migrado em produção | `admin.db` com coluna `email` populada | pendente |
| 2 | Login por email | `server/app.py` — `POST /login` | pendente |
| 2 | Registro salva email + valida MX | `server/app.py` — `POST /register` | pendente |
| 2 | Dependência MX check | `server/requirements.txt` — `dnspython` | pendente |
| 2 | Troca de senha | `server/app.py` — `POST /change-password` | pendente |
| 3 | Campo email no login | `client/src/components/LoginForm.jsx` | pendente |
| 3 | Formulário troca de senha | `client/src/components/ChangePasswordForm.jsx` | pendente |
| 3 | 3 abas (Cadastro greyed out) | `client/src/pages/AuthPage.jsx` | pendente |
| 3 | Chaves i18n novas | `client/src/i18n/*.json` | pendente |
| 4 | Servidor paralelo rodando em `:8082` | EC2 `/opt/studyamigo_v1.5/` | pendente |
| 5 | Suite de testes atualizada para email | `server_v2/scripts/test_api_v1.5.py` | pendente |
| 5 | Smoke test parametrizável | `server_v2/scripts/smoke_test.py` | pendente |
| 5 | Todos os testes passando contra `:8082` | — | pendente |
| 6 | Cutover Nginx → produção | EC2 | pendente |

---

## Comparação com plano Clerk

| Aspecto | Este plano (SAv1.5) | PLAN_MIGRATE_TO_CLERK_AUTH.md (SAv2) |
|---|---|---|
| Dependências novas | Nenhuma | Clerk SDK, PyJWT |
| Infra nova | Não | Nova instância EC2, Terraform v2 |
| Migração de bancos Anki | Não | Sim (migrate_user_dbs.py) |
| Resolve esquecimento de senha | Parcialmente (auto-atendimento) | Totalmente (sem senha) |
| Tempo de implementação | 2–3 dias | 3–4 semanas |
| Risco | Mínimo | Médio |
| Recomendação | **Agora, para a turma atual** | Próximo ano letivo, nova turma |
