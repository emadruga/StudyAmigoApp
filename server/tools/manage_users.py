#!/usr/bin/env python3
"""
manage_users.py — Ferramenta administrativa para gerenciar contas duplicadas.

Modos de uso:
  --list-dupes [substring]          Lista usuários com contas duplicadas
  --dry-run --delete-users IDs      Gera SQL de deleção (não executa)
  --dry-run --reset-password ID     Gera SQL de reset de senha (não executa)
  --apply-to-local-cache --sql F    Aplica SQL sobre banco local
  --apply-to-production --sql F     Aplica SQL no EC2 via SSH

Exemplos:
  python manage_users.py --db admin.db --userdb-dir user_dbs/ --list-dupes
  python manage_users.py --db admin.db --userdb-dir user_dbs/ --list-dupes "Rogério"
  python manage_users.py --db admin.db --userdb-dir user_dbs/ --dry-run --delete-users 53,66,70,73,87
  python manage_users.py --db admin.db --userdb-dir user_dbs/ --dry-run --reset-password 107
  python manage_users.py --db admin.db --userdb-dir user_dbs/ --session-dir flask_session/ \\
      --apply-to-local-cache --sql migration_delete_20260406.sql
  python manage_users.py --apply-to-production --sql migration_delete_20260406.sql \\
      --ssh-host 54.152.109.26 --ssh-user ubuntu --ssh-key ~/.ssh/study-amigo-aws \\
      --remote-db /opt/study-amigo/server/admin.db \\
      --remote-userdb-dir /opt/study-amigo/server/user_dbs/ \\
      --remote-session-dir /opt/study-amigo/server/flask_session/
"""

import argparse
import getpass
import os
import pickle
import re
import sqlite3
import subprocess
import sys
from collections import defaultdict
from datetime import datetime


# ---------------------------------------------------------------------------
# .env loader
# ---------------------------------------------------------------------------

def _load_env(env_path=None):
    """Carrega variáveis de um arquivo .env para os defaults do script.

    Procura na seguinte ordem:
      1. Caminho explícito passado via --env-file
      2. manage_users.env no mesmo diretório do script
      3. .env no mesmo diretório do script
    """
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
    """Lê variável de ambiente com expansão de ~ no valor."""
    val = os.environ.get(key, default)
    return os.path.expanduser(val) if val else val


# ---------------------------------------------------------------------------
# Session helpers
# ---------------------------------------------------------------------------

def _read_session_file(path):
    """Desserializa um arquivo de sessão Flask-Session (cachelib/pickle com prefixo)."""
    try:
        with open(path, "rb") as f:
            raw = f.read()
        # cachelib prefixes the pickle payload with a small header ending at the
        # first occurrence of the pickle protocol opcode (0x80 = PROTO).
        idx = raw.find(b"\x80")
        if idx == -1:
            return None
        return pickle.loads(raw[idx:])
    except Exception:
        return None


def get_active_sessions_local(session_dir, user_ids):
    """Retorna dict {user_id: [arquivo, ...]} para sessões ativas locais."""
    active = defaultdict(list)
    if not session_dir or not os.path.isdir(session_dir):
        return active
    for fname in os.listdir(session_dir):
        fpath = os.path.join(session_dir, fname)
        if not os.path.isfile(fpath):
            continue
        data = _read_session_file(fpath)
        if isinstance(data, dict) and "user_id" in data and data["user_id"] in user_ids:
            active[data["user_id"]].append(fname)
    return active


