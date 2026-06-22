#!/usr/bin/env python3
"""
assess_source_tracking.py — E04
================================
Verifica a rastreabilidade de fontes no baralho AUTHENTIC_E04.

Para cada aluno com baralho AUTHENTIC_E04, o script:
  1. Busca cartões cuja frente contenha "FONTE" (case-insensitive) → cartões-metadado
  2. Extrai URL ou referência do verso de cada cartão-metadado
  3. Valida o formato da referência (URL válida ou padrão "Artista — Título")
  4. Conta os cartões de vocabulário entre cartões-metadado consecutivos
  5. Gera flags: SEM_FONTE, FONTE_INVALIDA, POUCOS_CARTOES

Outputs:
  - E04_source_tracking_detail.csv  — uma linha por fonte por aluno
  - E04_source_tracking_summary.csv — uma linha por aluno
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import unicodedata
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

# ─── Constantes ──────────────────────────────────────────────────────────────

MATCH_THRESHOLD = 0.55
SEP = "\x1f"  # Separador de campos nas notas Anki

MIN_VOCAB_CARDS = {1: 5, 2: 7, 3: 8}   # mínimo por tier
MIN_SOURCES     = {1: 1, 2: 1, 3: 2}   # fontes mínimas por tier

DETAIL_FIELDS = [
    "student_id", "name", "tier", "source_index",
    "source_type", "source_ref", "source_valid",
    "vocab_card_count", "flag",
]

SUMMARY_FIELDS = [
    "student_id", "name", "tier",
    "total_sources", "total_vocab_cards",
    "valid_sources", "invalid_sources",
    "flags",
]

# ─── Utilidades de nome ───────────────────────────────────────────────────────

def _normalise(name: str) -> str:
    """Remove acentos, pontuação e caixa para comparação fuzzy."""
    nfkd = unicodedata.normalize("NFD", name)
    ascii_str = "".join(c for c in nfkd if not unicodedata.combining(c))
    ascii_str = re.sub(r"[^a-z0-9 ]", " ", ascii_str.lower())
    return re.sub(r"\s+", " ", ascii_str).strip()

# ─── Carga de dados ───────────────────────────────────────────────────────────

def load_users(admin_db: Path) -> Dict[int, Dict]:
    """Retorna {user_id: {'username': …, 'name': …}}."""
    conn = sqlite3.connect(str(admin_db))
    rows = conn.execute("SELECT user_id, username, name FROM users").fetchall()
    conn.close()
    return {r[0]: {"username": r[1], "name": r[2]} for r in rows}


def find_user_db(user_dbs_dir: Path, user_id: int) -> Optional[Path]:
    p = user_dbs_dir / f"user_{user_id}.db"
    return p if p.exists() else None


def load_roster(roster_path: Path) -> List[Dict]:
    """Lê o roster CSV e normaliza colunas."""
    students: List[Dict] = []
    with open(roster_path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            # Normaliza chaves
            norm = {k.strip().lower(): v.strip() for k, v in row.items()}
            sid_raw = norm.get("id") or norm.get("student_id") or ""
            if not sid_raw.isdigit():
                continue
            name = norm.get("name") or norm.get("nome") or ""
            tier_raw = norm.get("suggested tier") or norm.get("tier") or ""
            m = re.search(r"(\d)", tier_raw)
            tier = int(m.group(1)) if m else None
            students.append({
                "student_id": int(sid_raw),
                "name": name,
                "tier": tier,
                "user_id": None,
                "_matched_uids": [],
            })
    return students


def load_account_map(account_map_path: Path) -> Dict[str, str]:
    """Retorna {username_lower: roster_name}."""
    mapping: Dict[str, str] = {}
    with open(account_map_path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            norm = {k.strip().lower(): v.strip() for k, v in row.items()}
            username = norm.get("username", "")
            roster_name = norm.get("roster_name", "")
            if username and roster_name:
                mapping[username.lower()] = roster_name
    return mapping


def match_roster_to_users(
    students: List[Dict],
    users: Dict[int, Dict],
    account_map: Dict[str, str],
) -> None:
    """Resolve cada aluno do roster para user_id(s) via fuzzy + account_map (in-place)."""
    # Índice de nome normalizado → lista de user_ids
    norm_to_uids: Dict[str, List[int]] = {}
    for uid, info in users.items():
        n = _normalise(info["name"])
        norm_to_uids.setdefault(n, []).append(uid)

    # Fuzzy matching
    used_uids: set[int] = set()
    candidates: List[Tuple[float, int, int]] = []  # (score, student_idx, uid)
    for s_idx, s in enumerate(students):
        s_norm = _normalise(s["name"])
        for norm_name, uids in norm_to_uids.items():
            score = SequenceMatcher(None, s_norm, norm_name).ratio()
            if score >= MATCH_THRESHOLD:
                for uid in uids:
                    candidates.append((score, s_idx, uid))

    candidates.sort(key=lambda x: -x[0])
    for score, s_idx, uid in candidates:
        if uid in used_uids:
            continue
        if students[s_idx]["user_id"] is None:
            students[s_idx]["user_id"] = uid
        students[s_idx]["_matched_uids"].append(uid)
        used_uids.add(uid)

    # Account map: adiciona UIDs secundários
    name_to_student: Dict[str, int] = {
        _normalise(s["name"]): i for i, s in enumerate(students)
    }
    for username_lower, roster_name in account_map.items():
        roster_norm = _normalise(roster_name)
        s_idx = name_to_student.get(roster_norm)
        if s_idx is None:
            continue
        # Encontra uid correspondente ao username
        for uid, info in users.items():
            if info["username"].lower() == username_lower and uid not in students[s_idx]["_matched_uids"]:
                students[s_idx]["_matched_uids"].append(uid)

# ─── Leitura do banco Anki ────────────────────────────────────────────────────

def get_deck_id(conn: sqlite3.Connection, deck_name: str) -> Optional[int]:
    """Retorna o deck id para o nome exato do baralho."""
    row = conn.execute("SELECT decks FROM col LIMIT 1").fetchone()
    if not row:
        return None
    try:
        decks = json.loads(row[0])
    except (json.JSONDecodeError, TypeError):
        return None
    for did_str, deck in decks.items():
        if deck.get("name", "") == deck_name:
            return int(did_str)
    return None


def _ts(dt: datetime) -> int:
    """Datetime → milissegundos epoch (Anki card.id / note.id usam ms)."""
    return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)


def fetch_cards_in_deck(
    conn: sqlite3.Connection,
    deck_id: int,
    start_ms: int,
    end_ms: int,
) -> List[Tuple[int, str, str]]:
    """
    Retorna lista de (card_id, front, back) do baralho no período.
    Ordenados por card_id (proxy para ordem de criação).
    """
    rows = conn.execute(
        """
        SELECT c.id, n.flds
        FROM cards c
        JOIN notes n ON c.nid = n.id
        WHERE c.did = ?
          AND c.id BETWEEN ? AND ?
        ORDER BY c.id ASC
        """,
        (deck_id, start_ms, end_ms),
    ).fetchall()

    result = []
    for card_id, flds in rows:
        parts = flds.split(SEP)
        front = re.sub(r"<[^>]+>", "", parts[0]).strip() if len(parts) > 0 else ""
        back  = re.sub(r"<[^>]+>", "", parts[1]).strip() if len(parts) > 1 else ""
        result.append((card_id, front, back))
    return result

# ─── Validação de fonte ───────────────────────────────────────────────────────

def _is_valid_url(text: str) -> bool:
    """Verifica se o texto contém uma URL HTTP/HTTPS válida."""
    urls = re.findall(r"https?://[^\s\"'<>]+", text)
    for url in urls:
        try:
            parsed = urlparse(url)
            if parsed.scheme in ("http", "https") and parsed.netloc:
                return True
        except Exception:
            pass
    return False


def _is_artist_title(text: str) -> bool:
    """
    Verifica padrão "Artista — Título" ou "Artista - Título".
    Aceita tanto travessão (—) quanto hífen (-).
    """
    return bool(re.search(r".+[\u2014\-].+", text.strip()))


def detect_source_type(back: str) -> str:
    """Detecta tipo de fonte: 'video', 'music' ou 'unknown'."""
    b = back.lower()
    if "youtube.com" in b or "youtu.be" in b:
        return "video"
    if any(domain in b for domain in ("genius.com", "azlyrics.com", "vagalume.com", "letras.mus.br")):
        return "music"
    if _is_valid_url(back):
        return "video"  # URL genérica tratada como vídeo
    if _is_artist_title(back):
        return "music"
    return "unknown"


def validate_source_ref(back: str) -> Tuple[bool, str]:
    """
    Retorna (is_valid, source_type).
    Válido se: URL HTTP/HTTPS presente, OU padrão Artista — Título.
    """
    if _is_valid_url(back):
        return True, detect_source_type(back)
    if _is_artist_title(back):
        return True, "music"
    return False, "unknown"


def is_metadata_card(front: str) -> bool:
    """True se a frente do cartão contém 'FONTE' (case-insensitive)."""
    return "fonte" in front.lower()

# ─── Análise por aluno ────────────────────────────────────────────────────────

def analyse_student(
    db_path: Path,
    deck_name: str,
    start_dt: datetime,
    end_dt: datetime,
    tier: Optional[int],
) -> Optional[Dict]:
    """
    Analisa o baralho AUTHENTIC_E04 de um aluno.
    Retorna dict com 'sources' (lista de info por fonte) e 'summary'.
    Retorna None se baralho não encontrado.
    """
    conn = sqlite3.connect(str(db_path))
    try:
        deck_id = get_deck_id(conn, deck_name)
        if deck_id is None:
            return None

        start_ms = _ts(start_dt)
        end_ms   = _ts(end_dt)
        cards = fetch_cards_in_deck(conn, deck_id, start_ms, end_ms)
    finally:
        conn.close()

    if not cards:
        return None

    # Agrupa cartões por fonte
    sources: List[Dict] = []
    current_source: Optional[Dict] = None
    no_metadata_vocab: List[Tuple] = []  # cartões antes do primeiro metadado

    for card_id, front, back in cards:
        if is_metadata_card(front):
            # Salva grupo anterior
            if current_source is not None:
                sources.append(current_source)
            # Inicia novo grupo
            is_valid, src_type = validate_source_ref(back)
            current_source = {
                "source_type": src_type,
                "source_ref": back,
                "source_valid": is_valid,
                "vocab_cards": [],
            }
        else:
            if current_source is not None:
                current_source["vocab_cards"].append((card_id, front, back))
            else:
                no_metadata_vocab.append((card_id, front, back))

    # Fecha último grupo
    if current_source is not None:
        sources.append(current_source)

    return {
        "sources": sources,
        "no_metadata_vocab": no_metadata_vocab,
        "total_cards": len(cards),
        "tier": tier,
    }


def build_detail_rows(
    student_id: int,
    name: str,
    tier: Optional[int],
    analysis: Dict,
    min_vocab: int,
) -> List[Dict]:
    rows = []
    sources = analysis["sources"]

    if not sources and analysis["no_metadata_vocab"]:
        # Todos os cartões existem mas nenhum metadado
        rows.append({
            "student_id": student_id,
            "name": name,
            "tier": tier or "",
            "source_index": 1,
            "source_type": "unknown",
            "source_ref": "",
            "source_valid": False,
            "vocab_card_count": len(analysis["no_metadata_vocab"]),
            "flag": "SEM_FONTE",
        })
        return rows

    if not sources:
        # Nenhum cartão no baralho
        return []

    for i, src in enumerate(sources, start=1):
        n_vocab = len(src["vocab_cards"])
        flags = []
        if not src["source_valid"]:
            flags.append("FONTE_INVALIDA")
        if n_vocab < min_vocab:
            flags.append("POUCOS_CARTOES")

        rows.append({
            "student_id": student_id,
            "name": name,
            "tier": tier or "",
            "source_index": i,
            "source_type": src["source_type"],
            "source_ref": src["source_ref"],
            "source_valid": src["source_valid"],
            "vocab_card_count": n_vocab,
            "flag": " ".join(flags) if flags else "",
        })

    return rows


def build_summary_row(
    student_id: int,
    name: str,
    tier: Optional[int],
    analysis: Optional[Dict],
    detail_rows: List[Dict],
    min_sources: int,
) -> Dict:
    if analysis is None:
        return {
            "student_id": student_id,
            "name": name,
            "tier": tier or "",
            "total_sources": 0,
            "total_vocab_cards": 0,
            "valid_sources": 0,
            "invalid_sources": 0,
            "flags": "SEM_BARALHO",
        }

    sources = analysis["sources"]
    total_sources = len(sources)
    total_vocab = sum(len(s["vocab_cards"]) for s in sources)
    no_meta_vocab = len(analysis["no_metadata_vocab"])
    valid_sources = sum(1 for s in sources if s["source_valid"])
    invalid_sources = total_sources - valid_sources

    agg_flags = set()
    for row in detail_rows:
        for f in row["flag"].split():
            agg_flags.add(f)

    # Flag adicional se faltam fontes mínimas
    if total_sources < min_sources:
        agg_flags.add("POUCAS_FONTES")

    # Cartões sem metadado
    if no_meta_vocab > 0 and total_sources == 0:
        agg_flags.add("SEM_FONTE")
    elif no_meta_vocab > 0:
        agg_flags.add("CARTOES_SEM_FONTE")

    return {
        "student_id": student_id,
        "name": name,
        "tier": tier or "",
        "total_sources": total_sources,
        "total_vocab_cards": total_vocab + no_meta_vocab,
        "valid_sources": valid_sources,
        "invalid_sources": invalid_sources,
        "flags": " ".join(sorted(agg_flags)) if agg_flags else "",
    }

# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Verifica rastreabilidade de fontes no baralho AUTHENTIC_E04 "
            "(cartões-metadado com emoji 📺/🎵 FONTE)."
        )
    )
    parser.add_argument("--start", required=True, help="Data de início (YYYY-MM-DD)")
    parser.add_argument("--end",   required=True, help="Data de fim (YYYY-MM-DD)")
    parser.add_argument("--roster",      required=True, help="CSV do roster de alunos")
    parser.add_argument("--account-map", required=True, help="CSV de mapeamento de contas")
    parser.add_argument("--admin-db",    required=True, help="Caminho para admin.db")
    parser.add_argument("--user-db-dir", required=True, help="Diretório com user_*.db")
    parser.add_argument(
        "--deck-name", default="AUTHENTIC_E04",
        help="Nome exato do baralho Component C (padrão: AUTHENTIC_E04)",
    )
    parser.add_argument(
        "--detail-output", default="placement_exam/planning_E04/output/E04_source_tracking_detail.csv",
        help="Caminho do CSV detalhado (uma linha por fonte)",
    )
    parser.add_argument(
        "--summary-output", default="placement_exam/planning_E04/output/E04_source_tracking_summary.csv",
        help="Caminho do CSV resumido (uma linha por aluno)",
    )
    args = parser.parse_args()

    start_dt = datetime.strptime(args.start, "%Y-%m-%d")
    end_dt   = datetime.strptime(args.end,   "%Y-%m-%d").replace(
        hour=23, minute=59, second=59
    )

    admin_db    = Path(args.admin_db).expanduser()
    user_db_dir = Path(args.user_db_dir).expanduser()
    roster_path = Path(args.roster).expanduser()
    acct_map_path = Path(args.account_map).expanduser()
    detail_out  = Path(args.detail_output)
    summary_out = Path(args.summary_output)
    detail_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.parent.mkdir(parents=True, exist_ok=True)

    print(f"  Janela: {args.start} → {args.end}")
    print(f"  Baralho: {args.deck_name}")

    users    = load_users(admin_db)
    students = load_roster(roster_path)
    acct_map = load_account_map(acct_map_path)
    match_roster_to_users(students, users, acct_map)

    print(f"  Roster: {len(students)} alunos | admin.db: {len(users)} usuários")

    all_detail: List[Dict] = []
    all_summary: List[Dict] = []

    students_with_deck = 0
    students_no_deck   = 0
    students_no_db     = 0
    total_sources      = 0
    total_vocab_cards  = 0

    for s in students:
        tier = s["tier"]
        min_vocab   = MIN_VOCAB_CARDS.get(tier, 5)
        min_sources = MIN_SOURCES.get(tier, 1)

        # Resolve DB
        db_path: Optional[Path] = None
        for uid in s["_matched_uids"]:
            candidate = find_user_db(user_db_dir, uid)
            if candidate is not None:
                db_path = candidate
                break

        if db_path is None:
            students_no_db += 1
            summary_row = build_summary_row(
                s["student_id"], s["name"], tier, None, [], min_sources
            )
            all_summary.append(summary_row)
            continue

        analysis = analyse_student(db_path, args.deck_name, start_dt, end_dt, tier)

        if analysis is None:
            students_no_deck += 1
            summary_row = build_summary_row(
                s["student_id"], s["name"], tier, None, [], min_sources
            )
            all_summary.append(summary_row)
            continue

        students_with_deck += 1
        detail_rows = build_detail_rows(
            s["student_id"], s["name"], tier, analysis, min_vocab
        )
        summary_row = build_summary_row(
            s["student_id"], s["name"], tier, analysis, detail_rows, min_sources
        )
        all_detail.extend(detail_rows)
        all_summary.append(summary_row)

        total_sources    += int(summary_row["total_sources"])
        total_vocab_cards += int(summary_row["total_vocab_cards"])

    # ── Escreve CSVs ──────────────────────────────────────────────────────────
    with open(detail_out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=DETAIL_FIELDS)
        writer.writeheader()
        writer.writerows(all_detail)

    with open(summary_out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(all_summary)

    # ── Sumário no terminal ───────────────────────────────────────────────────
    from collections import Counter
    flag_counts = Counter()
    for row in all_summary:
        for f in row["flags"].split():
            if f and f != "SEM_BARALHO":
                flag_counts[f] += 1

    students_with_source = sum(
        1 for r in all_summary
        if int(r.get("total_sources", 0)) > 0
    )
    students_sem_fonte = sum(
        1 for r in all_summary
        if "SEM_FONTE" in r.get("flags", "") or "SEM_BARALHO" in r.get("flags", "")
    )
    valid_src_total = sum(int(r.get("valid_sources", 0)) for r in all_summary)
    invalid_src_total = sum(int(r.get("invalid_sources", 0)) for r in all_summary)

    print()
    print(f"  Alunos com baralho {args.deck_name} : {students_with_deck}")
    print(f"  Alunos sem baralho                  : {students_no_deck}")
    print(f"  Alunos sem DB encontrado             : {students_no_db}")
    print(f"  Alunos com ≥1 fonte                  : {students_with_source}")
    print(f"  Total de fontes encontradas          : {total_sources}")
    print(f"    Fontes válidas                     : {valid_src_total}")
    print(f"    Fontes inválidas                   : {invalid_src_total}")
    print(f"  Total de cartões de vocabulário      : {total_vocab_cards}")
    print()

    if flag_counts:
        print("  Flags (alunos c/ baralho):")
        for flag, count in flag_counts.most_common():
            print(f"    {flag}: {count}")
    else:
        print("  Nenhuma flag de problema detectada.")

    print()
    print(f"  Detail  → {detail_out}")
    print(f"  Summary → {summary_out}")


if __name__ == "__main__":
    main()
