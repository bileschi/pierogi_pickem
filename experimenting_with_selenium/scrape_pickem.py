import requests
import pandas as pd
import csv
from bs4 import BeautifulSoup
import json

s = requests.Session()
domain_url = 'https://fantasy.espn.com'
user_agent_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
s.headers.update(user_agent_header)
session_response = s.get(domain_url)
# Check the response status code
if session_response.status_code == 200:
  print("session ok.")
else:
  print("session request failed.")
  exit(1)

swid = s.cookies.get_dict()['SWID']
entry_url = 'https://gambit-api.fantasy.espn.com/apis/v1/challenges/nfl-pigskin-pickem-2023?scoringPeriodId=7&platform=chui&view=chui_default'
# entry_url = 'https://fantasy.espn.com/games/nfl-pigskin-pickem-2023/picks?id=72520e10-4b6e-11ee-a4c8-27e5ad8f3bbd'
picks_url = 'https://gambit-api.fantasy.espn.com/apis/v1/challenges/230/entries/72520e10-4b6e-11ee-a4c8-27e5ad8f3bbd?platform=chui&view=chui_default'

stans_picks_url = 'https://fantasy.espn.com/games/nfl-pigskin-pickem-2023/picks?id=72520e10-4b6e-11ee-a4c8-27e5ad8f3bbd'
dads_picks_url  = 'https://fantasy.espn.com/games/nfl-pigskin-pickem-2023/picks?id=385fbc90-4b71-11ee-85db-77e9d8fab8a0'


entry_response = requests.get(entry_url, cookies={"swid": swid})



# Check the response status code
if entry_response.status_code == 200:
  print("entry ok.")
else:
  print("entry request failed.")
  exit(1)

soup = BeautifulSoup(entry_response.content, 'html.parser')
target_script = None
for script in soup.find_all('script'):
  if ('__project-chui__' in script.text):
    target_script = script
    print('found target script')
    break
if not target_script:
  print('could not found target script')
print('script: ', len(script), len(script.text))
# start_loc = target_script.text.find("window['__project-chui__'] = ")
json_key = "window['__project-chui__']="
start_loc = target_script.text.find(json_key)
print(start_loc)
t = target_script.text[(start_loc + len(json_key)):-1]
js = json.loads(t)

# print(len(script_block))

with open('one_entry_response.json', 'w') as jsonfile:
  json.dump(js, jsonfile, indent=1)

# print(type(r))
# pass
  
# SMB
# Week 1 request:
# https://gambit-api.fantasy.espn.com/apis/v1/challenges/230/entries/72520e10-4b6e-11ee-a4c8-27e5ad8f3bbd?platform=chui&view=chui_default
# https://gambit-api.fantasy.espn.com/apis/v1/challenges/230/entries/72520e10-4b6e-11ee-a4c8-27e5ad8f3bbd?platform=chui&view=chui_default
# https://gambit-api.fantasy.espn.com/apis/v1/challenges/230/entries/72520e10-4b6e-11ee-a4c8-27e5ad8f3bbd?platform=chui&view=chui_default
# SLB
# https://gambit-api.fantasy.espn.com/apis/v1/challenges/230/entries/385fbc90-4b71-11ee-85db-77e9d8fab8a0?platform=chui&view=chui_default

# These gambit links have, for each person a map from  propositionID to (outcomeID, result) pairs.
# If we can map from the gameID to the propositionID, we can get each person's picks, I think.

# Step 1 - Get 


# League URL.
# 'https://gambit-api.fantasy.espn.com/apis/v1/challenges/nfl-pigskin-pickem-2023?scoringPeriodId=7&platform=chui&view=chui_default'
# Entries URL.
# 'https://gambit-api.fantasy.espn.com/apis/v1/challenges/230/entries/72520e10-4b6e-11ee-a4c8-27e5ad8f3bbd?platform=chui&view=chui_default'


# One person's unique entries URL.  - this is specific per person.
# SLB
# https://gambit-api.fantasy.espn.com/apis/v1/challenges/230/entries/385fbc90-4b71-11ee-85db-77e9d8fab8a0?platform=chui&view=chui_default
# SMB
# https://gambit-api.fantasy.espn.com/apis/v1/challenges/230/entries/72520e10-4b6e-11ee-a4c8-27e5ad8f3bbd?platform=chui&view=chui_default



# Propositions URL.  A "Challenge" is a collection of "Propositions".
# https://gambit-api.fantasy.espn.com/apis/v1/propositions?challengeId=230&platform=chui&view=chui_default
# We will need to collect the full set of propositions for the Challenge (league)
#  Each proposition has a 
#    "correctOutcome" such as 9cb76a82-f0e0-11ed-a0c6-e37e259a4c71
#    "id" such as "9cb76a80-f0e0-11ed-a0c6-e37e259a4c71"
#    "name" such as "CAR @ ATL"  
#    "mappings: - type; EVENT_ID, 401547403   ** This can connect to games.csv
#    "spread": -2.5
#  This was proposition 252