def get_active_sessions_remote(ssh_args, remote_session_dir, user_ids):
    """Verifica sessões ativas no servidor remoto via SSH + python3."""
    script = f"""
import os, pickle
session_dir = {repr(remote_session_dir)}
user_ids = {repr(set(user_ids))}
active = {{}}
if os.path.isdir(session_dir):
    for fname in os.listdir(session_dir):
        fpath = os.path.join(session_dir, fname)
        if not os.path.isfile(fpath):
            continue
        try:
            with open(fpath, 'rb') as f:
                raw = f.read()
            idx = raw.find(b'\\x80')
            if idx == -1:
                continue
            data = pickle.loads(raw[idx:])
            if data and 'user_id' in data and data['user_id'] in user_ids:
                uid = data['user_id']
                active.setdefault(uid, []).append(fname)
        except Exception:
            pass
for uid, files in active.items():
    print(f"{{uid}}:{{','.join(files)}}")
"""
    cmd = ssh_args + ["python3", "-c", script]
    result = subprocess.run(cmd, capture_output=True, text=True)
    active = defaultdict(list)
    for line in result.stdout.strip().splitlines():
        if ":" in line:
            uid_str, files_str = line.split(":", 1)
            active[int(uid_str)] = files_str.split(",")
    return active


def warn_active_sessions(active, db_path):
    """Imprime aviso de sessões ativas e pede confirmação."""
    if not active:
        return True
    print("\n[AVISO] As seguintes contas têm sessões ativas no momento:")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    for uid, files in active.items():
        row = conn.execute("SELECT username, name FROM users WHERE user_id=?", (uid,)).fetchone()
        label = f"{row['name']} ({row['username']})" if row else f"user_id={uid}"
        print(f"  user_id={uid}  {label}  [{len(files)} sessão(ões)]")
    conn.close()
    print()
    ans = input("Deseja prosseguir mesmo assim? [s/N] ").strip().lower()
    return ans == "s"


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def open_db(path):
    if not os.path.isfile(path):
        print(f"Erro: banco de dados não encontrado: {path}")
        print("Verifique o valor de LOCAL_DB no manage_users.env ou o argumento --db.")
        sys.exit(1)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def get_revlog_count(userdb_dir, user_id):
    path = os.path.join(userdb_dir, f"user_{user_id}.db")
    if not os.path.isfile(path):
        return None
    try:
        conn = sqlite3.connect(path)
        count = conn.execute("SELECT COUNT(*) FROM revlog").fetchone()[0]
        conn.close()
        return count
    except Exception:
        return None


def get_notes_count(userdb_dir, user_id):
    path = os.path.join(userdb_dir, f"user_{user_id}.db")
    if not os.path.isfile(path):
        return None
    try:
        conn = sqlite3.connect(path)
        count = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        conn.close()
        return count
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Mode: --list-dupes
# ---------------------------------------------------------------------------

def cmd_list_dupes(args):
    if not os.path.isdir(args.userdb_dir):
        print(f"Erro: diretório de bancos individuais não encontrado: {args.userdb_dir}")
        print("Verifique o valor de LOCAL_USERDB no manage_users.env ou o argumento --userdb-dir.")
        sys.exit(1)
    conn = open_db(args.db)
    substring = args.list_dupes  # pode ser "" (sem filtro)

    if substring:
        rows = conn.execute(
            "SELECT user_id, username, name FROM users WHERE name LIKE ?",
            (f"%{substring}%",)
        ).fetchall()
    else:
        # Todos os usuários
        rows = conn.execute("SELECT user_id, username, name FROM users ORDER BY name").fetchall()

    # Agrupar por name normalizado
    groups = defaultdict(list)
    for row in rows:
        groups[row["name"]].append(row)

    if substring:
        # Mostrar todos que batem, independente de ser duplicata
        to_show = {k: v for k, v in groups.items()}
    else:
        # Mostrar apenas os que têm duplicatas
        to_show = {k: v for k, v in groups.items() if len(v) > 1}

    if not to_show:
        print("Nenhuma duplicata encontrada.")
        conn.close()
        return

    for name, users in sorted(to_show.items()):
        print(f"\n{'='*60}")
        print(f"Nome: {name}  ({len(users)} conta(s))")
        print(f"{'='*60}")
        print(f"  {'user_id':>8}  {'username':<20}  {'cartões':>8}  {'revisões':>9}")
        print(f"  {'-'*8}  {'-'*20}  {'-'*8}  {'-'*9}")
        for u in users:
            notes = get_notes_count(args.userdb_dir, u["user_id"])
            revs = get_revlog_count(args.userdb_dir, u["user_id"])
            notes_str = str(notes) if notes is not None else "n/a"
            revs_str = str(revs) if revs is not None else "n/a"
            print(f"  {u['user_id']:>8}  {u['username']:<20}  {notes_str:>8}  {revs_str:>9}")

    conn.close()


