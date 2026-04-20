#!/usr/bin/env python3
"""
assess_card_quality.py — Avaliador Programático de Aderência ao Método E03

Lê os cartões criados pelos alunos nos baralhos PASSAGE_E03_TIER{1,2,3} e
avalia cada cartão em 3 critérios heurísticos:

    Critério 1 — Formato da frente  (0–2 pts)
    Critério 2 — Formato do verso   (0–2 pts, regras diferentes por tier)
    Critério 3 — Evidência processo (0–2 pts): frente não copiada do texto-fonte

Score total: 0–6 → normalizado para 0–100%.

Produz dois CSVs:
    --detail-output  : uma linha por cartão avaliado
    --summary-output : uma linha por aluno (médias + flags)

Uso:
    placement_exam/.venv/bin/python \\
        placement_exam/planning_E03/scripts/assess_card_quality.py \\
        --start 2026-04-21 --end 2026-05-17 \\
        --roster exam_prep/exam_01/bases/curated_student_roster_v2.csv \\
        --account-map placement_exam/planning_E02/account_map.csv \\
        --admin-db ~/.cache/studyamigo/SNAPSHOT/admin.db \\
        --user-db-dir ~/.cache/studyamigo/SNAPSHOT/user_dbs \\
        --detail-output placement_exam/planning_E03/E03_card_quality_detail.csv \\
        --summary-output placement_exam/planning_E03/E03_card_quality_summary.csv
"""

import argparse
import csv
import difflib
import json
import re
import sqlite3
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# Textos-fonte embutidos (usados para detectar cópia direta — Critério 3)
# ─────────────────────────────────────────────────────────────────────────────

TIER1_SOURCE_TEXT = """
Brazil is famous for a special style of football. It is called jogo bonito,
which means the beautiful game. Brazilian players are creative, fast, and
exciting to watch. In 1970, Brazil showed the world what jogo bonito means.
The players moved the ball with speed and precision. Every goal was beautiful.
People still talk about that team today. Today, Vinícius Júnior and Rodrygo
play in that same style. They are fast, creative, and very dangerous attackers.
Brazilian fans love watching them. The 2026 FIFA World Cup will be in North
America. The games will be in the United States, Canada, and Mexico. Brazil is
in Group C with Morocco, Scotland, and Haiti. At the 2022 World Cup in Qatar,
Brazil lost to Croatia in the quarterfinals. That was a very painful result for
fans and players. Now, Brazil wants to do better. Head coach Carlo Ancelotti is
one of the most experienced coaches in the world. Fans are excited and ready to
cheer for A Seleção in 2026.
""".strip()

TIER2_SOURCE_TEXT = """
Few teams in football play with the creativity and style that Brazil is known
for. The concept of jogo bonito the beautiful game is deeply connected to the
Brazilian football tradition. It describes a way of playing that combines
technical skill, improvisation, and attacking flair. When Brazil plays well,
the game looks more like an art form than a sport. This philosophy was most
visible in 1970, when Brazil's squad demonstrated what jogo bonito truly means.
The players moved the ball with speed and precision, and every goal seemed
better than the last. That team is still remembered as one of the greatest in
football history. Today, attackers like Vinícius Júnior and Rodrygo carry that
tradition forward with their pace, creativity, and ability to finish under
pressure. The 2026 FIFA World Cup will be held across the United States, Canada,
and Mexico. Brazil qualified for the tournament without difficulty and entered as
one of the top favorites. The team is placed in Group C alongside Morocco,
Scotland, and Haiti. At the 2022 World Cup in Qatar, Brazil was considered one
of the strongest teams. However, they were eliminated in the quarterfinals by
Croatia. The match ended 1-1 after extra time, and Croatia won 4-2 in a penalty
shootout. That defeat was painful for players and fans alike. Now, the team is
determined to go further in 2026. Head coach Carlo Ancelotti is known for
managing elite clubs and developing talented players. With his experience and
Brazil's depth of quality, expectations are high. Fans around the world believe
this could finally be A Seleção's year to claim a sixth World Cup title and
prove that the beautiful game still belongs to Brazil.
""".strip()

