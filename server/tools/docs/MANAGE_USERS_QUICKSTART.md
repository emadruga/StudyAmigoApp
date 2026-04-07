# manage_users.py — Guia Rápido

Ferramenta administrativa para gerenciar contas duplicadas e resetar senhas.
Todos os comandos abaixo são executados a partir do diretório raiz do projeto.

Scripts envolvidos:
- `server/tools/manage_users.py` — operações de deleção e reset de senha
- `server/tools/validate_migration.py` — validação pós-apply
- `server/tools/restore_backup.py` — restauração de emergência via S3

---

## Sumário

- [0. Configuração via arquivo .env](#0-configuração-via-arquivo-env)
- [1. Listar duplicatas](#1-listar-duplicatas)
- [2. Deletar contas duplicadas](#2-deletar-contas-duplicadas)
  - [Passo 1 — Gerar o SQL](#passo-1--gerar-o-sql-dry-run-não-executa-nada)
  - [Passo 2 — Revisar o SQL gerado](#passo-2--revisar-o-sql-gerado)
  - [Passo 3 — Validar sobre o backup local](#passo-3--validar-sobre-o-backup-local)
  - [Passo 4 — Commitar para rastreabilidade](#passo-4--commitar-o-sql-para-rastreabilidade)
  - [Passo 5 — Aplicar em produção](#passo-5--aplicar-em-produção)
  - [Passo 6 — Validar em produção](#passo-6--validar-em-produção)
- [3. Trocar a senha de um usuário](#3-trocar-a-senha-de-um-usuário)
  - [Passo 1 — Gerar o SQL](#passo-1--gerar-o-sql-com-o-novo-hash-dry-run-interativo)
  - [Passo 2 — Revisar o SQL gerado](#passo-2--revisar-o-sql-gerado-1)
  - [Passo 3 — Commitar para rastreabilidade](#passo-3--commitar-o-sql-para-rastreabilidade)
  - [Passo 4 — Aplicar em produção](#passo-4--aplicar-em-produção)
  - [Passo 5 — Validar em produção](#passo-5--validar-em-produção)
- [4. Fluxo completo — exemplo do Rogério](#4-fluxo-completo--exemplo-do-rogério)
- [5. Restauração de emergência](#5-restauração-de-emergência-algo-deu-errado)
- [Avisos importantes](#avisos-importantes)

---

## 0. Configuração via arquivo .env

O script carrega automaticamente `server/tools/manage_users.env` se existir,
eliminando a necessidade de passar todos os parâmetros na linha de comando.

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
Para usar um arquivo alternativo: `--conf /caminho/outro.env` (ou `-f`)

---

## 1. Listar duplicatas

```bash
# Todos os alunos com mais de uma conta (banco local/cache)
python server/tools/manage_users.py --list-dupes

# Filtrar por nome de um aluno específico (banco local/cache)
python server/tools/manage_users.py --list-dupes "Rogério"

# Confirmar resultado diretamente em PRODUÇÃO
python server/tools/manage_users.py --list-dupes --production
python server/tools/manage_users.py --list-dupes "Rogério" --production
```

A saída mostra user_id, username, número de cartões e revisões de cada conta.
Use essas informações para identificar qual conta manter (geralmente a com mais revisões).
Use `--production` para consultar o servidor EC2 diretamente (útil após aplicar uma migração).

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

### Passo 6 — Validar em produção

```bash
python server/tools/validate_migration.py \
    --validate-production --sql migration_delete_YYYYMMDD.sql
```

Saída esperada para cada conta deletada: `OK  user_id=N não existe no banco`
Saída esperada para cada arquivo removido: `OK  /opt/.../user_N.db removido`
Resultado final: `RESULTADO: TUDO OK`

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

### Passo 5 — Validar em produção

```bash
python server/tools/validate_migration.py \
    --validate-production --sql migration_reset_pw_YYYYMMDD.sql
```

Saída esperada: `OK  user_id=107 (username) tem hash bcrypt válido`

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

# 6. Validar deleção em produção
python server/tools/validate_migration.py \
    --validate-production --sql migration_delete_YYYYMMDD.sql

# 7. Aplicar reset de senha em produção
python server/tools/manage_users.py \
    --apply-to-production --sql migration_reset_pw_YYYYMMDD.sql

# 8. Validar reset de senha em produção
python server/tools/validate_migration.py \
    --validate-production --sql migration_reset_pw_YYYYMMDD.sql

# 9. Confirmar resultado final diretamente em produção
python server/tools/manage_users.py --list-dupes "Rogério" --production
```

---

## 5. Restauração de emergência (algo deu errado)

Use este procedimento se a validação falhar ou se uma migração incorreta foi aplicada.

> **Atenção:** a restauração desfaz **tudo** que ocorreu no banco desde as 03:00 (hora do backup).
> Novos cadastros feitos após as 03:00 serão perdidos. Avalie antes de prosseguir.

### Passo 1 — Verificar os backups disponíveis

```bash
python3 server/tools/verify_backups.py \
    --bucket study-amigo-backups-645069181643 \
    --profile study-amigo
```

Identifique o slot marcado com `►` (backup de hoje às 03:00).
Cheque se o status está `OK` e não `PARTIAL` ou `CORRUPT`.

### Passo 2 — Restaurar o último backup (da sua máquina)

```bash
python3 server/tools/restore_backup.py \
    --bucket study-amigo-backups-645069181643 \
    --profile study-amigo \
    --remote \
    --host 54.152.109.26 \
    --ssh-key ~/.ssh/study-amigo-aws \
    --latest
```

O script vai:
1. Baixar o backup do S3 para `/tmp/` local
2. Enviar ao EC2 via SCP
3. Salvar snapshot de segurança em `/tmp/studyamigo-pre-restore/` no EC2
4. Parar o container `flashcard_server`
5. Restaurar `admin.db` e `user_dbs/`
6. Reiniciar o container
7. Pedir confirmação `yes` antes de executar qualquer coisa

### Passo 3 — Verificar que o servidor voltou ao normal

```bash
# Container rodando?
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  "sudo docker compose -f /opt/study-amigo/docker-compose.yml ps"

# Banco restaurado corretamente?
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  "sqlite3 /opt/study-amigo/server/admin.db \
   \"SELECT COUNT(*) FROM users;\""
```

### Passo 4 — Se precisar de um backup de um dia específico

```bash
# Listar todos os slots disponíveis
python3 server/tools/restore_backup.py \
    --bucket study-amigo-backups-645069181643 \
    --profile study-amigo \
    --list

# Restaurar slot específico (ex: semana 2, quinta-feira)
python3 server/tools/restore_backup.py \
    --bucket study-amigo-backups-645069181643 \
    --profile study-amigo \
    --remote \
    --host 54.152.109.26 \
    --ssh-key ~/.ssh/study-amigo-aws \
    --week 2 --day thursday
```

---

## Avisos importantes

- **Nunca** inclua na lista de deleção a conta que o aluno usa (a com mais revisões).
- O `--apply-to-local-cache` altera o **backup local** — não afeta produção.
- O `--apply-to-production` é **irreversível** sem restauração de backup. Sempre valide no cache local primeiro.
- Os arquivos `.sql` gerados ficam no diretório de onde o script é chamado. Mova-os para `server/tools/` antes de commitar.
- `manage_users.env` nunca deve ser commitado (contém caminho da chave SSH).
- O backup S3 roda diariamente às **03:00 BRT**. Migrações feitas antes das 03:00 do dia seguinte não estão no próximo backup — o backup mais seguro para rollback é o das 03:00 **do mesmo dia**, feito antes da intervenção.
