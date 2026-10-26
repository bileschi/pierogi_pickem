import os
import games_col_keys


# I got these ids from the espn site by poking around at the network tab.

# 2023_2024
# ESPN_PLAYER_IDS = {
#   SMB_PICK_KEY: '72520e10-4b6e-11ee-a4c8-27e5ad8f3bbd',
#   SLB_PICK_KEY: '385fbc90-4b71-11ee-85db-77e9d8fab8a0',
#   SUE_PICK_KEY: '4d1a4380-4bfd-11ee-b3fb-11aa5673265b',
#   JEAN_PICK_KEY: '5d03d350-4c3a-11ee-8382-91995701af39',
# }

# 2024_2025
# PLAYER_IDS = [
#   JEAN_PICK_KEY,
#   MORGAN_PICK_KEY,
#   SLB_PICK_KEY,
#   SMB_PICK_KEY,
#   SUE_PICK_KEY,
#   ADAM_PICK_KEY,
# ]
# 2025_2026
PLAYER_IDS = [
  games_col_keys.JEAN_PICK_KEY,
  games_col_keys.MORGAN_PICK_KEY,
  games_col_keys.SLB_PICK_KEY,
  games_col_keys.SMB_PICK_KEY,
  games_col_keys.SUE_PICK_KEY,
  games_col_keys.ADAM_PICK_KEY,
  games_col_keys.CONSTANCE_PICK_KEY,
  games_col_keys.MAX_PICK_KEY,
]

PLAYERS = ['smb', 'slb', 'sue', 'jean', 'morgan', 'adam', 'constance', 'max']

PLAYER_DISPLAY_NAMES = {
    'smb': 'Stan M',
    'slb': 'Stan L',
    'sue': 'Sue',
    'jean': 'Jean',
    'morgan': 'Morgan',
    'adam': 'Adam',
    'constance': 'Constance',
    'max': 'Max',
}