TIER3_SOURCE_TEXT = """
Demis Hassabis was a child chess prodigy who became a master at the age of
thirteen. Rather than pursuing a career in professional chess, he turned his
attention to a far more ambitious goal: understanding intelligence itself. He
studied neuroscience at Cambridge, convinced that the brain held the key to
building truly intelligent machines. That conviction led him to co-found
DeepMind in 2010, an AI research company later acquired by Google. His
longstanding ambition was to use artificial intelligence to accelerate
scientific discovery. DeepMind's early breakthrough came with AlphaGo, an AI
system that defeated world champion Lee Sedol at the ancient board game of Go
in 2016. One of AlphaGo's moves move 37 was so unexpected that it shook Sedol
to his core. Commentators initially thought it was a mistake. It turned out to
be a stroke of genius that no human player would have considered. The victory
demonstrated that AI could develop strategies that went far beyond anything its
creators had explicitly programmed. But Hassabis never forgot a simpler game he
had played years earlier a crowdsourced puzzle called Fold It, in which ordinary
players competed to fold virtual proteins into their correct three-dimensional
shapes. Trained biologists were being outperformed by amateur gamers who relied
on intuition rather than expertise. Hassabis was fascinated. He wondered whether
an AI system could learn to mimic that intuition at scale. The result was
AlphaFold, a project Hassabis initiated to solve one of biology's most stubborn
unsolved problems: predicting the three-dimensional structure of a protein from
its amino acid sequence alone. For over sixty years, tens of thousands of
biologists had painstakingly determined the structure of around 150,000 proteins
using expensive laboratory techniques. AlphaFold's second version, released in
2021, predicted the structure of over 200 million proteins essentially every
protein known to exist in nature in a matter of months. The implications were
staggering. Protein structure determines function, and understanding function is
the foundation of drug discovery. Researchers working on diseases from malaria
to Parkinson's suddenly had access to structural data that would previously have
taken entire careers to obtain. AlphaFold's database was made freely available
to the scientific community, and within a year it had been accessed by over one
million researchers in 190 countries. In 2024, Demis Hassabis was awarded the
Nobel Prize in Chemistry alongside John Jumper, who led the AlphaFold 2 project,
and David Baker, a pioneer in computational protein design. The Nobel Committee
described the work as having unlocked the secret of proteins. For Hassabis, the
prize confirmed something he had believed since his days as a teenager playing
chess: that intelligence, whether human or artificial, is most powerful when it
is directed at problems that truly matter.
""".strip()

SOURCE_TEXTS = {
    1: TIER1_SOURCE_TEXT,
    2: TIER2_SOURCE_TEXT,
    3: TIER3_SOURCE_TEXT,
}

# Pre-split source texts into sentences for similarity comparison
def _sentences(text: str) -> List[str]:
    """Split text into sentences (rough split on period/exclamation/question)."""
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip().lower() for p in parts if len(p.strip()) > 10]

SOURCE_SENTENCES: Dict[int, List[str]] = {
    tier: _sentences(text) for tier, text in SOURCE_TEXTS.items()
}

# Regex for detecting [UPPERCASE_WORD] cloze marker
RE_CLOZE = re.compile(r'\[[A-ZÁÉÍÓÚÀÂÊÔÃÕÇ][A-ZÁÉÍÓÚÀÂÊÔÃÕÇ\s]+\]')

# Regex for grammatical class markers (n.), (v.), (adj.), (adv.), (prep.)
RE_GRAM_CLASS = re.compile(r'\((n|v|adj|adv|prep)\.\)', re.IGNORECASE)

# Regex for = sign used as translation separator (Tier 1 / Tier 2 pattern)
RE_EQUALS = re.compile(r'\S+\s*=\s*\S+')

