# manage_users.py — Guia Rápido

Ferramenta administrativa para gerenciar contas duplicadas e resetar senhas.
Todos os comandos abaixo são executados a partir do diretório raiz do projeto.

---

## Configuração via arquivo .env

O script carrega automaticamente `server/tools/manage_users.env` se existir.
Isso elimina a necessidade de passar todos os parâmetros na linha de comando.

### Primeiro uso

```bash
cp server/tools/manage_users.env.example server/tools/manage_users.env
# edite manage_users.env conforme necessário
```

O arquivo `manage_users.env` está no `.gitignore` e **não deve ser commitado**.
Apenas `manage_users.env.example` vai para o repositório.

### Conteúdo do manage_users.env

```ini
# Banco local (backup)
LOCAL_DB=~/.cache/studyamigo/20260330/admin.db
LOCAL_USERDB=~/.cache/studyamigo/20260330/user_dbs/
LOCAL_SESSION=server/flask_session/

# Produção (EC2)
PROD_HOST=54.152.109.26
PROD_USER=ubuntu
PROD_KEY=~/.ssh/study-amigo-aws
PROD_DB=/opt/study-amigo/server/admin.db
PROD_USERDB=/opt/study-amigo/server/user_dbs/
PROD_SESSION=/opt/study-amigo/server/flask_session/
```

Argumentos CLI sempre sobrescrevem os valores do `.env`.
Para usar um arquivo alternativo: `--env-file /caminho/outro.env`

---

## 1. Listar duplicatas

```bash
# Todos os alunos com mais de uma conta no sistema
python server/tools/manage_users.py --list-dupes

# Filtrar por nome de um aluno específico
python server/tools/manage_users.py --list-dupes "Rogério"
```

A saída mostra user_id, username, número de cartões e revisões de cada conta.
Use essas informações para identificar qual conta manter (geralmente a com mais revisões).

---

## 2. Deletar contas duplicadas

### Passo 1 — Gerar o SQL (dry-run, não executa nada)

```bash
python server/tools/manage_users.py --dry-run --delete-users 53,66,70,73,87
```

Gera: `migration_delete_YYYYMMDD.sql`

### Passo 2 — Revisar o SQL gerado

```bash
cat migration_delete_YYYYMMDD.sql
```

Confirme que os IDs listados são os corretos e que a conta a manter **não** está incluída.

### Passo 3 — Validar sobre o backup local

```bash
python server/tools/manage_users.py \
    --apply-to-local-cache --sql migration_delete_YYYYMMDD.sql
```

Verifique que apenas a conta correta permanece:

```bash
python server/tools/manage_users.py --list-dupes "Rogério"
```

### Passo 4 — Commitar o SQL para rastreabilidade

```bash
git add server/tools/migration_delete_YYYYMMDD.sql
git commit -m "admin: delete duplicate accounts for <nome do aluno>"
git push origin main
```

### Passo 5 — Aplicar em produção

```bash
python server/tools/manage_users.py \
    --apply-to-production --sql migration_delete_YYYYMMDD.sql
```

Se houver sessão ativa de alguma conta afetada, um **aviso** será exibido e
será solicitada confirmação antes de prosseguir.

---

## 3. Trocar a senha de um usuário

### Passo 1 — Gerar o SQL com o novo hash (dry-run, interativo)

```bash
python server/tools/manage_users.py --dry-run --reset-password 107
```

O script solicitará a nova senha duas vezes (sem eco no terminal).
Requisitos: mínimo 10 caracteres, máximo 20.

Gera: `migration_reset_pw_YYYYMMDD.sql`

### Passo 2 — Revisar o SQL gerado

```bash
cat migration_reset_pw_YYYYMMDD.sql
```

Confirme que o `user_id` no UPDATE corresponde ao aluno correto.

### Passo 3 — Commitar o SQL para rastreabilidade

```bash
git add server/tools/migration_reset_pw_YYYYMMDD.sql
git commit -m "admin: reset password for user_id=107 (<nome do aluno>)"
git push origin main
```

### Passo 4 — Aplicar em produção

```bash
python server/tools/manage_users.py \
    --apply-to-production --sql migration_reset_pw_YYYYMMDD.sql
```

---

## 4. Fluxo completo — exemplo do Rogério

```bash
# 1. Confirmar contas
python server/tools/manage_users.py --list-dupes "Rogério"

# 2. Gerar SQL de deleção das contas inúteis (manter user_id=107)
python server/tools/manage_users.py --dry-run --delete-users 53,66,70,73,87

# 3. Gerar SQL de reset de senha para a conta correta
python server/tools/manage_users.py --dry-run --reset-password 107

# 4. Revisar e commitar ambos os SQLs
git add server/tools/migration_*.sql
git commit -m "admin: clean up duplicate accounts and reset password for Rogério"
git push origin main

# 5. Aplicar deleção em produção
python server/tools/manage_users.py \
    --apply-to-production --sql migration_delete_YYYYMMDD.sql

# 6. Aplicar reset de senha em produção
python server/tools/manage_users.py \
    --apply-to-production --sql migration_reset_pw_YYYYMMDD.sql

# 7. Confirmar resultado final
python server/tools/manage_users.py --list-dupes "Rogério"
```

---

## Avisos importantes

- **Nunca** inclua na lista de deleção a conta que o aluno usa (a com mais revisões).
- O `--apply-to-local-cache` altera o **backup local** — não afeta produção.
- O `--apply-to-production` é **irreversível**. Sempre valide no cache local primeiro.
- Os arquivos `.sql` gerados ficam no diretório de onde o script é chamado. Mova-os para `server/tools/` antes de commitar.
- `manage_users.env` nunca deve ser commitado (contém caminho da chave SSH).