# ---------------------------------------------------------------------------
# Mode: --dry-run --delete-users
# ---------------------------------------------------------------------------

def cmd_dry_run_delete(args):
    ids = [int(x.strip()) for x in args.delete_users.split(",")]
    conn = open_db(args.db)

    rows = []
    for uid in ids:
        row = conn.execute(
            "SELECT user_id, username, name FROM users WHERE user_id=?", (uid,)
        ).fetchone()
        if row:
            rows.append(row)
        else:
            print(f"[AVISO] user_id={uid} não encontrado no banco — ignorado.")
    conn.close()

    if not rows:
        print("Nenhum usuário válido para deletar.")
        return

    date_str = datetime.now().strftime("%Y%m%d")
    fname = f"migration_delete_{date_str}.sql"

    with open(fname, "w", encoding="utf-8") as f:
        f.write("-- Deleção de contas duplicadas\n")
        f.write(f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} por manage_users.py\n")
        f.write("-- Revise cuidadosamente antes de aplicar.\n")
        f.write("--\n")
        for r in rows:
            f.write(f"-- user_id={r['user_id']}  username={r['username']}  nome={r['name']}\n")
        f.write("\n")
        id_list = ", ".join(str(r["user_id"]) for r in rows)
        f.write(f"DELETE FROM users WHERE user_id IN ({id_list});\n")
        f.write("\n")
        f.write("-- Remover arquivos de banco individual:\n")
        for r in rows:
            f.write(f"-- rm user_dbs/user_{r['user_id']}.db\n")

    print(f"SQL gerado: {os.path.abspath(fname)}")
    print(f"Contas a deletar: {id_list}")
    print("Nada foi alterado. Revise o arquivo antes de aplicar.")


# ---------------------------------------------------------------------------
# Mode: --dry-run --reset-password
# ---------------------------------------------------------------------------

def cmd_dry_run_reset_password(args):
    try:
        import bcrypt
    except ImportError:
        print("Erro: biblioteca 'bcrypt' não instalada. Execute: pip install bcrypt")
        sys.exit(1)

    uid = int(args.reset_password)
    conn = open_db(args.db)
    row = conn.execute(
        "SELECT user_id, username, name FROM users WHERE user_id=?", (uid,)
    ).fetchone()
    conn.close()

    if not row:
        print(f"Erro: user_id={uid} não encontrado.")
        sys.exit(1)

    print(f"Conta: user_id={row['user_id']}  username={row['username']}  nome={row['name']}")

    while True:
        pwd = getpass.getpass("Nova senha (10-20 caracteres): ")
        if not (10 <= len(pwd) <= 20):
            print("Senha deve ter entre 10 e 20 caracteres.")
            continue
        pwd2 = getpass.getpass("Confirme a nova senha: ")
        if pwd != pwd2:
            print("Senhas não conferem. Tente novamente.")
            continue
        break

    hashed = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    date_str = datetime.now().strftime("%Y%m%d")
    fname = f"migration_reset_pw_{date_str}.sql"

    with open(fname, "w", encoding="utf-8") as f:
        f.write("-- Reset de senha\n")
        f.write(f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} por manage_users.py\n")
        f.write("-- Revise cuidadosamente antes de aplicar.\n")
        f.write("--\n")
        f.write(f"-- user_id={row['user_id']}  username={row['username']}  nome={row['name']}\n")
        f.write("\n")
        # Escapar aspas simples no hash (precaução)
        safe_hash = hashed.replace("'", "''")
        f.write(f"UPDATE users SET password_hash = '{safe_hash}' WHERE user_id = {uid};\n")

    print(f"SQL gerado: {os.path.abspath(fname)}")
    print("Nada foi alterado. Revise o arquivo antes de aplicar.")