# ─────────────────────────────────────────────────────────────────────────────
# Scoring functions
# ─────────────────────────────────────────────────────────────────────────────

def score_front(front: str) -> Tuple[int, str]:
    """
    Critério 1: Formato da frente.
    2 — frase ≥ 4 palavras + [MAIÚSCULO] marcado
    1 — frase ≥ 4 palavras mas sem [MAIÚSCULO]
    0 — menos de 4 palavras (palavra isolada)
    """
    words = front.split()
    has_cloze = bool(RE_CLOZE.search(front))

    if len(words) >= 4 and has_cloze:
        return 2, "frase contextualizada com [MAIÚSCULO]"
    if len(words) >= 4:
        return 1, "frase presente mas sem marcação [MAIÚSCULO]"
    return 0, f"muito curta ({len(words)} palavra(s)) — parece palavra isolada"


def score_back_tier1(back: str) -> Tuple[int, str]:
    """
    Tier 1: verso deve ter 'palavra = tradução'.
    2 — contém padrão X = Y
    1 — texto não-vazio mas sem =
    0 — vazio ou só espaços
    """
    stripped = back.strip()
    if not stripped:
        return 0, "verso vazio"
    if RE_EQUALS.search(stripped):
        return 2, "padrão 'palavra = tradução' encontrado"
    return 1, "verso preenchido mas sem separador '='"


def score_back_tier2(back: str) -> Tuple[int, str]:
    """
    Tier 2: verso deve ter classe gramatical (n.)/(v.)/(adj.) E ☞.
    2 — ambos presentes
    1 — apenas um dos dois
    0 — nenhum
    """
    has_class = bool(RE_GRAM_CLASS.search(back))
    has_arrow = "☞" in back

    if has_class and has_arrow:
        return 2, "classe gramatical + ☞ colocação"
    if has_class:
        return 1, "classe gramatical presente mas sem ☞"
    if has_arrow:
        return 1, "☞ presente mas sem classe gramatical"
    return 0, "sem classe gramatical e sem ☞"


def score_back_tier3(back: str) -> Tuple[int, str]:
    """
    Tier 3: verso deve ter ☞ E definição em inglês (não tradução 'palavra = PT').
    2 — ☞ presente E sem padrão 'palavra = tradução_PT'
    1 — ☞ presente MAS com padrão 'palavra = tradução_PT' (usou formato T2)
    0 — sem ☞
    """
    has_arrow = "☞" in back
    has_pt_translation = bool(RE_EQUALS.search(back))

    if has_arrow and not has_pt_translation:
        return 2, "☞ colocação + definição em inglês (sem tradução PT da palavra)"
    if has_arrow and has_pt_translation:
        return 1, "☞ presente mas com tradução PT — deveria ser definição em inglês"
    return 0, "sem ☞ colocação"


def score_back(back: str, tier: int) -> Tuple[int, str]:
    if tier == 1:
        return score_back_tier1(back)
    if tier == 2:
        return score_back_tier2(back)
    return score_back_tier3(back)


def score_process(front: str, tier: int) -> Tuple[int, str]:
    """
    Critério 3: frente não foi copiada diretamente do texto-fonte.
    Compara normalização da frente com cada sentença do texto usando
    difflib.SequenceMatcher.

    2 — similaridade máxima < 0.60 (criou frase própria)
    1 — similaridade entre 0.60 e 0.84 (adaptou mas pouco)
    0 — similaridade ≥ 0.85 (copiou diretamente)
    """
    sentences = SOURCE_SENTENCES.get(tier, [])
    if not sentences:
        return 2, "sem texto-fonte para comparar"

    front_norm = front.strip().lower()
    # Remove cloze markers for comparison
    front_norm = re.sub(r'\[([^\]]+)\]', r'\1', front_norm)

    max_ratio = 0.0
    for sent in sentences:
        ratio = difflib.SequenceMatcher(None, front_norm, sent).ratio()
        if ratio > max_ratio:
            max_ratio = ratio

    if max_ratio >= 0.85:
        return 0, f"alta similaridade com texto-fonte ({max_ratio:.2f}) — provável cópia"
    if max_ratio >= 0.60:
        return 1, f"similaridade moderada ({max_ratio:.2f}) — pouca adaptação"
    return 2, f"frase original ({max_ratio:.2f} de similaridade)"