def player_has_manual_pick(games=None, player_id='max') -> bool:
    """Checks whether a player has ever made a manual (non-default) pick.

    A pick is considered manual if it was made directly by the user on the site (SITE),
    submitted via manual picks (MANUAL), or fetched from ESPN (ESPN) -- anything other
    than the automated fallback (DEFAULT).
    """
    # 1. Check games list if provided
    if games:
        pick_col = f"{player_id}_pick"
        for game in games:
            val = ""
            if isinstance(game, dict):
                val = game.get(pick_col) or game.get(player_id) or ""
            elif hasattr(game, "picks"):
                val = game.picks.get(pick_col) or game.picks.get(player_id) or ""
            elif hasattr(game, pick_col):
                val = getattr(game, pick_col, "")
            if not val:
                continue
            parts = str(val).strip().split()
            if not parts:
                continue
            team = parts[0]
            source = parts[1] if len(parts) > 1 else ""
            if team and team not in ("?", "None", "TIE") and source != "DEFAULT":
                return True

    # 2. Check games.csv for current season if games not provided or not matched
    try:
        import csv
        from current_season import FOOTBALL_SEASON
        proj_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(proj_dir, FOOTBALL_SEASON, "games.csv")
        if os.path.exists(csv_path):
            with open(csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                pick_col = f"{player_id}_pick"
                for row in reader:
                    val = row.get(pick_col, "").strip()
                    if not val:
                        continue
                    parts = val.split()
                    team = parts[0]
                    source = parts[1] if len(parts) > 1 else ""
                    if team and team not in ("?", "None", "TIE") and source != "DEFAULT":
                        return True
    except Exception:
        pass

    # 3. Check picks.db event log
    try:
        import db
        db_path = db.get_db_path()
        if os.path.exists(db_path):
            conn = db.get_connection(db_path)
            row = conn.execute(
                "SELECT 1 FROM pick_events WHERE player_id = ? LIMIT 1",
                (player_id,)
            ).fetchone()
            conn.close()
            if row:
                return True
    except Exception:
        pass

    # 4. Check current season's manual picks module if available
    try:
        import importlib
        from current_season import FOOTBALL_SEASON
        mod_name = f"manual_picks_{FOOTBALL_SEASON}"
        manual_mod = importlib.import_module(mod_name)
        manual_picks = getattr(manual_mod, "MANUAL_PICKS", {})
        pick_key = f"{player_id}_pick"
        player_picks = manual_picks.get(pick_key) or manual_picks.get(player_id)
        if player_picks:
            for week_picks in player_picks.values():
                if week_picks:
                    return True
    except Exception:
        pass

    return False

# You can get the ID here from hovering over the 'group entry' field
# for each player within the league view.
# https://fantasy.espn.com/games/nfl-pigskin-pickem-2024/group?id=93fb8547-d412-4290-b470-9261d2415021
# https://ibb.co/zbVG0Ld
# 

# 2024_2025
# ESPN_PLAYER_IDS = {
#   SMB_PICK_KEY: '6f072d90-670a-11ef-93c5-71d4b52c43b1',
#   SLB_PICK_KEY: '2a2d8720-67d0-11ef-bec6-71e3ade2304d',
#   SUE_PICK_KEY: '719947f0-6bdd-11ef-9300-e73470a18359',
#   JEAN_PICK_KEY: '373e4850-716c-11ef-b954-bb5441c4e093',
# }
# 2025_2026
# ESPN_PLAYER_IDS = {
#   games_col_keys.SMB_PICK_KEY: '65b79490-7c3b-11f0-8e6b-379d7a2b7cd8',
#   games_col_keys.SUE_PICK_KEY: '5197fc50-891c-11f0-b1ab-011cec36886d',
#   games_col_keys.SLB_PICK_KEY: '5831c2c0-89fe-11f0-8797-c790a2901aa2',
#   games_col_keys.JEAN_PICK_KEY: '15c866c0-8ac9-11f0-add8-416dcf432d0a',
#   games_col_keys.MORGAN_PICK_KEY: 'c2892ca0-8989-11f0-8ebe-c134be42498f',
# }
# 2026_2027
# Group URL: https://fantasy.espn.com/games/nfl-pickem-2026/group?id=0c59e437-7fef-41f4-ab51-f59630b42f35
ESPN_PLAYER_IDS = {
  games_col_keys.SMB_PICK_KEY: '02b3ae80-a80c-11f1-b79b-878cc15323ad',
}

def home_strategy(game):
    return game.home_team

def favorite_strategy(game):
    str_line = game.home_line
    if not str_line:
        return game.home_team
    if float(str_line) < 0:
        return game.home_team
    else:
        return game.away_team

TEAM_CITY_TO_NAME = {
    "ARI": "Cardinals",
    "ATL": "Falcons",
    "BAL": "Ravens",
    "BUF": "Bills",
    "CAR": "Panthers",
    "CHI": "Bears",
    "CIN": "Bengals",
    "CLE": "Browns",
    "DAL": "Cowboys",
    "DEN": "Broncos",
    "DET": "Lions",
    "GB": "Packers",
    "HOU": "Texans",
    "IND": "Colts",
    "JAX": "Jaguars",
    "KC": "Chiefs",
    "LV": "Raiders",
    "LAR": "Rams",
    "LAC": "Chargers",
    "MIA": "Dolphins",
    "MIN": "Vikings",
    "NE": "Patriots",
    "NO": "Saints",
    "NYG": "Giants",
    "NYJ": "Jets",
    "PHI": "Eagles",
    "PIT": "Steelers",
    "SF": "49ers",
    "SEA": "Seahawks",
    "TB": "Buccaneers",
    "TEN": "Titans",
    "WSH": "Commanders",
}

def morgan_fewest_letters_strategy(game):
    """ I would like my forgetting weeks to use a system of whichever team name
    has the least amount of letters, not including the city name. Does that make
    sense?
    
    Oh shoot. I totally forgot. Yes alphabetical works if there are the same
    number 
    """
    home_team = game.home_team
    away_team = game.away_team
    home_team_name = TEAM_CITY_TO_NAME[home_team]
    away_team_name = TEAM_CITY_TO_NAME[away_team]
    if len(home_team_name) < len(away_team_name):
        return home_team
    elif len(home_team_name) > len(away_team_name):
        return away_team
    # Team same length, use alpha by team name
    if home_team_name < away_team_name:
        return home_team
    else:
        return away_team

DEFAULT_STRATEGY = {
    games_col_keys.JEAN_PICK_KEY: home_strategy,
    games_col_keys.MORGAN_PICK_KEY: morgan_fewest_letters_strategy,
    games_col_keys.SLB_PICK_KEY: home_strategy,
    games_col_keys.SMB_PICK_KEY: favorite_strategy,
    games_col_keys.SUE_PICK_KEY: home_strategy,
    games_col_keys.ADAM_PICK_KEY: home_strategy,
    games_col_keys.CONSTANCE_PICK_KEY: home_strategy,
    games_col_keys.MAX_PICK_KEY: home_strategy,
}


