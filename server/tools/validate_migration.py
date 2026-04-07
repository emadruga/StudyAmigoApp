#!/usr/bin/env python3
"""
validate_migration.py — Valida se uma migração foi aplicada corretamente.

Lê um arquivo .sql gerado pelo manage_users.py e verifica no banco alvo
(local ou produção via SSH) se as operações foram executadas com sucesso.

Modos:
  --validate-local --sql <arquivo.sql>      Valida no banco local
  --validate-production --sql <arquivo.sql> Valida no EC2 via SSH

Exemplos:
  python server/tools/validate_migration.py \\
      --validate-local --sql migration_delete_20260407.sql

  python server/tools/validate_migration.py \\
      --validate-production --sql migration_delete_20260407.sql

  python server/tools/validate_migration.py \\
      --validate-production --sql migration_reset_pw_20260407.sql
"""

import argparse
import os
import re
import sqlite3
import subprocess
import sys
from datetime import datetime


# ---------------------------------------------------------------------------
# .env loader (mesmo padrão do manage_users.py)
# ---------------------------------------------------------------------------

def _load_env(env_path=None):
    candidates = []
    if env_path:
        candidates.append(env_path)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates += [
        os.path.join(script_dir, "manage_users.env"),
        os.path.join(script_dir, ".env"),
    ]
    for path in candidates:
        expanded = os.path.expanduser(path)
        if os.path.isfile(expanded):
            with open(expanded) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip())
            return expanded
    return None


def _env(key, default=None):
    val = os.environ.get(key, default)
    return os.path.expanduser(val) if val else val


# ---------------------------------------------------------------------------
# SQL parser (igual ao manage_users.py)
# ---------------------------------------------------------------------------

def parse_sql_file(sql_path):
    """Extrai operações do .sql gerado pelo manage_users.py."""
    with open(sql_path, encoding="utf-8") as f:
        content = f.read()

    # DELETE ... WHERE user_id IN (...)
    deleted_ids = set()
    for m in re.finditer(r"DELETE\s+FROM\s+users\s+WHERE\s+user_id\s+IN\s*\(([^)]+)\)", content, re.IGNORECASE):
        for part in m.group(1).split(","):
            deleted_ids.add(int(part.strip()))

    # UPDATE ... WHERE user_id = N
    reset_ids = set()
    for m in re.finditer(r"UPDATE\s+users\s+SET\s+password_hash.*?WHERE\s+user_id\s*=\s*(\d+)", content, re.IGNORECASE):
        reset_ids.add(int(m.group(1)))

    # Arquivos db a remover (comentários "-- rm user_dbs/...")
    removed_files = []
    for m in re.finditer(r"--\s*rm\s+(user_dbs/\S+)", content):
        removed_files.append(m.group(1))

    return deleted_ids, reset_ids, removed_files


# ---------------------------------------------------------------------------
# Validação local
# ---------------------------------------------------------------------------

