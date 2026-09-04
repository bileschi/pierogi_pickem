"""Database persistence and player management for Pierogi Pick'em.

Uses SQLite with Write-Ahead Logging (WAL) for safe concurrent reads/writes.
Maintains an append-only event log of all pick actions for auditability.
"""

import os
import secrets
import sqlite3
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

DEFAULT_PLAYERS = [
    {"id": "smb", "display_name": "Stan"},
    {"id": "slb", "display_name": "Steve"},
    {"id": "sue", "display_name": "Sue"},
    {"id": "jean", "display_name": "Jean"},
    {"id": "morgan", "display_name": "Morgan"},
    {"id": "adam", "display_name": "Adam"},
]


def get_db_path() -> str:
    """Resolves the path to picks.db."""
    if "PIEROGI_DB_PATH" in os.environ:
        return os.environ["PIEROGI_DB_PATH"]
    # Production path on Dreamhost
    prod_path = "/home/bileschi_2016/proj/pierogi_pickem/picks.db"
    if os.path.exists(os.path.dirname(prod_path)):
        return prod_path
    # Local dev fallback
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "picks.db")


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Returns a SQLite connection configured with WAL mode and timeout."""
    path = db_path or get_db_path()
    conn = sqlite3.connect(path, timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Creates schema and seeds initial league players if not present."""
    conn = get_connection(db_path)
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                token TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pick_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                player_id TEXT NOT NULL,
                season TEXT NOT NULL,
                week INTEGER NOT NULL,
                game_id TEXT NOT NULL,
                team_pick TEXT NOT NULL,
                ip_address TEXT,
                FOREIGN KEY (player_id) REFERENCES players (id)
            );
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_pick_events_lookup
            ON pick_events (season, week, player_id, game_id, id);
        """)

        # Seed players if missing
        now_iso = datetime.now(timezone.utc).isoformat()
        for p in DEFAULT_PLAYERS:
            existing = conn.execute(
                "SELECT id FROM players WHERE id = ?", (p["id"],)
            ).fetchone()
            if not existing:
                token = secrets.token_urlsafe(16)
                conn.execute(
                    "INSERT INTO players (id, display_name, token, created_at) VALUES (?, ?, ?, ?)",
                    (p["id"], p["display_name"], token, now_iso),
                )
    conn.close()


def get_player(player_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves player record by player_id."""
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT id, display_name, token, created_at FROM players WHERE id = ?",
            (player_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_player_by_token(token: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves player record by secret token."""
    if not token:
        return None
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT id, display_name, token, created_at FROM players WHERE token = ?",
            (token,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_players(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lists all registered players."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT id, display_name, token, created_at FROM players ORDER BY id"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def add_player(player_id: str, display_name: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    """Adds a new player or returns existing player."""
    conn = get_connection(db_path)
    with conn:
        existing = conn.execute(
            "SELECT id, display_name, token, created_at FROM players WHERE id = ?",
            (player_id,),
        ).fetchone()
        if existing:
            conn.close()
            return dict(existing)
        token = secrets.token_urlsafe(16)
        now_iso = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT INTO players (id, display_name, token, created_at) VALUES (?, ?, ?, ?)",
            (player_id, display_name, token, now_iso),
        )
    conn.close()
    return {"id": player_id, "display_name": display_name, "token": token, "created_at": now_iso}


def save_pick(
    player_id: str,
    season: str,
    week: int,
    game_id: str,
    team_pick: str,
    ip_address: Optional[str] = None,
    db_path: Optional[str] = None,
) -> int:
    """Appends a pick event to the log. Returns the new event id."""
    conn = get_connection(db_path)
    now_iso = datetime.now(timezone.utc).isoformat()
    with conn:
        cursor = conn.execute(
            """
            INSERT INTO pick_events (timestamp, player_id, season, week, game_id, team_pick, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (now_iso, player_id, season, week, str(game_id), str(team_pick), ip_address),
        )
        event_id = cursor.lastrowid
    conn.close()
    return event_id


def get_active_picks(
    season: str,
    week: Optional[int] = None,
    player_id: Optional[str] = None,
    db_path: Optional[str] = None,
) -> Dict[str, Dict[str, str]]:
    """Returns the latest pick for each player and game: {player_id: {game_id: team_pick}}.

    If week is specified, limits to that week.
    If player_id is specified, limits to that player.
    """
    conn = get_connection(db_path)
    try:
        conditions = ["season = ?"]
        params: List[Any] = [season]
        if week is not None:
            conditions.append("week = ?")
            params.append(week)
        if player_id is not None:
            conditions.append("player_id = ?")
            params.append(player_id)

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT pe.player_id, pe.game_id, pe.team_pick
            FROM pick_events pe
            INNER JOIN (
                SELECT player_id, game_id, MAX(id) as max_id
                FROM pick_events
                WHERE {where_clause}
                GROUP BY player_id, game_id
            ) latest ON pe.id = latest.max_id
        """
        rows = conn.execute(query, params).fetchall()
        result: Dict[str, Dict[str, str]] = {}
        for r in rows:
            p_id = r["player_id"]
            if p_id not in result:
                result[p_id] = {}
            result[p_id][str(r["game_id"])] = r["team_pick"]
        return result
    finally:
        conn.close()


def print_magic_links(base_url: str = "https://bileschi.com/nfl/pick.html", db_path: Optional[str] = None) -> None:
    """Utility to print personalized links for all players."""
    players = list_players(db_path)
    print("\n--- Pierogi Pick'em Magic Links ---")
    for p in players:
        link = f"{base_url}?u={p['id']}&k={p['token']}"
        print(f"{p['display_name']} ({p['id']}):\n  {link}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage Pierogi Pick'em SQLite database and player tokens.")
    parser.add_argument("--add", nargs=2, metavar=("ID", "NAME"), help="Add a new player: --add dave 'Dave'")
    parser.add_argument("--links", action="store_true", help="Print all player magic links")
    args = parser.parse_args()

    init_db()
    if args.add:
        p_id, p_name = args.add[0].lower(), args.add[1]
        player = add_player(p_id, p_name)
        print(f"Added player: {player['display_name']} ({player['id']})")
        print(f"Magic Link: https://bileschi.com/nfl/pick.html?u={player['id']}&k={player['token']}")
    else:
        print_magic_links()
