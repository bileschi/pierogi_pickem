import csv
import os
import requests
from bs4 import BeautifulSoup

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
  propositions.LINE_KEY,
  propositions.PROP_DATE_KEY,
  games_col_keys.SMB_PICK_KEY,
  games_col_keys.SLB_PICK_KEY,
  games_col_keys.SUE_PICK_KEY,
  games_col_keys.JEAN_PICK_KEY,
  games_col_keys.MORGAN_PICK_KEY,
  games_col_keys.ADAM_PICK_KEY
)

DEBUG_PRINT = True
def dbprint(*args, **kwargs):
  if DEBUG_PRINT:
    print("§§§", end=" ")
    print(*args, **kwargs)

def parse_score_text(score_text, home_team):
  # expect text like "ATL 25, GB 24" or "BUF 38, LV 10"
  # scores are listed larger number first - not in home/away order.
  #
  # return {"home": home_score, "away": away_score}
  (away, home) = score_text.split(",")
  first_team = away.strip().split(" ")[0].strip()
  first_score = away.strip().split(" ")[1].strip()
  second_score = home.strip().split(" ")[1].strip()
  if first_team == home_team:
    return({"home": first_score, "away": int(second_score)})
  else:
    return({"home": second_score, "away": int(first_score)})


def get_game_scores():
  # Get all the games and all the scores.
  #
  # Uses ESPN's main schedule pages to scrape basic stats. These values have
  # nothing to do with our pickem picks, they are common to the NFL.
  games = []
  for week in range(1, N_WEEKS_IN_SEASON + 1):
    # site should look like this: https://ibb.co/KxP7Jv4
    dbprint(f"  {week=}")
    year = FOOTBALL_SEASON.split("_")[0]
    espn_week_url = (
      f'https://www.espn.com/nfl/schedule/_/week/{week}/year/{year}/seasontype/2')
    dbprint(f"  loading from {espn_week_url=}")
    response = requests.get(
      espn_week_url,
      headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    soup = BeautifulSoup(response.content, 'html.parser')

    # The page organizes weeks by days, separating, e.g.,
    # Monday night football from the Sunday games.
    football_days = soup.find_all(
      'div',
      class_='ScheduleTables mb5 ScheduleTables--nfl ScheduleTables--football')
    for i_f, football_day in enumerate(football_days):
      day_name = football_day.find('div', class_='Table__Title').get_text()
      dbprint(f"  football_day {day_name}")
      # Each of these rows corresponds to one game.
      rows = football_day.find_all(
        'tr',
        class_='Table__TR Table__TR--sm Table__even')
      for i_r, row in enumerate(rows[:]):
        game = {k: '' for k in GAME_COL_KEYS}
        game[games_col_keys.WEEK_KEY] = week
        # Get the teams
        teams = row.find_all('span', class_='Table__Team')
        for i_t, team in enumerate(teams):
          team_link = team.find_all('a')[0]
          team_code = team_link['href'].split('/')[5].upper()
          # Away team is listed first
          if i_t == 0:
            game[games_col_keys.AWAY_KEY] = team_code
            dbprint(f'    Away team: {team_code}')
          if i_t == 1:
            game[games_col_keys.HOME_KEY] = team_code
            dbprint(f'    Home team: {team_code}')
        # Get the score and ESPN game ID.  This will be none if the game
        # has not happened or is in progres.
        #
        # The 'game_href' link has a format that looks like:
        #  https://www.espn.com/nfl/game/_/gameId/401671861/texans-colts
        #
        # The game id is the number after the "gameId" string.
        score_col = row.find('td', class_='teams__col Table__TD')
        date_col = row.find('td', class_='date__col Table__TD')
        game_href = None
        col = None
        if score_col:
          col = score_col
        else:
          col = date_col
        if col:
          game_href = col.find_all('a')[0]['href']
          dbprint('    game href ', game_href)
          # Split the url by the '/' and get the element after 'gameId'
          game_href_parts = game_href.split("/")
          game_id = None
          for i, part in enumerate(game_href_parts):
            if part == 'gameId':
              game_id = game_href_parts[i + 1]
          if not game_id:
            print(f"    ERROR: could not find game id in {game_href}")
            continue
          game[propositions.GAME_ID_KEY] = game_id
        if score_col:
          score_text = score_col.get_text()
          # Score text should be something like "ATL 25, GB 24".
          scores = parse_score_text(
            score_text, home_team=game[games_col_keys.HOME_KEY])
          game[games_col_keys.HOME_SCORE_KEY] = scores['home']
          game[games_col_keys.AWAY_SCORE_KEY] = scores['away']
        games.append(game)
  return(games)


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
