import espn_game_results
import propositions

JEAN_PICK_KEY = 'jean_pick'
MORGAN_PICK_KEY = 'morgan_pick'
SLB_PICK_KEY = 'slb_pick'
SMB_PICK_KEY = 'smb_pick'
SUE_PICK_KEY = 'sue_pick'
ADAM_PICK_KEY = 'adam_pick'


# I got these ids from the espn site by poking around at the network tab.

# 2023_2024
# ESPN_PLAYER_IDS = {
#   SMB_PICK_KEY: '72520e10-4b6e-11ee-a4c8-27e5ad8f3bbd',
#   SLB_PICK_KEY: '385fbc90-4b71-11ee-85db-77e9d8fab8a0',
#   SUE_PICK_KEY: '4d1a4380-4bfd-11ee-b3fb-11aa5673265b',
#   JEAN_PICK_KEY: '5d03d350-4c3a-11ee-8382-91995701af39',
# }

# 2024_2025
PLAYER_IDS = [
  JEAN_PICK_KEY,
  MORGAN_PICK_KEY,
  SLB_PICK_KEY,
  SMB_PICK_KEY,
  SUE_PICK_KEY,
  ADAM_PICK_KEY,
]
# You can get the ID here from hovering over the 'group entry' field
# for each player within the league view.
# https://fantasy.espn.com/games/nfl-pigskin-pickem-2024/group?id=93fb8547-d412-4290-b470-9261d2415021
# https://ibb.co/zbVG0Ld
# 
ESPN_PLAYER_IDS = {
  SMB_PICK_KEY: '6f072d90-670a-11ef-93c5-71d4b52c43b1',
  SLB_PICK_KEY: '2a2d8720-67d0-11ef-bec6-71e3ade2304d',
  SUE_PICK_KEY: '719947f0-6bdd-11ef-9300-e73470a18359',
  JEAN_PICK_KEY: '373e4850-716c-11ef-b954-bb5441c4e093',
}

home_strategy = lambda game: game[espn_game_results.HOME_KEY]

def favorite_strategy(game):
  str_line = game[propositions.LINE_KEY]
  if not str_line:
    return game[espn_game_results.HOME_KEY]
  if float(str_line) < 0:
    return game[espn_game_results.HOME_KEY]
  else:
    return game[espn_game_results.AWAY_KEY]

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
  home_team = game[espn_game_results.HOME_KEY]
  away_team = game[espn_game_results.AWAY_KEY]
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
  JEAN_PICK_KEY: home_strategy,
  MORGAN_PICK_KEY: morgan_fewest_letters_strategy,
  SLB_PICK_KEY: home_strategy,
  SMB_PICK_KEY: favorite_strategy,
  SUE_PICK_KEY: home_strategy,
  ADAM_PICK_KEY: home_strategy,
}


