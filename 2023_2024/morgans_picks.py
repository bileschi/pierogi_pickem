MORGAN_MANUAL_PICKS = {
    1: [
        "KC",
        "ATL",
        "CIN",
        "JAX",
        "MIN",
        "SF",
        "ARI",
        "BAL",
        "TEN",
        "MIA",
        "PHI",
        "SEA",
        "CHI",
        "DEN",
        "DAl",
        "NYJ",
    ],
    3: [
        "SF",
        "TEN",
        "DET",
        "NO",
        "MIA",
        "MIN",
        "NE",
        "BUF",
        "HOU",
        "IND",
        "SEA",
        "KC",
        "DAL",
        "LV",
        "PHI",
        "LAR",
    ],
    4: [
        "MIA",
        "DEN",
        "CIN",
        "BAL",
        "IND",
        "TB",
        "PHI",
        "MIN",
        "HOU",
        "LAC",
        "DAL",
        "SF",
        "KC",
        "SEA",
    ],
    6: [
        "LV",
        "DET",
        "LAR",
        "PHI",
        "BUF",
        "DAL",
    ],
    7: [
        "LV",
        "CLE",
        "BUF",
        "WSH",
        "TB",
        "DET",
        "LAR",
        "ARI",
        "GB",
        "LAC",
        "MIA",
        "SF",
    ],
    8: [
        "BUF",
        "LAR",
        "MIN",
        "TEN",
        "IND",
        "MIA",
        "NYJ",
        "JAX",
        "PHI",
        "HOU",
        "SEA",
        "KC",
        "BAL",
        "SF",
        "CHI",
        "DET",
    ],
    11: [
        "PIT",
        "DET",
        "LAC",
        "MIA",
        "WSH",
        "DAL",
        "JAX",
        "HOU",
        "SF",
        "NYJ",
        "LAR",
        "MIN",
        "KC",
    ],
}

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

def morgan_auto_pick(home_team, away_team):
  """ I would like my forgetting weeks to use a system of whichever team name
  has the least amount of letters, not including the city name. Does that make
  sense?
  
  Oh shoot. I totally forgot. Yes alphabetical works if there are the same
  number 
  """
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


def get_morgan_pick(week, home_team, away_team):
  if week in MORGAN_MANUAL_PICKS:
    home_pick = home_team in MORGAN_MANUAL_PICKS[week]
    away_pick = away_team in MORGAN_MANUAL_PICKS[week]
    if home_pick and away_pick:
      print("ERROR: both teams picked for week %s, %s @ %s" % (week, away_team, home_team))
    if home_pick:
      return home_team
    if away_pick:
      return away_team
  return morgan_auto_pick(home_team, away_team)