def validate_local(args):
    deleted_ids, reset_ids, removed_files = parse_sql_file(args.sql)
    db_path = args.db
    userdb_dir = args.userdb_dir
    ok = True

    print(f"\n{'='*60}")
    print(f"Validação LOCAL: {db_path}")
    print(f"SQL aplicado:    {args.sql}")
    print(f"{'='*60}\n")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # 1. Verificar deleções
    if deleted_ids:
        print(f"[ DELETE ] Verificando {len(deleted_ids)} conta(s) removida(s)...")
        for uid in sorted(deleted_ids):
            row = conn.execute("SELECT user_id, username, name FROM users WHERE user_id=?", (uid,)).fetchone()
            if row is None:
                print(f"  OK  user_id={uid} não existe no banco (deletado corretamente)")
            else:
                print(f"  FALHA  user_id={uid} AINDA EXISTE: username={row['username']} nome={row['name']}")
                ok = False

    # 2. Verificar arquivos .db removidos
    if removed_files:
        print(f"\n[ ARQUIVOS ] Verificando {len(removed_files)} arquivo(s) removido(s)...")
        for rel_path in removed_files:
            full_path = os.path.join(userdb_dir, os.path.basename(rel_path))
            if not os.path.isfile(full_path):
                print(f"  OK  {full_path} removido")
            else:
                print(f"  FALHA  {full_path} AINDA EXISTE")
                ok = False

    # 3. Verificar reset de senha (só confirma que o hash mudou — não testa login)
    if reset_ids:
        print(f"\n[ SENHA ] Verificando {len(reset_ids)} reset(s) de senha...")
        for uid in sorted(reset_ids):
            row = conn.execute("SELECT user_id, username, name, password_hash FROM users WHERE user_id=?", (uid,)).fetchone()
            if row is None:
                print(f"  AVISO  user_id={uid} não encontrado no banco")
                ok = False
            else:
                ph = row["password_hash"]
                is_bcrypt = ph.startswith("$2b$") or ph.startswith("$2a$")
                if is_bcrypt:
                    print(f"  OK  user_id={uid} ({row['username']}) tem hash bcrypt válido")
                else:
                    print(f"  FALHA  user_id={uid} hash não parece bcrypt: {ph[:20]}...")
                    ok = False

    conn.close()

    print(f"\n{'='*60}")
    if ok:
        print("RESULTADO: TUDO OK")
    else:
        print("RESULTADO: FALHAS ENCONTRADAS — verifique acima")
    print(f"{'='*60}\n")
    return ok


# ---------------------------------------------------------------------------
# Validação em produção via SSH
# ---------------------------------------------------------------------------

def ssh_query(ssh_args, remote_db, query):
    """Executa uma query SQLite no servidor remoto e retorna as linhas."""
    cmd = ssh_args + [f'sqlite3 {remote_db} "{query}"']
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode


def ssh_file_exists(ssh_args, remote_path):
    cmd = ssh_args + [f"test -f {remote_path} && echo EXISTS || echo MISSING"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip() == "EXISTS"


def build_ssh_args(args):
    return ["ssh", "-i", os.path.expanduser(args.ssh_key),
            "-o", "StrictHostKeyChecking=no",
            f"{args.ssh_user}@{args.ssh_host}"]


def validate_production(args):
    for required in ("ssh_host", "ssh_user", "ssh_key", "remote_db", "remote_userdb_dir"):
        if not getattr(args, required, None):
            print(f"Erro: --{required.replace('_','-')} é obrigatório para --validate-production.")
            sys.exit(1)

    deleted_ids, reset_ids, removed_files = parse_sql_file(args.sql)
    ssh_args = build_ssh_args(args)
    ok = True

    print(f"\n{'='*60}")
    print(f"Validação PRODUÇÃO: {args.ssh_host}:{args.remote_db}")
    print(f"SQL aplicado:       {args.sql}")
    print(f"{'='*60}\n")

    # 1. Verificar deleções
    if deleted_ids:
        print(f"[ DELETE ] Verificando {len(deleted_ids)} conta(s) removida(s)...")
        ids_str = ",".join(str(i) for i in sorted(deleted_ids))
        out, _ = ssh_query(
            ssh_args, args.remote_db,
            f"SELECT user_id||'|'||username||'|'||name FROM users WHERE user_id IN ({ids_str});"
        )
        still_exist = {}
        if out:
            for line in out.splitlines():
                parts = line.split("|", 2)
                if len(parts) == 3:
                    still_exist[int(parts[0])] = (parts[1], parts[2])

        for uid in sorted(deleted_ids):
            if uid not in still_exist:
                print(f"  OK  user_id={uid} não existe no banco (deletado corretamente)")
            else:
                uname, name = still_exist[uid]
                print(f"  FALHA  user_id={uid} AINDA EXISTE: username={uname} nome={name}")
                ok = False

    # 2. Verificar arquivos .db removidos
    if removed_files:
        print(f"\n[ ARQUIVOS ] Verificando {len(removed_files)} arquivo(s) removido(s)...")
        for rel_path in removed_files:
            remote_file = os.path.join(args.remote_userdb_dir, os.path.basename(rel_path))
            exists = ssh_file_exists(ssh_args, remote_file)
            if not exists:
                print(f"  OK  {remote_file} removido")
            else:
                print(f"  FALHA  {remote_file} AINDA EXISTE")
                ok = False

    # 3. Verificar reset de senha
    if reset_ids:
        print(f"\n[ SENHA ] Verificando {len(reset_ids)} reset(s) de senha...")
        for uid in sorted(reset_ids):
            out, _ = ssh_query(
                ssh_args, args.remote_db,
                f"SELECT username||'|'||password_hash FROM users WHERE user_id={uid};"
            )
            if not out:
                print(f"  AVISO  user_id={uid} não encontrado no banco")
                ok = False
            else:
                parts = out.split("|", 1)
                uname = parts[0]
                ph = parts[1] if len(parts) > 1 else ""
                is_bcrypt = ph.startswith("$2b$") or ph.startswith("$2a$")
                if is_bcrypt:
                    print(f"  OK  user_id={uid} ({uname}) tem hash bcrypt válido")
                else:
                    print(f"  FALHA  user_id={uid} hash não parece bcrypt: {ph[:20]}...")
                    ok = False

    print(f"\n{'='*60}")
    if ok:
        print("RESULTADO: TUDO OK")
    else:
        print("RESULTADO: FALHAS ENCONTRADAS — verifique acima")
    print(f"{'='*60}\n")
    return ok


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def main():
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--conf", "-f", dest="env_file", default=None)
    pre_args, _ = pre.parse_known_args()
    env_loaded = _load_env(pre_args.env_file)

    parser = argparse.ArgumentParser(
        description="Valida se uma migração gerada pelo manage_users.py foi aplicada corretamente.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument("--conf", "-f", dest="env_file", metavar="ARQUIVO",
                        help="Arquivo .env de configuração [manage_users.env]")
    parser.add_argument("--sql", required=True, metavar="ARQUIVO.sql",
                        help="Arquivo SQL cuja aplicação será validada")

    parser.add_argument("--validate-local", action="store_true",
                        help="Valida no banco local")
    parser.add_argument("--validate-production", action="store_true",
                        help="Valida no EC2 via SSH")

    # Local
    parser.add_argument("--db", default=_env("LOCAL_DB"), metavar="CAMINHO",
                        help="Caminho para admin.db local [LOCAL_DB]")
    parser.add_argument("--userdb-dir", dest="userdb_dir", default=_env("LOCAL_USERDB"), metavar="CAMINHO",
                        help="Diretório com bancos individuais [LOCAL_USERDB]")

    # SSH / produção
    parser.add_argument("--ssh-host", dest="ssh_host", default=_env("PROD_HOST"), metavar="HOST")
    parser.add_argument("--ssh-user", dest="ssh_user", default=_env("PROD_USER"), metavar="USER")
    parser.add_argument("--ssh-key", dest="ssh_key", default=_env("PROD_KEY"), metavar="CHAVE")
    parser.add_argument("--remote-db", dest="remote_db", default=_env("PROD_DB"), metavar="CAMINHO")
    parser.add_argument("--remote-userdb-dir", dest="remote_userdb_dir", default=_env("PROD_USERDB"), metavar="CAMINHO")

    args = parser.parse_args()

    if env_loaded:
        print(f"[config] Usando .env: {env_loaded}")

    if args.validate_local:
        if not args.db:
            print("Erro: --db é obrigatório para --validate-local.")
            sys.exit(1)
        success = validate_local(args)
    elif args.validate_production:
        success = validate_production(args)
    else:
        parser.print_help()
        sys.exit(0)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
