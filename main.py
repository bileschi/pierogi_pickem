from dataclasses import dataclass, asdict, field
from typing import Optional, Dict

import csv
import os

import espn_picks
import espn_game_results
import games_col_keys
import players
import propositions
# TODO: Get morgan & adams picks in.
# import morgans_picks

from current_season import FOOTBALL_SEASON
#from manual_picks_2024_2025 import MANUAL_PICKS
from manual_picks_2025_2026 import MANUAL_PICKS

SKIP_LOAD_LINES = False
SKIP_LOAD_PICKS = False
SKIP_LOAD_SCORES = False

DEBUG_PRINT = True
def dbprint(*args, **kwargs):
  if DEBUG_PRINT:
    print("§§§", end=" ")
    print(*args, **kwargs)

@dataclass
class Game:
    week: Optional[str] = None
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    game_id: Optional[str] = None
    home_score: Optional[str] = None
    away_score: Optional[str] = None
    home_line: Optional[str] = None
    prop_date: Optional[str] = None
    proposition_id: Optional[str] = None
    outcome_1_id: Optional[str] = None
    outcome_1_abbr: Optional[str] = None
    outcome_2_id: Optional[str] = None
    outcome_2_abbr: Optional[str] = None
    bet_win_key: Optional[str] = None
    # Player picks will be stored here
    picks: Dict[str, Optional[str]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> "Game":
        known_fields = {
            'week', 'home_team', 'away_team', 'game_id', 'home_score', 'away_score',
            'home_line', 'prop_date', 'proposition_id', 'outcome_1_id', 'outcome_1_abbr',
            'outcome_2_id', 'outcome_2_abbr', 'bet_win_key'
        }
        picks = {k: v for k, v in d.items() if k not in known_fields}
        return cls(
            week=d.get('week'),
            home_team=d.get('home_team'),
            away_team=d.get('away_team'),
            game_id=d.get('game_id'),
            home_score=d.get('home_score'),
            away_score=d.get('away_score'),
            home_line=d.get('home_line'),
            prop_date=d.get('prop_date'),
            proposition_id=d.get('proposition_id'),
            outcome_1_id=d.get('outcome_1_id'),
            outcome_1_abbr=d.get('outcome_1_abbr'),
            outcome_2_id=d.get('outcome_2_id'),
            outcome_2_abbr=d.get('outcome_2_abbr'),
            bet_win_key=d.get('bet_win_key'),
            picks=picks
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        picks = d.pop('picks', {})
        d.update(picks)
        return d

def load_games_csv(filename) -> list:
    games = []
    with open(filename, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            games.append(Game.from_dict(row))
    return games

def write_games_csv(games, filename):
    if not games:
        return
    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(games[0].to_dict().keys()))
        writer.writeheader()
        for game in games:
            writer.writerow(game.to_dict())

if __name__ == "__main__":
    # Load the list of "propositions" - the bets that are available for each game.
    # Writes propositions.csv
    if not SKIP_LOAD_LINES:
        dbprint("Fetching lines from ESPN.")
        props = propositions.get_propositions()
        propositions.write_propositions_csv(props)
    # Read the propositions from disk (even though we just wrote them to disk).
    dbprint("Loading propositions.")
    props = propositions.load_propositions_csv()

    # Load picks from ESPN for those who use ESPN.
    # TODO: fix up the filename logic here.
    # Writes {player}_pick.csv
    picks = {}
    dbprint("Loading player picks.")
    player_picks_fns = {player: os.path.join(FOOTBALL_SEASON,f'{player}.csv') for player in players.ESPN_PLAYER_IDS.keys()}
    if not SKIP_LOAD_PICKS:
        for (player, espn_pick_id) in players.ESPN_PLAYER_IDS.items():
            dbprint(f"Fetching picks for player {player} from ESPN.")
            picks[player] = espn_picks.get_picks(espn_pick_id)
            espn_picks.write_picks_csv(
                picks[player],
                player_picks_fns[player])
    # Load the picks from disk (even though we just wrote them to disk).
    # This pattern is useful for testing.
    for (player, espn_pick_id) in players.ESPN_PLAYER_IDS.items():
        picks[player] = espn_picks.read_picks_csv(player_picks_fns[player])

    # Load the actual results from ESPN.
    # Writes base_games.csv
    base_games_fn = os.path.join(FOOTBALL_SEASON, 'base_games.csv')
    if not SKIP_LOAD_SCORES:
        games = espn_game_results.get_game_scores()
        write_games_csv([Game.from_dict(g) for g in games], base_games_fn)
    # Read the results from disk (even though we just wrote them to disk).
    # Again, this is useful for testing.
    games = load_games_csv(base_games_fn)

    # At this point we are done with network calls.  All can be done locally.

    # Fill `games` with the aligned data from `propositions`.
    num_alignments_found = 0
    for game in games:
        for prop in props:
            if game.game_id == prop.game_id:
                num_alignments_found += 1
                game.home_line = prop.home_line
                game.prop_date = prop.prop_date
                game.proposition_id = prop.proposition_id
                game.outcome_1_id = prop.outcome_1_id
                game.outcome_1_abbr = prop.outcome_1_abbr
                game.outcome_2_id = prop.outcome_2_id
                game.outcome_2_abbr = prop.outcome_2_abbr
    dbprint(f"Found {num_alignments_found} alignments between games and propositions.")
    write_games_csv(games, os.path.join(FOOTBALL_SEASON, "games.csv"))

    # Fill the `bet_win_key` with the code of the team that won the bet.
    for game in games:
        if not game.home_score or not game.away_score:
            game.bet_win_key = "not_decided"
            continue
        home_score = float(game.home_score)
        away_score = float(game.away_score)
        home_line = float(game.home_line) if game.home_line else 0.0
        if (home_score + home_line) > away_score:
            game.bet_win_key = game.home_team
        else:
            game.bet_win_key = game.away_team
    write_games_csv(games, os.path.join(FOOTBALL_SEASON, "games.csv"))

    # Fill the games object for players who use ESPN.
    delim = " "
    espn_suffix = "ESPN"
    for game in games:
        for k in players.ESPN_PLAYER_IDS.keys():
            for pick in picks[k]:
                if game.proposition_id == pick[propositions.PROPOSITION_ID_KEY]:
                    outcome_id = pick[espn_picks.OUTCOME_ID_KEY]
                    if outcome_id == game.outcome_1_id:
                        game.picks[k] = (game.outcome_1_abbr or "") + delim + espn_suffix
                    elif outcome_id == game.outcome_2_id:
                        game.picks[k] = (game.outcome_2_abbr or "") + delim + espn_suffix
    write_games_csv(games, os.path.join(FOOTBALL_SEASON, "games.csv"))

    # Fill manual picks.  Manual picks override default or ESPN picks.
    manual_suffix = "MANUAL"
    dbprint("Incorporating manual picks.")
    num_manual_picks_matched = 0
    for game in games:
        for player in players.PLAYER_IDS:
            week = int(game.week) if game.week else 0
            home_team = game.home_team
            away_team = game.away_team
            manual_home_pick = home_team in MANUAL_PICKS[player][week]
            manual_away_pick = away_team in MANUAL_PICKS[player][week]
            if manual_home_pick and manual_away_pick:
                print(f"Error: Player {player} has both {home_team} and {away_team} in their manual picks for week {week}.")
            if manual_home_pick:
                num_manual_picks_matched += 1
                game.picks[player] = (home_team or "") + delim + manual_suffix
            if manual_away_pick:
                num_manual_picks_matched += 1
                game.picks[player] = (away_team or "") + delim + manual_suffix
    write_games_csv(games, os.path.join(FOOTBALL_SEASON, "games.csv"))
    dbprint(f"Matched {num_manual_picks_matched} manual picks.")

    # Fill default picks for players who don't have a pick yet.
    default_suffix = "DEFAULT"
    dbprint("Incorporating default picks.")
    num_default_picks_made = 0
    for game in games:
        for player in players.PLAYER_IDS:
            if game.picks.get(player):
                continue
            def_pick = players.DEFAULT_STRATEGY[player](game)
            game.picks[player] = def_pick + delim + default_suffix
            num_default_picks_made += 1
        write_games_csv(games, os.path.join(FOOTBALL_SEASON, "games.csv"))
    dbprint(f"Made {num_default_picks_made} default picks.")

    # TODO: Incorporate Morgan's picks and other logic