# ---------------------------------------------------------------------------
# SQL parser: extrai user_ids afetados e arquivos a remover
# ---------------------------------------------------------------------------

def parse_sql_file(sql_path):
    """Retorna (sql_statements, ids_afetados, arquivos_a_remover)."""
    with open(sql_path, encoding="utf-8") as f:
        content = f.read()

    # Extrair IDs de DELETE ... IN (...)
    ids_afetados = set()
    for m in re.finditer(r"DELETE\s+FROM\s+users\s+WHERE\s+user_id\s+IN\s*\(([^)]+)\)", content, re.IGNORECASE):
        for part in m.group(1).split(","):
            ids_afetados.add(int(part.strip()))

    # Extrair IDs de UPDATE ... WHERE user_id = N
    for m in re.finditer(r"WHERE\s+user_id\s*=\s*(\d+)", content, re.IGNORECASE):
        ids_afetados.add(int(m.group(1)))

    # Extrair arquivos de comentários "-- rm user_dbs/..."
    arquivos_remover = []
    for m in re.finditer(r"--\s*rm\s+(user_dbs/\S+)", content):
        arquivos_remover.append(m.group(1))

    # Extrair statements SQL executáveis (não comentários)
    statements = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("--"):
            statements.append(stripped)

    return " ".join(statements), ids_afetados, arquivos_remover


# ---------------------------------------------------------------------------
# Mode: --apply-to-local-cache
# ---------------------------------------------------------------------------

def cmd_apply_local(args):
    sql_text, ids_afetados, arquivos_remover = parse_sql_file(args.sql)

    # Verificar sessões ativas
    active = get_active_sessions_local(args.session_dir, ids_afetados)
    if active:
        if not warn_active_sessions(active, args.db):
            print("Operação cancelada.")
            return
    else:
        print("Nenhuma sessão ativa para os usuários afetados.")

    # Executar SQL
    conn = sqlite3.connect(args.db)
    try:
        conn.executescript(sql_text)
        conn.commit()
        print(f"SQL aplicado em: {args.db}")
    except Exception as e:
        conn.rollback()
        print(f"Erro ao executar SQL: {e}")
        conn.close()
        sys.exit(1)
    conn.close()

    # Remover arquivos user_dbs
    for rel_path in arquivos_remover:
        full_path = os.path.join(args.userdb_dir, os.path.basename(rel_path))
        if os.path.isfile(full_path):
            os.remove(full_path)
            print(f"Removido: {full_path}")
        else:
            print(f"[AVISO] Arquivo não encontrado (já removido?): {full_path}")

    print("\nConcluído.")


# ---------------------------------------------------------------------------
# Mode: --apply-to-production
# ---------------------------------------------------------------------------

def build_ssh_args(args):
    """Monta lista base de argumentos SSH."""
    cmd = ["ssh", "-i", os.path.expanduser(args.ssh_key),
           "-o", "StrictHostKeyChecking=no",
           f"{args.ssh_user}@{args.ssh_host}"]
    return cmd


def build_scp_args(args, local_file, remote_path):
    return ["scp", "-i", os.path.expanduser(args.ssh_key),
            "-o", "StrictHostKeyChecking=no",
            local_file, f"{args.ssh_user}@{args.ssh_host}:{remote_path}"]


def docker_db_path(remote_db):
    """Converte caminho do host para caminho dentro do container (./server → /app)."""
    # /opt/study-amigo/server/... → /app/...
    # Suporta qualquer sufixo após 'server/'
    import re as _re
    m = _re.search(r"/server(/.*)", remote_db)
    return "/app" + m.group(1) if m else remote_db


