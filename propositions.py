import csv
import json
import os
import requests
from typing import List, Optional
from bs4 import BeautifulSoup
from dataclasses import dataclass

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
    "2025_2026": (
        f"https://gambit-api.fantasy.espn.com/apis/v1/propositions?challengeId=265&platform=chui&view=chui_default"
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
PROP_DATE_KEY = "prop_date"

PROP_COL_KEYS = (
    PROPOSITION_ID_KEY,
    LINE_KEY,
    PROP_NAME_KEY,
    GAME_ID_KEY,
    OUTCOME_1_ID_KEY,
    OUTCOME_1_ABBREV_KEY,
    OUTCOME_2_ID_KEY,
    OUTCOME_2_ABBREV_KEY,
    PROP_DATE_KEY
)

@dataclass
class Proposition:
    proposition_id: Optional[str] = None
    home_line: Optional[str] = None
    prop_name: Optional[str] = None
    game_id: Optional[str] = None
    outcome_1_id: Optional[str] = None
    outcome_1_abbr: Optional[str] = None
    outcome_2_id: Optional[str] = None
    outcome_2_abbr: Optional[str] = None
    prop_date: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "Proposition":
        return cls(
            proposition_id=d.get(PROPOSITION_ID_KEY),
            home_line=d.get(LINE_KEY),
            prop_name=d.get(PROP_NAME_KEY),
            game_id=d.get(GAME_ID_KEY),
            outcome_1_id=d.get(OUTCOME_1_ID_KEY),
            outcome_1_abbr=d.get(OUTCOME_1_ABBREV_KEY),
            outcome_2_id=d.get(OUTCOME_2_ID_KEY),
            outcome_2_abbr=d.get(OUTCOME_2_ABBREV_KEY),
            prop_date=d.get(PROP_DATE_KEY),
        )

    def to_dict(self) -> dict:
        return {
            PROPOSITION_ID_KEY: self.proposition_id,
            LINE_KEY: self.home_line,
            PROP_NAME_KEY: self.prop_name,
            GAME_ID_KEY: self.game_id,
            OUTCOME_1_ID_KEY: self.outcome_1_id,
            OUTCOME_1_ABBREV_KEY: self.outcome_1_abbr,
            OUTCOME_2_ID_KEY: self.outcome_2_id,
            OUTCOME_2_ABBREV_KEY: self.outcome_2_abbr,
            PROP_DATE_KEY: self.prop_date,
        }

def get_propositions(espn_propositions_url: Optional[str] = None) -> List[Proposition]:
    """
    Fetches and parses proposition data from the given ESPN URL.

    A proposition is similar to a "bet" and can have multiple bets on a single game.

    Args:
      espn_propositions_url (str): The URL to fetch propositions from.

    Returns:
      list: A list of Proposition dataclass instances, each containing details
        about a proposition. Each instance contains the following fields:
          - proposition_id: The ID of the proposition.
          - home_line: The line or spread of the proposition.
          - prop_name: The name of the proposition.
          - game_id: The ID of the game associated with the proposition.
          - outcome_1_id: The ID of the first possible outcome.
          - outcome_1_abbr: The abbreviation of the first possible outcome.
          - outcome_2_id: The ID of the second possible outcome.
          - outcome_2_abbr: The abbreviation of the second possible outcome.
          - prop_date: The date of the proposition.
    """
    if not espn_propositions_url:
        espn_propositions_url = ESPN_PROPOSITIONS_URL[FOOTBALL_SEASON]
    # Get the ids and lines for all the propositions in the league.
    # A proposition is semantically like a "bet".  It is different from a game
    # since you can have multiple bets on a single game.
    propositions: List[Proposition] = []
    # e.g., 'https://gambit-api.fantasy.espn.com/apis/v1/propositions?challengeId=230&platform=chui&view=chui_default'
    response = requests.get(
        espn_propositions_url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    )
    soup = BeautifulSoup(response.content, "html.parser")
    propositions_json = json.loads(soup.text)
    for one_json_prop in propositions_json:
        prop = Proposition()
        prop.proposition_id = one_json_prop["id"]
        prop.prop_name = one_json_prop["name"]
        for i, possible_outcome in enumerate(one_json_prop["possibleOutcomes"]):
            id = possible_outcome["id"]
            abbrev = possible_outcome["abbrev"]
            if i == 0:
                prop.outcome_1_id = id
                prop.outcome_1_abbr = abbrev
            else:
                prop.outcome_2_id = id
                prop.outcome_2_abbr = abbrev
        if "spread" in one_json_prop:
            prop.home_line = one_json_prop["spread"]
        for val in one_json_prop["mappings"]:
            if val["type"] == "COMPETITION_ID":
                prop.game_id = val["value"]
        prop.prop_date = str(one_json_prop.get("date") or "unknown")
        propositions.append(prop)
    return propositions

def load_propositions_csv() -> List[Proposition]:
    """
    Loads a list of Proposition dataclass instances from a CSV file.

    Returns:
      list: A list of Proposition dataclass instances, each containing details
        about a proposition. Each instance should have fields corresponding to
        PROP_COL_KEYS.

    The CSV file is expected to be in the directory specified by the FOOTBALL_SEASON
    variable with the filename "propositions.csv". The file is expected to be written
    with a header row containing PROP_COL_KEYS, and each subsequent row containing
    the values of each proposition in the order specified by PROP_COL_KEYS.

    Note:
      - The FOOTBALL_SEASON and PROP_COL_KEYS variables must be defined in the
        module's scope.
      - The csv and os modules must be imported.
    """
    propositions: List[Proposition] = []
    with open(
        os.path.join(FOOTBALL_SEASON, "propositions.csv"), "r", newline=""
    ) as csvfile:
        propreader = csv.reader(csvfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        next(propreader)  # Skip the header row
        for row in propreader:
            d = {k: v for k, v in zip(PROP_COL_KEYS, row)}
            propositions.append(Proposition.from_dict(d))
    return propositions

def write_propositions_csv(propositions: List[Proposition]):
    """
    Writes a list of Proposition dataclass instances to a CSV file.

    Args:
      propositions (list of Proposition): A list where each element is a
        Proposition dataclass instance representing a proposition. Each instance
        should have fields corresponding to PROP_COL_KEYS.

    The CSV file is saved in the directory specified by the FOOTBALL_SEASON variable
    with the filename "propositions.csv". The file is written with a header row
    containing PROP_COL_KEYS, and each subsequent row contains the values of each
    proposition in the order specified by PROP_COL_KEYS.

    Note:
      - The FOOTBALL_SEASON and PROP_COL_KEYS variables must be defined in the
        module's scope.
      - The csv and os modules must be imported.
    """
    # Create the directory if it doesn't exist
    os.makedirs(FOOTBALL_SEASON, exist_ok=True)
    with open(
        os.path.join(FOOTBALL_SEASON, "propositions.csv"), "w", newline=""
    ) as csvfile:
        propwriter = csv.writer(csvfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        propwriter.writerow(PROP_COL_KEYS)
        for prop in propositions:
            d = prop.to_dict()
            propwriter.writerow([d[k] for k in PROP_COL_KEYS])


if __name__ == "__main__":
    propositions = get_propositions(
        espn_propositions_url=ESPN_PROPOSITIONS_URL[FOOTBALL_SEASON]
    )
    write_propositions_csv(propositions)
