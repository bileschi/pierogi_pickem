import csv
import json
import os
import requests
from typing import List, Optional
from bs4 import BeautifulSoup

from current_season import FOOTBALL_SEASON

# Get these by navigating to, e.g.,
# "https://fantasy.espn.com/games/pigskinpickem/?navmethod=web_vanityredirect"
# and monitoring the network tab.  Note that the challengeId is different for
# each season.
ESPN_PROPOSITIONS_URL = {
    "2023_2024": (
        f"https://gambit-api.fantasy.espn.com/apis/v1/propositions?challengeId=230&platform=chui&view=chui_default"
    ),
    "2024_2025": (
        f"https://gambit-api.fantasy.espn.com/apis/v1/propositions?challengeId=247&platform=chui&view=chui_default"
    ),
}


PROPOSITION_ID_KEY = "proposition_id"
LINE_KEY = "home_line"
PROP_NAME_KEY = "prop_name"
GAME_ID_KEY = "game_id"
OUTCOME_1_ID_KEY = "outcome_1_id"
OUTCOME_1_ABBREV_KEY = "outcome_1_abbr"
OUTCOME_2_ID_KEY = "outcome_2_id"
OUTCOME_2_ABBREV_KEY = "outcome_2_abbr"


PROP_COL_KEYS = (
    PROPOSITION_ID_KEY,
    LINE_KEY,
    PROP_NAME_KEY,
    GAME_ID_KEY,
    OUTCOME_1_ID_KEY,
    OUTCOME_1_ABBREV_KEY,
    OUTCOME_2_ID_KEY,
    OUTCOME_2_ABBREV_KEY,
)


def get_propositions(espn_propositions_url: Optional[str] = None) -> list:
    """
    Fetches and parses proposition data from the given ESPN URL.

    A proposition is similar to a "bet" and can have multiple bets on a single game.

    Args:
      espn_propositions_url (str): The URL to fetch propositions from.

    Returns:
      list: A list of dictionaries, each containing details about a proposition.
        Each dictionary contains the following keys:
          - PROPOSITION_ID_KEY: The ID of the proposition.
          - LINE_KEY: The line or spread of the proposition.
          - CORRECT_OUTCOME_ABBREV_KEY: The abbreviation of the correct outcome.
          - INCORRECT_OUTCOME_ABBREV_KEY: The abbreviation of the incorrect outcome.
          - PROP_NAME_KEY: The name of the proposition.
          - GAME_ID_KEY: The ID of the game associated with the proposition.
    """
    if not espn_propositions_url:
        espn_propositions_url = ESPN_PROPOSITIONS_URL[FOOTBALL_SEASON]
    # Get the ids and lines for all the propositions in the league.
    # A propisition is semantically like a "bet".  It is different from a game
    # since you can have multiple bets on a single game.
    propositions = []
    # e.g., 'https://gambit-api.fantasy.espn.com/apis/v1/propositions?challengeId=230&platform=chui&view=chui_default'
    response = requests.get(
        espn_propositions_url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    )
    soup = BeautifulSoup(response.content, "html.parser")
    propositions_json = json.loads(soup.text)
    for one_json_prop in propositions_json:
        proposition = {
            PROPOSITION_ID_KEY: None,
            LINE_KEY: None,
            PROP_NAME_KEY: None,
            GAME_ID_KEY: None,
            OUTCOME_1_ID_KEY: None,
            OUTCOME_1_ABBREV_KEY: None,
            OUTCOME_2_ID_KEY: None,
            OUTCOME_2_ABBREV_KEY: None,
        }
        proposition[PROPOSITION_ID_KEY] = one_json_prop["id"]
        proposition[PROP_NAME_KEY] = one_json_prop["name"]
        for i, possible_outcome in enumerate(one_json_prop["possibleOutcomes"]):
            id = possible_outcome["id"]
            abbrev = possible_outcome["abbrev"]
            if i == 0:
                proposition[OUTCOME_1_ID_KEY] = id
                proposition[OUTCOME_1_ABBREV_KEY] = abbrev
            else:
                proposition[OUTCOME_2_ID_KEY] = id
                proposition[OUTCOME_2_ABBREV_KEY] = abbrev
        if "spread" in one_json_prop:
            proposition[LINE_KEY] = one_json_prop["spread"]
        for val in one_json_prop["mappings"]:
            if val["type"] == "COMPETITION_ID":
                proposition[GAME_ID_KEY] = val["value"]
        propositions.append(proposition)
    return propositions

def load_propositions_csv():
    """
    Loads a list of proposition dictionaries from a CSV file.

    Returns:
      list: A list of dictionaries, each containing details about a proposition.
        Each dictionary should have keys corresponding to PROP_COL_KEYS.

    The CSV file is expected to be in the directory specified by the FOOTBALL_SEASON
    variable with the filename "propositions.csv". The file is expected to be written
    with a header row containing PROP_COL_KEYS, and each subsequent row containing
    the values of each proposition dictionary in the order specified by PROP_COL_KEYS.

    Note:
      - The FOOTBALL_SEASON and PROP_COL_KEYS variables must be defined in the
        module's scope.
      - The csv and os modules must be imported.
    """
    propositions = []
    with open(
        os.path.join(FOOTBALL_SEASON, "propositions.csv"), "r", newline=""
    ) as csvfile:
        propreader = csv.reader(csvfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        next(propreader)  # Skip the header row
        for row in propreader:
            proposition = {k: v for k, v in zip(PROP_COL_KEYS, row)}
            propositions.append(proposition)
    return propositions

def write_propositions_csv(propositions: List[dict]):
    """
    Writes a list of proposition dictionaries to a CSV file.

    Args:
      propositions (list of dict): A list where each element is a dictionary
                     representing a proposition. Each dictionary
                     should have keys corresponding to PROP_COL_KEYS.

    The CSV file is saved in the directory specified by the FOOTBALL_SEASON variable
    with the filename "propositions.csv". The file is written with a header row
    containing PROP_COL_KEYS, and each subsequent row contains the values of each
    proposition dictionary in the order specified by PROP_COL_KEYS.

    Note:
      - The FOOTBALL_SEASON and PROP_COL_KEYS variables must be defined in the
        module's scope.
      - The csv and os modules must be imported.
    """
    with open(
        os.path.join(FOOTBALL_SEASON, "propositions.csv"), "w", newline=""
    ) as csvfile:
        propwriter = csv.writer(csvfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        propwriter.writerow(PROP_COL_KEYS)
        for prop in propositions:
            propwriter.writerow([prop[k] for k in PROP_COL_KEYS])


if __name__ == "__main__":
    propositions = get_propositions(
        espn_propositions_url=ESPN_PROPOSITIONS_URL[FOOTBALL_SEASON]
    )
    write_propositions_csv(propositions)
