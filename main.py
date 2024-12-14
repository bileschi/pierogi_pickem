import csv
import os


import espn_picks
import espn_game_results
import players
import propositions
# TODO: Get morgan & adams picks in.
# import morgans_picks

from current_season import FOOTBALL_SEASON
from manual_picks_2024_2025 import MANUAL_PICKS

SKIP_LOAD_LINES = False
SKIP_LOAD_PICKS = False
SKIP_LOAD_SCORES = False

DEBUG_PRINT = True
def dbprint(*args, **kwargs):
  if DEBUG_PRINT:
    print("§§§", end=" ")
    print(*args, **kwargs)


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
    player_picks_fns = {player: os.path.join(FOOTBALL_SEASON,f'{player}.csv') for player in players.ESPN_PLAYER_IDS.keys()}
    if not SKIP_LOAD_PICKS:
        for (player, espn_pick_id) in players.ESPN_PLAYER_IDS.items():
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
        espn_game_results.write_games_csv(games, base_games_fn)
    # Read the results from disk (even though we just wrote them to disk).
    # Again, this is useful for testing.
    games = espn_game_results.load_games_csv(base_games_fn)

    # At this point we are done with network calls.  All can be done locally.

    # Fill `games` with the aligned data from `propositions`. A faster, non n^2
    # way to do this would be to build an index but this dumb way is so much
    # faster than the fetches that it doesn't matter.
    num_alignments_found = 0
    for game in games:
        for prop in props:
            if game[propositions.GAME_ID_KEY] == prop[propositions.GAME_ID_KEY]:
                num_alignments_found += 1
                game[propositions.LINE_KEY] = prop[propositions.LINE_KEY]
                game[propositions.PROP_DATE_KEY] = prop[propositions.PROP_DATE_KEY]
                game[propositions.PROPOSITION_ID_KEY] = prop[
                    propositions.PROPOSITION_ID_KEY
                ]
                # TODO: Do I really want to store the outcome IDs in game?
                # isn't that an ESPN detail?
                game[propositions.OUTCOME_1_ID_KEY] = prop[propositions.OUTCOME_1_ID_KEY]
                game[propositions.OUTCOME_1_ABBREV_KEY] = prop[propositions.OUTCOME_1_ABBREV_KEY]
                game[propositions.OUTCOME_2_ID_KEY] = prop[propositions.OUTCOME_2_ID_KEY]
                game[propositions.OUTCOME_2_ABBREV_KEY] = prop[propositions.OUTCOME_2_ABBREV_KEY] 
    dbprint(f"Found {num_alignments_found} alignments between games and propositions.")
    espn_game_results.write_games_csv(games, os.path.join(FOOTBALL_SEASON, "games.csv"))

    # Fill the `bet_win_key` with the code of the team that won the bet.
    for game in games:
        if not game[espn_game_results.HOME_SCORE_KEY] or not game[espn_game_results.AWAY_SCORE_KEY]:
            game[espn_game_results.BET_WIN_KEY] = "not_decided"
            continue
        home_score = float(game[espn_game_results.HOME_SCORE_KEY])
        away_score = float(game[espn_game_results.AWAY_SCORE_KEY])
        home_line = float(game[propositions.LINE_KEY])
        if (home_score + home_line) > away_score:
            game[espn_game_results.BET_WIN_KEY] = game[espn_game_results.HOME_KEY]
        else:
            game[espn_game_results.BET_WIN_KEY] = game[espn_game_results.AWAY_KEY]
    espn_game_results.write_games_csv(games, os.path.join(FOOTBALL_SEASON, "games.csv"))

    # Fill the games object for players who use ESPN.  For these picks we align
    # the proposition ID between games and picks.  Again, this is an n^2 algo,
    # and maps are faster, but it's so much faster than the network call that
    # the simplicity is worth it.
    delim = " "
    espn_suffix = "ESPN"
    for game in games:
      for k in players.ESPN_PLAYER_IDS.keys():
        for pick in picks[k]:
          if game[propositions.PROPOSITION_ID_KEY] == pick[propositions.PROPOSITION_ID_KEY]:
            # We know the player's outcome key
            outcome_id = pick[espn_picks.OUTCOME_ID_KEY]
            if outcome_id == game[propositions.OUTCOME_1_ID_KEY]:
              game[k] = game[propositions.OUTCOME_1_ABBREV_KEY] + delim + espn_suffix
            elif outcome_id == game[propositions.OUTCOME_2_ID_KEY]:
              game[k] = game[propositions.OUTCOME_2_ABBREV_KEY] + delim + espn_suffix

            # if(pick[espn_picks.RESULT_KEY]) == 'CORRECT':
            #   game[k] = game[espn_game_results.BET_WIN_KEY]
            # else:
            #   # If the pick was wrong, we need to get the other team.
            #   if game[espn_game_results.BET_WIN_KEY] == game[espn_game_results.HOME_KEY]:
            #     game[k] = game[espn_game_results.AWAY_KEY]
            #   else:
            #      game[k] = game[espn_game_results.HOME_KEY]
    espn_game_results.write_games_csv(games, os.path.join(FOOTBALL_SEASON, "games.csv"))

    # Fill manual picks.  Manual picks override default or ESPN picks.
    manual_suffix = "MANUAL"
    dbprint("Incorporating manual picks.")
    num_manual_picks_matched = 0
    for game in games:
      for player in players.PLAYER_IDS:
        # Check if this player has a manual pick for this game.
        week = int(game[espn_game_results.WEEK_KEY])
        home_team = game[espn_game_results.HOME_KEY]
        away_team = game[espn_game_results.AWAY_KEY]        
        manual_home_pick = home_team in MANUAL_PICKS[player][week]
        manual_away_pick = away_team in MANUAL_PICKS[player][week]
        if manual_home_pick and manual_away_pick:
            print(f"Error: Player {player} has both {home_team} and {away_team} in their manual picks for week {week}.")
        if manual_home_pick:
            num_manual_picks_matched += 1
            game[player] = home_team + delim + manual_suffix
        if manual_away_pick:
            num_manual_picks_matched += 1
            game[player] = home_team + delim + manual_suffix
    espn_game_results.write_games_csv(games, os.path.join(FOOTBALL_SEASON, "games.csv"))
    dbprint(f"Matched {num_manual_picks_matched} manual picks.")    

    # Fill manual picks.  Manual picks override default or ESPN picks.
    default_suffix = "DEFAULT"
    dbprint("Incorporating manual picks.")
    num_default_picks_made = 0
    for game in games:
      for player in players.PLAYER_IDS:
        # Check if the player already has a pick.
        if game[player]:
          continue
        # If not, make a pick based on the player's strategy
        def_pick = players.DEFAULT_STRATEGY[player](game)
        game[player] = def_pick + delim + default_suffix
        num_default_picks_made += 1
        espn_game_results.write_games_csv(games, os.path.join(FOOTBALL_SEASON, "games.csv"))
    dbprint(f"Made {num_default_picks_made} default picks.")    

    # TODO: Incorporate Default picks.
    # # Incorporate Morgan's picks.
    # for game in games:
    #   game[MORGAN_PICK_KEY] = morgans_picks.get_morgan_pick(week=game[WEEK_KEY],
    #                   home_team=game[HOME_KEY],
    #                   away_team=game[AWAY_KEY])
    # Add defaults for Sue, Jean, SMB, SLB
    # for game in games:
    #   game[players.SMB_PICK_KEY] = game[players.SMB_PICK_KEY] or game[espn_game_results.HOME_KEY]
    #   game[players.SLB_PICK_KEY] = game[players.SLB_PICK_KEY] or game[espn_game_results.HOME_KEY]
    #   game[players.SUE_PICK_KEY] = game[players.SUE_PICK_KEY] or game[espn_game_results.HOME_KEY]
    #   game[players.JEAN_PICK_KEY] = game[players.JEAN_PICK_KEY] or game[espn_game_results.HOME_KEY]
    # espn_game_results.write_games_csv(games, os.path.join(FOOTBALL_SEASON,'games.csv'))

