import csv
import json
import requests
from bs4 import BeautifulSoup

# week	home	away	line	home_score	away_score	Stanley M	Aunt Sue	Stanley L	Jean	Morgan	game_id

one_game = dict()

WEEK_KEY = 'week'
HOME_KEY = 'home_team'
AWAY_KEY = 'away_team'
GAME_ID_KEY = 'game_id'
CORRECT_OUTCOME_KEY = 'correct_outcome'
PROP_NAME_KEY = 'prop_name'
PROPOSITION_ID_KEY = 'proposition_id'
LINE_KEY = 'home_line'
HOME_SCORE_KEY = 'home_score'
AWAY_SCORE_KEY = 'away_score'
SMB_PICK_KEY = 'smb_pick'
SLB_PICK_KEY = 'slb_pick'
SUE_PICK_KEY = 'sue_pick'
JEAN_PICK_KEY = 'jean_pick'

game_col_keys = (
  WEEK_KEY,  # get_game_scores
  HOME_KEY,  # get_game_scores
  AWAY_KEY,  # get_game_scores
  GAME_ID_KEY,  # get_game_scores
  PROPOSITION_ID_KEY,  # get_propositions
  HOME_SCORE_KEY,  # get_game_scores
  AWAY_SCORE_KEY,  # get_game_scores
  LINE_KEY,  # get_propositions
  SMB_PICK_KEY,
  SLB_PICK_KEY,
  SUE_PICK_KEY,
  JEAN_PICK_KEY,
)

prop_col_keys = (
  PROPOSITION_ID_KEY,
  LINE_KEY,
  CORRECT_OUTCOME_KEY,
  PROP_NAME_KEY, 
  GAME_ID_KEY
)

def parse_score_text(score_text):
  # expect text like "ATL 25, GB 24" or "BUF 38, LV 10"
  (away, home) = score_text.split(",")
  away_score = away.strip().split(" ")[1].strip()
  home_score = home.strip().split(" ")[1].strip()
  return(away_score, home_score)

def game_as_str(game_dict):
  return(','.join([str(game_dict[k]) for k in game_col_keys]))


def get_game_scores():
  # Get all the games and all the scores.
  #
  # Uses ESPN's main schedule pages to scrape basic stats. These values have
  # nothing to do with our pickem picks, they are common to the NFL.
  games = []
  for week in range(1, 19):
    # Assume year is 2023
    espn_week_url = (
      f'https://www.espn.com/nfl/schedule/_/week/{week}/year/2023/seasontype/2')
    response = requests.get(
      espn_week_url,
      headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    soup = BeautifulSoup(response.content, 'html.parser')

    # The page organizes weeks by days, separating, e.g., 
    # Monday night football from the Sunday games.
    football_days = soup.find_all(
      'div',
      class_='ScheduleTables mb5 ScheduleTables--nfl ScheduleTables--football')
    print(f"week {week}")
    for football_day in football_days:
      # Each of these rows corresponds to one game.
      rows = football_day.find_all(
        'tr',
        class_='Table__TR Table__TR--sm Table__even')
      for i_r, row in enumerate(rows[:]):
        game = {k: '' for k in game_col_keys}
        game[WEEK_KEY] = week
        # Get the teams
        teams = row.find_all('span', class_='Table__Team')
        for i_t, team in enumerate(teams):
          team_link = team.find_all('a')[0]
          team_code = team_link['href'].split('/')[5].upper()
          # Away team is listed first
          if i_t == 0:
            game[AWAY_KEY] = team_code
          if i_t == 1:
            game[HOME_KEY] = team_code
        # Get the score and ESPN game ID.  This will be none if the game 
        # has not happened or is in progres.
        score_col = row.find('td', class_='teams__col Table__TD')
        if score_col:
          game_href = score_col.find_all('a')[0]['href']
          # print('game href ', game_href)
          game_id = game_href.split("=")[1]
          score_text = score_col.get_text()
          # Score text should be something like "ATL 25, GB 24".
          (away_score, home_score) = parse_score_text(score_text)   
          game[HOME_SCORE_KEY] = home_score
          game[AWAY_SCORE_KEY] = away_score
          game[GAME_ID_KEY] = game_id
        games.append(game)
  return(games)

def get_propositions():
    propositions = []
    espn_propositions_url = (
      f'https://gambit-api.fantasy.espn.com/apis/v1/propositions?challengeId=230&platform=chui&view=chui_default')
    response = requests.get(
      espn_propositions_url,
      headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    soup = BeautifulSoup(response.content, 'html.parser')
    propositions_json = json.loads(soup.text)
    for one_json_prop in propositions_json:
      proposition = {
          PROPOSITION_ID_KEY: None,
          LINE_KEY: None,
          CORRECT_OUTCOME_KEY: None,
          PROP_NAME_KEY: None, 
          GAME_ID_KEY: None
      }
      if len(one_json_prop['correctOutcomes']) == 1:
        proposition[CORRECT_OUTCOME_KEY] = one_json_prop['correctOutcomes'][0]
      proposition[PROPOSITION_ID_KEY] = one_json_prop['id']
      proposition[PROP_NAME_KEY] = one_json_prop['name']
      if 'spread' in one_json_prop:
        proposition[LINE_KEY] = one_json_prop['spread']
      for val in one_json_prop['mappings']:
        if val['type'] == 'COMPETITION_ID':
          proposition[GAME_ID_KEY] = val['value']
      propositions.append(proposition)
    return(propositions)

def write_games_csv(games):
  # Write CSV with one row per game.  Include keys as above.
  with open('games.csv', 'w', newline='') as csvfile:
    gamewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    gamewriter.writerow(game_col_keys)
    for game in games:
      gamewriter.writerow([game[k] for k in game_col_keys])

def write_propositions_csv(propositions):
  with open('propositions.csv', 'w', newline='') as csvfile:
    propwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    propwriter.writerow(prop_col_keys)
    for prop in propositions:
      propwriter.writerow([prop[k] for k in prop_col_keys])

if __name__ == "__main__":
  # games = get_game_scores()
  # write_games_csv(games)
  propositions = get_propositions()
  write_propositions_csv(propositions)
  