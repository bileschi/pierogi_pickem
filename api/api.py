#!/usr/bin/env python3
"""Lightweight CGI API for Pierogi Pick'em mobile picking.

Handles user authentication via secret tokens, serves weekly game matchups
with live kickoff lock enforcement, and records picks into the append-only SQLite log.
"""

import csv
import json
import os
import sys
import time
import urllib.parse
from datetime import datetime, timezone

# Ensure project root is in sys.path
PROJECT_DIR = os.environ.get(
    "PIEROGI_PROJ_DIR",
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
if not os.path.exists(os.path.join(PROJECT_DIR, "db.py")):
    prod_path = "/home/bileschi_2016/proj/pierogi_pickem"
    if os.path.exists(prod_path):
        PROJECT_DIR = prod_path

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import db

try:
    from current_season import FOOTBALL_SEASON
except ImportError:
    FOOTBALL_SEASON = "2026_2027"

try:
    from players import TEAM_CITY_TO_NAME
except ImportError:
    TEAM_CITY_TO_NAME = {}


def send_response(data: dict, status: int = 200) -> None:
    """Outputs HTTP response headers and JSON body for CGI."""
    status_msg = "200 OK" if status == 200 else ("400 Bad Request" if status == 400 else ("401 Unauthorized" if status == 401 else f"{status} Error"))
    print(f"Status: {status_msg}")
    print("Content-Type: application/json; charset=utf-8")
    print("Cache-Control: no-store, no-cache, must-revalidate")
    print("Access-Control-Allow-Origin: *")
    print("Access-Control-Allow-Methods: GET, POST, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type")
    print()
    print(json.dumps(data))
    sys.exit(0)


def load_season_games(season: str) -> list:
    """Loads games for the given season from games.csv."""
    games_csv = os.path.join(PROJECT_DIR, season, "games.csv")
    if not os.path.exists(games_csv):
        return []
    with open(games_csv, mode="r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def format_kickoff(prop_date_str: str) -> str:
    """Formats epoch timestamp in milliseconds to human-readable string."""
    try:
        epoch_sec = int(prop_date_str) / 1000.0
        # Convert to local time format
        dt = datetime.fromtimestamp(epoch_sec, tz=timezone.utc)
        return dt.strftime("%a %b %d · %-I:%M %p UTC")
    except Exception:
        return ""


def handle_get() -> None:
    query_string = os.environ.get("QUERY_STRING", "")
    params = urllib.parse.parse_qs(query_string)

    user_id = params.get("u", [""])[0].strip()
    token = params.get("k", [""])[0].strip()
    requested_week = params.get("week", [""])[0].strip()
    season = params.get("season", [FOOTBALL_SEASON])[0].strip()

    # Authenticate player
    player = None
    if token:
        player = db.get_player_by_token(token)
    elif user_id:
        p = db.get_player(user_id)
        # If token query was not supplied but user_id was, require token
        player = None

    if not player or (user_id and player["id"] != user_id):
        send_response({
            "authenticated": False,
            "error": "Please access using your personal magic link.",
        }, status=401)

    games = load_season_games(season)
    available_weeks = sorted(list(set(int(g["week"]) for g in games if g.get("week"))))
    if not available_weeks:
        available_weeks = list(range(1, 19))

    # Determine current week
    current_week = available_weeks[0] if available_weeks else 1
    now_ms = time.time() * 1000
    for w in available_weeks:
        week_games = [g for g in games if g.get("week") == str(w)]
        has_future_games = any(
            float(g["prop_date"]) > now_ms for g in week_games if g.get("prop_date")
        )
        if has_future_games:
            current_week = w
            break

    selected_week = int(requested_week) if requested_week.isdigit() else current_week

    # Filter games for selected week
    week_games_raw = [g for g in games if g.get("week") == str(selected_week)]

    # Fetch player's current active picks for this week
    active_picks_by_player = db.get_active_picks(season, week=selected_week, player_id=player["id"])
    player_picks = active_picks_by_player.get(player["id"], {})

    formatted_games = []
    for g in week_games_raw:
        prop_date = int(g["prop_date"]) if g.get("prop_date") else 0
        is_locked = now_ms >= prop_date if prop_date > 0 else False

        line_str = g.get("home_line", "")
        if line_str and not line_str.startswith("-") and not line_str.startswith("+"):
            line_str = "+" + line_str

        formatted_games.append({
            "game_id": g.get("game_id"),
            "week": selected_week,
            "away_team": g.get("away_team"),
            "away_team_name": TEAM_CITY_TO_NAME.get(g.get("away_team"), g.get("away_team")),
            "away_logo": f"images2/nfl/{g.get('away_team')}.png",
            "home_team": g.get("home_team"),
            "home_team_name": TEAM_CITY_TO_NAME.get(g.get("home_team"), g.get("home_team")),
            "home_logo": f"images2/nfl/{g.get('home_team')}.png",
            "home_line": line_str,
            "prop_date": prop_date,
            "kickoff_str": format_kickoff(g.get("prop_date", "0")),
            "is_locked": is_locked,
            "home_score": g.get("home_score", ""),
            "away_score": g.get("away_score", ""),
            "bet_win_key": g.get("bet_win_key", "not_decided"),
        })

    send_response({
        "authenticated": True,
        "player": {
            "id": player["id"],
            "display_name": player["display_name"],
        },
        "season": season,
        "current_week": current_week,
        "selected_week": selected_week,
        "available_weeks": available_weeks,
        "games": formatted_games,
        "picks": player_picks,
    })


def handle_post() -> None:
    try:
        content_length = int(os.environ.get("CONTENT_LENGTH", 0))
        raw_body = sys.stdin.read(content_length) if content_length > 0 else ""
    except Exception:
        raw_body = ""

    payload = {}
    if raw_body:
        try:
            payload = json.loads(raw_body)
        except Exception:
            parsed = urllib.parse.parse_qs(raw_body)
            payload = {k: v[0] for k, v in parsed.items()}

    user_id = payload.get("u", "").strip()
    token = payload.get("k", "").strip()
    game_id = str(payload.get("game_id", "")).strip()
    team_pick = str(payload.get("team", "")).strip().upper()
    season = payload.get("season", FOOTBALL_SEASON).strip()

    # Authenticate player
    if not token:
        send_response({"success": False, "error": "Missing secret token"}, status=401)

    player = db.get_player_by_token(token)
    if not player or (user_id and player["id"] != user_id):
        send_response({"success": False, "error": "Unauthorized"}, status=401)

    # Validate game exists
    games = load_season_games(season)
    matching_game = next((g for g in games if str(g.get("game_id")) == game_id), None)
    if not matching_game:
        send_response({"success": False, "error": "Game not found"}, status=400)

    # Check kickoff time locking
    prop_date = int(matching_game.get("prop_date", "0"))
    now_ms = time.time() * 1000
    if prop_date > 0 and now_ms >= prop_date:
        send_response({
            "success": False,
            "error": "Picks for this game locked at kickoff.",
            "is_locked": True,
        }, status=400)

    # Validate team pick
    home_team = matching_game.get("home_team", "").upper()
    away_team = matching_game.get("away_team", "").upper()
    if team_pick not in (home_team, away_team):
        send_response({
            "success": False,
            "error": f"Invalid team pick. Must be {away_team} or {home_team}."
        }, status=400)

    week = int(matching_game.get("week", 1))
    ip_address = os.environ.get("REMOTE_ADDR")

    event_id = db.save_pick(
        player_id=player["id"],
        season=season,
        week=week,
        game_id=game_id,
        team_pick=team_pick,
        ip_address=ip_address,
    )

    send_response({
        "success": True,
        "event_id": event_id,
        "game_id": game_id,
        "team": team_pick,
        "week": week,
        "saved_at": datetime.now(timezone.utc).isoformat(),
    })


def main() -> None:
    method = os.environ.get("REQUEST_METHOD", "GET").upper()
    if method == "OPTIONS":
        send_response({"status": "ok"})
    elif method == "POST":
        handle_post()
    else:
        handle_get()


if __name__ == "__main__":
    main()