def assess_card(front: str, back: str, tier: int) -> Dict:
    """Avaliar um cartão. Retorna dict com scores e razões."""
    s_front, r_front = score_front(front)
    s_back, r_back = score_back(back, tier)
    s_proc, r_proc = score_process(front, tier)

    total = s_front + s_back + s_proc
    pct = round(total / 6 * 100, 1)

    return {
        "score_front": s_front,
        "reason_front": r_front,
        "score_back": s_back,
        "reason_back": r_back,
        "score_process": s_proc,
        "reason_process": r_proc,
        "total_score": total,
        "pct_score": pct,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Database helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def load_users(admin_db: Path) -> Dict[int, Dict]:
    """Return {user_id: {'username': …, 'name': …}}."""
    if not admin_db.exists():
        sys.exit(f"admin.db não encontrado em {admin_db}")
    conn = sqlite3.connect(str(admin_db))
    rows = conn.execute("SELECT user_id, username, name FROM users").fetchall()
    conn.close()
    return {r[0]: {"username": r[1], "name": r[2]} for r in rows}


def find_user_db(user_dbs_dir: Path, user_id: int) -> Optional[Path]:
    p = user_dbs_dir / f"user_{user_id}.db"
    return p if p.exists() else None


def load_account_map(csv_path: Optional[Path]) -> Dict[str, str]:
    """
    Returns {secondary_username_lower: primary_roster_name}.
    Same format as grade_exercise_v2.py — CSV with columns username, roster_name.
    """
    if csv_path is None or not csv_path.exists():
        return {}
    mapping: Dict[str, str] = {}
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            username = (row.get("username") or row.get("secondary_username") or "").strip()
            roster_name = (row.get("roster_name") or row.get("primary_name") or "").strip()
            if username and roster_name:
                mapping[username.lower()] = roster_name
    return mapping


def _normalise(s: str) -> str:
    """Lowercase, strip accents, remove punctuation — for fuzzy name matching."""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    return " ".join(s.split())


def match_roster_to_admin(
    roster: List[Dict], users: Dict[int, Dict]
) -> None:
    """
    Mutate roster entries in-place, setting 'user_id' to the best-matching
    admin DB user via fuzzy name comparison (same logic as grade_exercise_v2).
    """
    THRESHOLD = 0.55

    admin_norm_to_uids: Dict[str, List[int]] = defaultdict(list)
    for uid, info in users.items():
        admin_norm_to_uids[_normalise(info["name"])].append(uid)

    admin_slots = list(admin_norm_to_uids.keys())

    triples: List[Tuple[float, int, str]] = []
    for i, student in enumerate(roster):
        target = _normalise(student["name"])
        for slot in admin_slots:
            score = difflib.SequenceMatcher(None, target, slot).ratio()
            if score >= THRESHOLD:
                triples.append((score, i, slot))

    triples.sort(key=lambda t: -t[0])
    assigned_roster: set = set()
    assigned_slots: set = set()

    for score, i, slot in triples:
        if i in assigned_roster or slot in assigned_slots:
            continue
        uids = admin_norm_to_uids[slot]
        roster[i]["user_id"] = uids[0]
        roster[i]["_matched_uids"] = uids
        assigned_roster.add(i)
        assigned_slots.add(slot)


def apply_account_map(
    roster: List[Dict],
    users: Dict[int, Dict],
    account_map: Dict[str, str],
) -> None:
    """
    For secondary usernames in account_map, find the admin uid and append it
    to the _matched_uids of the corresponding roster student.
    """
    username_to_uid = {v["username"].lower(): k for k, v in users.items()}
    roster_norm_to_idx = {_normalise(s["name"]): i for i, s in enumerate(roster)}

    for username_lower, roster_name in account_map.items():
        uid = username_to_uid.get(username_lower)
        if uid is None:
            continue
        target_norm = _normalise(roster_name)
        idx = roster_norm_to_idx.get(target_norm)
        if idx is None:
            continue
        student = roster[idx]
        if student["user_id"] is None:
            student["user_id"] = uid
        matched = student.setdefault("_matched_uids", [student["user_id"]])
        if uid not in matched:
            matched.append(uid)


def load_roster(csv_path: Path) -> List[Dict]:
    """
    Returns list of {student_id, name, tier, user_id, _matched_uids}.
    Accepts column names from curated_student_roster_v2.csv: ID, Nome, Suggested Tier.
    """
    if not csv_path.exists():
        sys.exit(f"Roster não encontrado em {csv_path}")

    roster: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid_raw = (
                row.get("student_id") or row.get("id") or row.get("ID") or ""
            ).strip()
            if not sid_raw.isdigit():
                continue
            sid = int(sid_raw)
            tier_raw = (
                row.get("tier") or row.get("Tier") or row.get("Suggested Tier") or ""
            ).strip()
            tier_match = re.search(r'(\d)', tier_raw)
            tier = int(tier_match.group(1)) if tier_match else None
            roster.append({
                "student_id": sid,
                "name": (
                    row.get("name") or row.get("Nome") or row.get("NAME") or ""
                ).strip(),
                "tier": tier,
                "user_id": None,
                "_matched_uids": [],
            })
    return roster


def get_deck_id(conn: sqlite3.Connection, deck_name: str) -> Optional[int]:
    """Parse col.decks JSON and return the deck id for the given name."""
    row = conn.execute("SELECT decks FROM col LIMIT 1").fetchone()
    if not row:
        return None
    try:
        decks = json.loads(row[0])
    except json.JSONDecodeError:
        return None
    for did_str, deck in decks.items():
        if deck.get("name", "") == deck_name:
            return int(did_str)
    return None


def get_cards_for_deck(
    conn: sqlite3.Connection,
    did: int,
    start_ms: int,
    end_ms: int,
) -> List[Tuple[int, str, str]]:
    """
    Return list of (card_id, front, back) for cards in the given deck
    created within [start_ms, end_ms].
    notes.flds uses U+001F (\\x1f) as field separator; first field = front.
    """
    rows = conn.execute(
        """
        SELECT c.id, n.flds
        FROM cards c
        JOIN notes n ON c.nid = n.id
        WHERE c.did = ? AND c.id BETWEEN ? AND ?
        ORDER BY c.id
        """,
        (did, start_ms, end_ms),
    ).fetchall()

    cards = []
    for card_id, flds in rows:
        parts = flds.split("\x1f")
        front = parts[0].strip() if len(parts) > 0 else ""
        back = parts[1].strip() if len(parts) > 1 else ""
        # Strip basic HTML tags that StudyAmigo may wrap fields in
        front = re.sub(r'<[^>]+>', '', front).strip()
        back = re.sub(r'<[^>]+>', '', back).strip()
        cards.append((card_id, front, back))
    return cards


# ─────────────────────────────────────────────────────────────────────────────
# Per-student assessment
# ─────────────────────────────────────────────────────────────────────────────

def assess_student_db(
    db_path: Path,
    student_id: int,
    name: str,
    tier: int,
    start_ms: int,
    end_ms: int,
    deck_prefix: str = "PASSAGE_E03",
) -> List[Dict]:
    """
    Open one student DB, find their {deck_prefix}_TIER{tier} deck,
    and assess every card in it. Returns list of row dicts.
    """
    deck_name = f"{deck_prefix}_TIER{tier}"
    results = []

    try:
        conn = sqlite3.connect(str(db_path))
    except Exception as e:
        print(f"  Aviso: não foi possível abrir {db_path}: {e}", file=sys.stderr)
        return results

    try:
        did = get_deck_id(conn, deck_name)
        if did is None:
            # Deck not found — student hasn't created the deck yet
            return results

        cards = get_cards_for_deck(conn, did, start_ms, end_ms)
        for card_id, front, back in cards:
            assessment = assess_card(front, back, tier)
            results.append({
                "student_id": student_id,
                "name": name,
                "tier": tier,
                "deck": deck_name,
                "card_id": card_id,
                "front": front,
                "back": back,
                **assessment,
            })
    except Exception as e:
        print(f"  Aviso: erro ao avaliar {db_path}: {e}", file=sys.stderr)
    finally:
        conn.close()

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Output
# ─────────────────────────────────────────────────────────────────────────────

DETAIL_FIELDS = [
    "student_id", "name", "tier", "deck", "card_id", "front", "back",
    "score_front", "reason_front",
    "score_back", "reason_back",
    "score_process", "reason_process",
    "total_score", "pct_score",
]

SUMMARY_FIELDS = [
    "student_id", "name", "tier",
    "cards_assessed",
    "mean_score_front", "mean_score_back", "mean_score_process",
    "mean_total", "mean_pct",
    "low_quality_cards", "flag_mostly_copied",
]


def build_summary(student_id: int, name: str, tier: int, rows: List[Dict]) -> Dict:
    """Aggregate card-level rows into one summary row per student."""
    if not rows:
        return {
            "student_id": student_id,
            "name": name,
            "tier": tier,
            "cards_assessed": 0,
            "mean_score_front": "",
            "mean_score_back": "",
            "mean_score_process": "",
            "mean_total": "",
            "mean_pct": "",
            "low_quality_cards": 0,
            "flag_mostly_copied": "",
        }

    fronts = np.array([r["score_front"] for r in rows], dtype=float)
    backs = np.array([r["score_back"] for r in rows], dtype=float)
    procs = np.array([r["score_process"] for r in rows], dtype=float)
    totals = np.array([r["total_score"] for r in rows], dtype=float)
    pcts = np.array([r["pct_score"] for r in rows], dtype=float)

    low_quality = int(np.sum(pcts < 33.4))
    mostly_copied = bool(np.mean(procs == 0) > 0.5)

    return {
        "student_id": student_id,
        "name": name,
        "tier": tier,
        "cards_assessed": len(rows),
        "mean_score_front": round(float(np.mean(fronts)), 2),
        "mean_score_back": round(float(np.mean(backs)), 2),
        "mean_score_process": round(float(np.mean(procs)), 2),
        "mean_total": round(float(np.mean(totals)), 2),
        "mean_pct": round(float(np.mean(pcts)), 1),
        "low_quality_cards": low_quality,
        "flag_mostly_copied": "COPIA" if mostly_copied else "",
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Avalia aderência ao método dos cartões de E03 (PASSAGE_E03_TIER{1,2,3})."
    )
    p.add_argument("--start", required=True, help="Data de início ISO (YYYY-MM-DD)")
    p.add_argument("--end", required=True, help="Data de fim ISO (YYYY-MM-DD)")
    p.add_argument(
        "--roster", required=True, type=Path,
        help="CSV do roster com colunas student_id, name, tier",
    )
    p.add_argument(
        "--account-map", type=Path, default=None,
        help="CSV de contas secundárias: secondary_username,primary_student_id",
    )
    p.add_argument("--admin-db", required=True, type=Path, help="Caminho para admin.db")
    p.add_argument("--user-db-dir", required=True, type=Path, help="Diretório com user_<id>.db")
    p.add_argument(
        "--detail-output", type=Path,
        default=Path("E03_card_quality_detail.csv"),
        help="CSV detalhado (uma linha por cartão)",
    )
    p.add_argument(
        "--summary-output", type=Path,
        default=Path("E03_card_quality_summary.csv"),
        help="CSV resumo (uma linha por aluno)",
    )
    p.add_argument(
        "--deck-prefix", default="PASSAGE_E03",
        help="Prefixo do nome do baralho a avaliar (padrão: PASSAGE_E03). "
             "Use PASSAGE_E02 para testar contra snapshot de E02.",
    )
    return p.parse_args()


def parse_date(date_str: str) -> datetime:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        sys.exit(f"Formato de data inválido: {date_str!r}. Use YYYY-MM-DD.")


def main() -> None:
    args = parse_args()

    start_dt = parse_date(args.start)
    end_dt = parse_date(args.end).replace(hour=23, minute=59, second=59)
    start_ms = _ms(start_dt)
    end_ms = _ms(end_dt)

    print(f"\n  Janela: {args.start} → {args.end}")

    # Load data sources
    users = load_users(args.admin_db)
    roster = load_roster(args.roster)
    account_map = load_account_map(args.account_map)

    # Resolve roster names → admin user_ids (fuzzy name match)
    match_roster_to_admin(roster, users)
    apply_account_map(roster, users, account_map)

    print(f"  Roster: {len(roster)} alunos | admin.db: {len(users)} usuários")

    all_detail_rows: List[Dict] = []
    all_summary_rows: List[Dict] = []

    students_assessed = 0
    students_no_deck = 0
    students_no_db = 0

    for student in sorted(roster, key=lambda s: s["student_id"]):
        student_id = student["student_id"]
        name = student["name"]
        tier = student["tier"]

        if tier not in (1, 2, 3):
            continue

        # Try all matched admin user_ids (primary + secondary accounts)
        matched_uids: List[int] = student.get("_matched_uids") or (
            [student["user_id"]] if student["user_id"] else []
        )

        db_path: Optional[Path] = None
        for uid in matched_uids:
            candidate = find_user_db(args.user_db_dir, uid)
            if candidate is not None:
                db_path = candidate
                break

        if db_path is None:
            students_no_db += 1
            all_summary_rows.append(build_summary(student_id, name, tier, []))
            continue

        rows = assess_student_db(db_path, student_id, name, tier, start_ms, end_ms,
                                  deck_prefix=args.deck_prefix)

        if not rows:
            students_no_deck += 1
        else:
            students_assessed += 1

        all_detail_rows.extend(rows)
        all_summary_rows.append(build_summary(student_id, name, tier, rows))

    # Write detail CSV
    args.detail_output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.detail_output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=DETAIL_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_detail_rows)

    # Write summary CSV (sort by tier, then mean_pct desc)
    all_summary_rows.sort(
        key=lambda r: (r["tier"] or 99, -(r["mean_pct"] if isinstance(r["mean_pct"], float) else 0))
    )
    with open(args.summary_output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_summary_rows)

    # Print summary to stdout
    total_cards = len(all_detail_rows)
    mean_pct_all = (
        round(float(np.mean([r["pct_score"] for r in all_detail_rows])), 1)
        if all_detail_rows else 0.0
    )
    low_quality_total = sum(1 for r in all_detail_rows if r["pct_score"] < 33.4)
    copy_flags = sum(1 for r in all_summary_rows if r.get("flag_mostly_copied") == "COPIA")

    print(f"\n  Alunos com baralho avaliado : {students_assessed}")
    print(f"  Alunos sem baralho PASSAGE  : {students_no_deck}")
    print(f"  Alunos sem DB encontrado    : {students_no_db}")
    print(f"  Total de cartões avaliados  : {total_cards}")
    print(f"  Score médio de aderência    : {mean_pct_all}%")
    print(f"  Cartões de baixa qualidade  : {low_quality_total} (<33%)")
    print(f"  Alunos flag COPIA           : {copy_flags}")
    print(f"\n  Detail  → {args.detail_output}")
    print(f"  Summary → {args.summary_output}\n")


if __name__ == "__main__":
    main()
