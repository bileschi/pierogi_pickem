import csv
import json
import os
import requests

from bs4 import BeautifulSoup

import propositions
# import morgans_picks

from current_season import FOOTBALL_SEASON


# week	home	away	line	home_score	away_score	Stanley M	Aunt Sue	Stanley L	Jean	Morgan	game_id

one_game = dict()

AWAY_KEY = 'away_team'
AWAY_SCORE_KEY = 'away_score'
# CORRECT_OUTCOME_ABBREV_KEY = 'correct_outcome_key'
# GAME_ID_KEY = 'game_id'
HOME_KEY = 'home_team'
HOME_SCORE_KEY = 'home_score'
# INCORRECT_OUTCOME_ABBREV_KEY = 'incorrect_outcome_key'
JEAN_PICK_KEY = 'jean_pick'
# LINE_KEY = 'home_line'
MORGAN_PICK_KEY = 'morgan_pick'
OUTCOME_ID_KEY = 'outcome_id'
# PROP_NAME_KEY = 'prop_name'
# PROPOSITION_ID_KEY = 'proposition_id'
RESULT_KEY = 'result'
SLB_PICK_KEY = 'slb_pick'
SMB_PICK_KEY = 'smb_pick'
SUE_PICK_KEY = 'sue_pick'
WEEK_KEY = 'week'

GAME_COL_KEYS = (
  WEEK_KEY,  # get_game_scores
  HOME_KEY,  # get_game_scores
  AWAY_KEY,  # get_game_scores
  propositions.GAME_ID_KEY,  # get_game_scores
  propositions.PROPOSITION_ID_KEY,  # get_propositions
  propositions.CORRECT_OUTCOME_ABBREV_KEY, # get_propositions
  HOME_SCORE_KEY,  # get_game_scores
  AWAY_SCORE_KEY,  # get_game_scores
  propositions.LINE_KEY,  # get_propositions
  SMB_PICK_KEY,
  SLB_PICK_KEY,
  SUE_PICK_KEY,
  JEAN_PICK_KEY,
  MORGAN_PICK_KEY,
)

PICKS_COL_KEYS = (
  propositions.PROPOSITION_ID_KEY,
  OUTCOME_ID_KEY,
  RESULT_KEY,
)

PLAYER_IDS = {
  SMB_PICK_KEY: '72520e10-4b6e-11ee-a4c8-27e5ad8f3bbd',
  SLB_PICK_KEY: '385fbc90-4b71-11ee-85db-77e9d8fab8a0',
  SUE_PICK_KEY: '4d1a4380-4bfd-11ee-b3fb-11aa5673265b',
  JEAN_PICK_KEY: '5d03d350-4c3a-11ee-8382-91995701af39',
}

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

def game_as_str(game_dict):
  return(','.join([str(game_dict[k]) for k in GAME_COL_KEYS]))


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
        game = {k: '' for k in GAME_COL_KEYS}
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
          game_id = game_href.split("=")[1].split("&")[0]
          score_text = score_col.get_text()
          # Score text should be something like "ATL 25, GB 24".
          scores = parse_score_text(
            score_text, home_team=game[HOME_KEY])   
          game[HOME_SCORE_KEY] = scores['home']
          game[AWAY_SCORE_KEY] = scores['away']
          game[propositions.GAME_ID_KEY] = game_id
        games.append(game)
  return(games)


def get_picks(pick_id):
  picks = []
  picks_url = (
    f'https://gambit-api.fantasy.espn.com/apis/v1/challenges/230/entries/{pick_id}?platform=chui&view=chui_default'
  )
  response = requests.get(
    picks_url,
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
  soup = BeautifulSoup(response.content, 'html.parser')
  picks_json = json.loads(soup.text)
  for one_json_pick in picks_json['picks']:
    pick = {
      propositions.PROPOSITION_ID_KEY: None,
      OUTCOME_ID_KEY: None,
      RESULT_KEY: None
    }
    if len(one_json_pick['outcomesPicked']) == 1:
      one_outcome = one_json_pick['outcomesPicked'][0]
      pick[OUTCOME_ID_KEY] = one_outcome['outcomeId']
      pick[RESULT_KEY] = one_outcome['result']
    # Otherwise no pick.
    # TODO: handle multiple picks.  - is that even possible?
    pick[propositions.PROPOSITION_ID_KEY] = one_json_pick['propositionId']
    picks.append(pick)
  return(picks)

def write_games_csv(games, filename):
  # Write CSV with one row per game.  Include keys as above.
  with open(filename, 'w', newline='') as csvfile:
    gamewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    gamewriter.writerow(GAME_COL_KEYS)
    for game in games:
      gamewriter.writerow([game[k] for k in GAME_COL_KEYS])

def write_picks_csv(picks, filename):
  with open(filename, 'w', newline='') as csvfile:
    pickwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    pickwriter.writerow(PICKS_COL_KEYS)
    for pick in picks:
      pickwriter.writerow([pick[k] for k in PICKS_COL_KEYS])

def load_games_csv(filename):
  games = []
  with open(filename, newline='') as csvfile:
    gamereader = csv.DictReader(csvfile, delimiter=',')
    return [row for row in gamereader]


if __name__ == "__main__":

  picks = {}
  # for (k, v) in PLAYER_IDS.items():
  #   picks[k] = get_picks(v)
  #   write_picks_csv(picks[k], f'{k}.csv')
  # games = get_game_scores()
  # write_games_csv(games, 'base_games.csv')
  # # games = load_games_csv('base_games.csv')
  
  # # Populate lines & picks. A faster, non n^2 way to do this would be to build
  # # an index but this dumb way is so much faster than the
  # # fetches that it doesn't matter.
  # for game in games:
  #   for prop in propositions:
  #     if game[GAME_ID_KEY] == prop[GAME_ID_KEY]:
  #       game[LINE_KEY] = prop[LINE_KEY]
  #       game[PROPOSITION_ID_KEY] = prop[PROPOSITION_ID_KEY]
  #       game[CORRECT_OUTCOME_ABBREV_KEY] = prop[CORRECT_OUTCOME_ABBREV_KEY]
  #       game[INCORRECT_OUTCOME_ABBREV_KEY] = prop[INCORRECT_OUTCOME_ABBREV_KEY]
  # for game in games:
  #   for k in PLAYER_IDS.keys():
  #     for pick in picks[k]:
  #       if game[PROPOSITION_ID_KEY] == pick[PROPOSITION_ID_KEY]:
  #         if(pick[RESULT_KEY]) == 'CORRECT':
  #           game[k] = game[CORRECT_OUTCOME_ABBREV_KEY]
  #         else:
  #           game[k] = game[INCORRECT_OUTCOME_ABBREV_KEY]

  # # Incorporate Morgan's picks.
  # for game in games:
  #   game[MORGAN_PICK_KEY] = morgans_picks.get_morgan_pick(week=game[WEEK_KEY],
  #                   home_team=game[HOME_KEY],
  #                   away_team=game[AWAY_KEY])
  # # Add defaults for Sue, Jean, SMB, SLB
  # for game in games:
  #   game[SMB_PICK_KEY] = game[SMB_PICK_KEY] or game[HOME_KEY]
  #   game[SLB_PICK_KEY] = game[SLB_PICK_KEY] or game[HOME_KEY]
  #   game[SUE_PICK_KEY] = game[SUE_PICK_KEY] or game[HOME_KEY]
  #   game[JEAN_PICK_KEY] = game[JEAN_PICK_KEY] or game[HOME_KEY]
  # write_games_csv(games, 'games.csv')
