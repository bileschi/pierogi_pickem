import csv
import json
import os
from typing import Any, Dict
import urllib.request

import players
import propositions
from current_season import FOOTBALL_SEASON, N_WEEKS_IN_SEASON
import games_col_keys

# Game metadata.
GAME_COL_KEYS = (
  games_col_keys.WEEK_KEY,
  games_col_keys.HOME_KEY,
  games_col_keys.AWAY_KEY,
  propositions.GAME_ID_KEY,
  propositions.PROPOSITION_ID_KEY,
  games_col_keys.BET_WIN_KEY,
  games_col_keys.HOME_SCORE_KEY,
  games_col_keys.AWAY_SCORE_KEY,
  games_col_keys.GAME_STATUS_KEY,
  games_col_keys.STATUS_DETAIL_KEY,
  propositions.LINE_KEY,
  propositions.PROP_DATE_KEY,
  games_col_keys.SMB_PICK_KEY,
  games_col_keys.SLB_PICK_KEY,
  games_col_keys.SUE_PICK_KEY,
  games_col_keys.JEAN_PICK_KEY,
  games_col_keys.MORGAN_PICK_KEY,
  games_col_keys.ADAM_PICK_KEY,
  games_col_keys.CONSTANCE_PICK_KEY,
  games_col_keys.MAX_PICK_KEY,
)

DEBUG_PRINT = True
def dbprint(*args, **kwargs):
  if DEBUG_PRINT:
    print("§§§", end=" ")
    print(*args, **kwargs)

def parse_score_text(score_text, home_team):
  (away, home) = score_text.split(",")
  first_team = away.strip().split(" ")[0].strip()
  first_score = away.strip().split(" ")[1].strip()
  second_score = home.strip().split(" ")[1].strip()
  if first_team == home_team:
    return({"home": first_score, "away": int(second_score)})
  else:
    return({"home": second_score, "away": int(first_score)})


def get_game_scores():
  # Get all the games and all the scores using ESPN's scoreboard JSON endpoint.
  games = []
  year = FOOTBALL_SEASON.split("_")[0]
  for week in range(1, N_WEEKS_IN_SEASON + 1):
    dbprint(f"  week={week}")
    espn_week_url = (
      f'https://cdn.espn.com/core/nfl/scoreboard?xhr=1&year={year}&seasontype=2&week={week}'
    )
    req = urllib.request.Request(
      espn_week_url,
      headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    try:
      with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode('utf-8'))
      events = data.get('content', {}).get('sbData', {}).get('events', [])
      for event in events:
        game : Dict[str, Any] = {k: '' for k in GAME_COL_KEYS}
        game[games_col_keys.WEEK_KEY] = week
        game[propositions.GAME_ID_KEY] = str(event.get('id', ''))

        status_info = event.get('status', {}).get('type', {})
        game_state = status_info.get('state', 'pre')  # 'pre', 'in', 'post'
        game_detail = status_info.get('shortDetail', '')
        game[games_col_keys.GAME_STATUS_KEY] = game_state
        game[games_col_keys.STATUS_DETAIL_KEY] = game_detail

        competitors = event.get('competitions', [{}])[0].get('competitors', [])
        for comp in competitors:
          abbr = comp.get('team', {}).get('abbreviation', '').upper()
          score = str(comp.get('score', ''))
          if comp.get('homeAway') == 'away':
            game[games_col_keys.AWAY_KEY] = abbr
            if game_state in ('in', 'post') and score != '':
              game[games_col_keys.AWAY_SCORE_KEY] = score
          elif comp.get('homeAway') == 'home':
            game[games_col_keys.HOME_KEY] = abbr
            if game_state in ('in', 'post') and score != '':
              game[games_col_keys.HOME_SCORE_KEY] = score
        games.append(game)
    except Exception as e:
      print(f"  Error loading scoreboard for week {week}: {e}")
  return games


def write_games_csv(games, filename):
  # Write CSV with one row per game.  Include keys as above.
  with open(filename, 'w', newline='') as csvfile:
    gamewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    gamewriter.writerow(GAME_COL_KEYS)
    for game in games:
      gamewriter.writerow([game[k] for k in GAME_COL_KEYS])


def load_games_csv(filename):
  with open(filename, newline='') as csvfile:
    gamereader = csv.DictReader(csvfile, delimiter=',')
    return [row for row in gamereader]


if __name__ == "__main__":
  dbprint("Getting games scores")
  games = get_game_scores()
  dbprint("Found %d games" % len(games))
  games_filename = os.path.join(FOOTBALL_SEASON, 'base_games.csv')
  write_games_csv(games, games_filename)
  dbprint("Wrote games to %s" % games_filename)
  games = load_games_csv(games_filename)
  dbprint("Loaded %d games" % len(games))
