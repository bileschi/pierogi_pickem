import csv
import json
import os
import requests
from bs4 import BeautifulSoup
from current_season import FOOTBALL_SEASON

import propositions

OUTCOME_ID_KEY = 'outcome_id'
RESULT_KEY = 'result'

PICKS_COL_KEYS = (
  propositions.PROPOSITION_ID_KEY,
  OUTCOME_ID_KEY,
  RESULT_KEY,
)

DEBUG_PRINT = True
def dbprint(*args, **kwargs):
  if DEBUG_PRINT:
    print("§§§", end=" ")
    print(args, kwargs)

# ESPN changes the api URL location. you need to get the new URL by poking
# around at the network tab at the ESPN site.
year_key = None
if FOOTBALL_SEASON == "2023_2024":
  year_key = 230
elif FOOTBALL_SEASON == "2024_2025":
  year_key = 247
else:
  raise ValueError(f"Unknown FOOTBALL_SEASON: {FOOTBALL_SEASON}")

def get_picks(pick_id):
  dbprint(f"> get_picks({pick_id})")
  picks = []
  picks_url = (
    f'https://gambit-api.fantasy.espn.com/apis/v1/challenges/{year_key}/entries/{pick_id}?platform=chui&view=chui_default'
  )
  dbprint(f"contacting url {picks_url=}")
  response = requests.get(
    picks_url,
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
  soup = BeautifulSoup(response.content, 'html.parser')
  picks_json = json.loads(soup.text)
  dbprint("picks found" if 'picks' in picks_json else "ERROR parsing picks")
  for one_json_pick in picks_json['picks']:
    pick = {
      propositions.PROPOSITION_ID_KEY: None,
      OUTCOME_ID_KEY: None,
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

def write_picks_csv(picks, filename):
  with open(filename, 'w', newline='') as csvfile:
    pickwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    pickwriter.writerow(PICKS_COL_KEYS)
    for pick in picks:
      pickwriter.writerow([pick[k] for k in PICKS_COL_KEYS])

def read_picks_csv(filename):
  picks = []
  with open(filename, 'r', newline='') as csvfile:
    pickreader = csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    next(pickreader) #to skip header
    for row in pickreader:
      picks.append({k: v for (k,v) in zip(PICKS_COL_KEYS, row)})
  return picks

if __name__ == "__main__":
  import players
  picks = {}
  for (player, espn_pick_id) in players.ESPN_PLAYER_IDS.items():
    picks[player] = get_picks(espn_pick_id)
    write_picks_csv(picks[player], os.path.join(FOOTBALL_SEASON,f'{player}.csv'))
  picks_read_from_disk = {}
  for (player, espn_pick_id) in players.ESPN_PLAYER_IDS.items():
    picks_read_from_disk[player] = read_picks_csv(os.path.join(FOOTBALL_SEASON,f'{player}.csv'))
  for player in players.ESPN_PLAYER_IDS.keys():
    if picks[player] != picks_read_from_disk[player]:
      print(f"ERROR: {player} picks don't match")
      print(f"  {picks[player]}")
      print(f"  {picks_read_from_disk[player]}")
    assert picks[player] == picks_read_from_disk[player]