def docker_userdb_path(remote_userdb_dir):
    """Converte diretório user_dbs do host para caminho dentro do container."""
    import re as _re
    m = _re.search(r"/server(/.*)", remote_userdb_dir)
    return "/app" + m.group(1) if m else remote_userdb_dir


def cmd_apply_production(args):
    for required in ("ssh_host", "ssh_user", "ssh_key", "remote_db",
                     "remote_userdb_dir", "remote_session_dir"):
        if not getattr(args, required, None):
            print(f"Erro: --{required.replace('_', '-')} é obrigatório para --apply-to-production.")
            sys.exit(1)

    sql_text, ids_afetados, arquivos_remover = parse_sql_file(args.sql)
    ssh_args = build_ssh_args(args)
    container = args.docker_container
    container_db = docker_db_path(args.remote_db)
    container_userdb = docker_userdb_path(args.remote_userdb_dir)

    # Verificar sessões ativas remotas
    print("Verificando sessões ativas no servidor remoto...")
    active = get_active_sessions_remote(ssh_args, args.remote_session_dir, ids_afetados)
    if active:
        print("\n[AVISO] As seguintes contas têm sessões ativas no servidor:")
        for uid, files in active.items():
            result = subprocess.run(
                ssh_args + [f"sudo docker exec {container} sqlite3 {container_db} "
                            f"\"SELECT username||' / '||name FROM users WHERE user_id={uid};\""],
                capture_output=True, text=True
            )
            label = result.stdout.strip() or f"user_id={uid}"
            print(f"  user_id={uid}  {label}  [{len(files)} sessão(ões)]")
        print()
        ans = input("Deseja prosseguir mesmo assim? [s/N] ").strip().lower()
        if ans != "s":
            print("Operação cancelada.")
            return
    else:
        print("Nenhuma sessão ativa para os usuários afetados.")

    # Copiar SQL para /tmp/ no servidor
    remote_sql = f"/tmp/{os.path.basename(args.sql)}"
    print(f"\nCopiando {args.sql} para {args.ssh_host}:{remote_sql} ...")
    scp_cmd = build_scp_args(args, args.sql, remote_sql)
    result = subprocess.run(scp_cmd)
    if result.returncode != 0:
        print("Erro ao copiar o arquivo SQL. Abortando.")
        sys.exit(1)

    # Executar SQL dentro do container Docker
    print(f"Executando SQL em {container}:{container_db} ...")
    exec_cmd = ssh_args + [
        f"sudo docker exec -i {container} sqlite3 {container_db} < {remote_sql}"
    ]
    result = subprocess.run(exec_cmd)
    if result.returncode != 0:
        print("Erro ao executar SQL no servidor. Verifique manualmente.")
        sys.exit(1)
    print("SQL aplicado com sucesso.")

    # Remover arquivos user_dbs dentro do container
    for rel_path in arquivos_remover:
        container_file = container_userdb.rstrip("/") + "/" + os.path.basename(rel_path)
        print(f"Removendo {container}:{container_file} ...")
        rm_cmd = ssh_args + [f"sudo docker exec {container} rm -f {container_file}"]
        subprocess.run(rm_cmd)

    # Limpar arquivo temporário no host
    subprocess.run(ssh_args + [f"rm -f {remote_sql}"])

    print("\nConcluído.")


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def main():
    # Pré-parse para capturar --conf/-f antes de carregar o .env
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--conf", "-f", dest="env_file", default=None)
    pre_args, _ = pre.parse_known_args()
    env_loaded = _load_env(pre_args.env_file)

    parser = argparse.ArgumentParser(
        description="Ferramenta administrativa: gerencia contas duplicadas no StudyAmigo.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Arquivo .env opcional
    parser.add_argument("--conf", "-f", dest="env_file", metavar="ARQUIVO",
                        help="Caminho para arquivo .env com variáveis de configuração.")

    # Banco e diretórios (para operações locais) — defaults via .env
    parser.add_argument("--db", default=_env("LOCAL_DB"),
                        help="Caminho para admin.db [LOCAL_DB]")
    parser.add_argument("--userdb-dir", dest="userdb_dir", default=_env("LOCAL_USERDB"),
                        help="Diretório com bancos individuais user_N.db [LOCAL_USERDB]")
    parser.add_argument("--session-dir", dest="session_dir", default=_env("LOCAL_SESSION"),
                        help="Diretório com arquivos de sessão Flask [LOCAL_SESSION]")

    # Modos de operação
    parser.add_argument("--list-dupes", nargs="?", const="", metavar="SUBSTRING",
                        help="Lista duplicatas. Sem argumento: todos; com argumento: filtra por nome.")
    parser.add_argument("--dry-run", action="store_true", help="Modo dry-run: gera SQL sem executar.")
    parser.add_argument("--delete-users", dest="delete_users", metavar="ID1,ID2,...",
                        help="IDs a deletar (usar com --dry-run).")
    parser.add_argument("--reset-password", dest="reset_password", metavar="USER_ID",
                        help="Reset de senha interativo (usar com --dry-run).")

    parser.add_argument("--apply-to-local-cache", action="store_true",
                        help="Aplica --sql sobre o banco local.")
    parser.add_argument("--apply-to-production", action="store_true",
                        help="Aplica --sql no servidor remoto via SSH.")
    parser.add_argument("--sql", metavar="ARQUIVO.sql",
                        help="Arquivo SQL gerado pelo --dry-run.")

    # SSH (para --apply-to-production) — defaults via .env
    parser.add_argument("--ssh-host", dest="ssh_host", default=_env("PROD_HOST"), metavar="HOST")
    parser.add_argument("--ssh-user", dest="ssh_user", default=_env("PROD_USER"), metavar="USER")
    parser.add_argument("--ssh-key", dest="ssh_key", default=_env("PROD_KEY"), metavar="CHAVE")
    parser.add_argument("--remote-db", dest="remote_db", default=_env("PROD_DB"), metavar="CAMINHO")
    parser.add_argument("--remote-userdb-dir", dest="remote_userdb_dir", default=_env("PROD_USERDB"), metavar="CAMINHO")
    parser.add_argument("--remote-session-dir", dest="remote_session_dir", default=_env("PROD_SESSION"), metavar="CAMINHO")
    parser.add_argument("--docker-container", dest="docker_container",
                        default=_env("PROD_CONTAINER", "flashcard_server"), metavar="NOME",
                        help="Nome do container Docker no servidor [PROD_CONTAINER=flashcard_server]")

    args = parser.parse_args()

    if env_loaded:
        print(f"[config] Usando .env: {env_loaded}")

    # Roteamento
    if args.list_dupes is not None:
        _require(args, ["db", "userdb_dir"], "--list-dupes")
        cmd_list_dupes(args)

    elif args.dry_run and args.delete_users:
        _require(args, ["db"], "--dry-run --delete-users")
        cmd_dry_run_delete(args)

    elif args.dry_run and args.reset_password:
        _require(args, ["db"], "--dry-run --reset-password")
        cmd_dry_run_reset_password(args)

    elif args.apply_to_local_cache:
        _require(args, ["db", "userdb_dir", "sql"], "--apply-to-local-cache")
        cmd_apply_local(args)

    elif args.apply_to_production:
        _require(args, ["sql"], "--apply-to-production")
        cmd_apply_production(args)

    else:
        parser.print_help()


def _require(args, fields, mode):
    for field in fields:
        if not getattr(args, field, None):
            print(f"Erro: --{field.replace('_', '-')} é obrigatório para {mode}.")
            sys.exit(1)


if __name__ == "__main__":
    main()
