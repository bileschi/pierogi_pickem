import csv
import os


import espn_picks
import espn_game_results
import players
import propositions
# import morgans_picks

from current_season import FOOTBALL_SEASON


SKIP_LOAD_PICKS = True
SKIP_LOAD_GAMES = True

DEBUG_PRINT = True
def dbprint(*args, **kwargs):
  if DEBUG_PRINT:
    print("§§§", end=" ")
    print(*args, **kwargs)


if __name__ == "__main__":
  # Load the list of "propositions" - the bets that are available for each game.
  if not os.path.exists(os.path.join(FOOTBALL_SEASON, "propositions.csv")):
    props = propositions.get_propositions()
    propositions.write_propositions_csv(propositions)
  else:
    props = propositions.load_propositions_csv()

  # Load picks from ESPN for those who use ESPN.
  # TODO: fix up the filename logic here.
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
  base_games_fn = os.path.join(FOOTBALL_SEASON, 'base_games.csv')
  if not SKIP_LOAD_GAMES:
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
        game[propositions.PROPOSITION_ID_KEY] = prop[propositions.PROPOSITION_ID_KEY]
        game[propositions.CORRECT_OUTCOME_ABBREV_KEY] = prop[propositions.CORRECT_OUTCOME_ABBREV_KEY]
        game[propositions.INCORRECT_OUTCOME_ABBREV_KEY] = prop[propositions.INCORRECT_OUTCOME_ABBREV_KEY]
  dbprint(f"Found {num_alignments_found} alignments between games and propositions.")

  # Fill the games object for players who use ESPN.
  for game in games:
    for k in players.ESPN_PLAYER_IDS.keys():
      for pick in picks[k]:
        if game[propositions.PROPOSITION_ID_KEY] == pick[propositions.PROPOSITION_ID_KEY]:
          if(pick[espn_picks.RESULT_KEY]) == 'CORRECT':
            game[k] = game[propositions.CORRECT_OUTCOME_ABBREV_KEY]
          else:
            game[k] = game[propositions.INCORRECT_OUTCOME_ABBREV_KEY]

  # # Incorporate Morgan's picks.
  # for game in games:
  #   game[MORGAN_PICK_KEY] = morgans_picks.get_morgan_pick(week=game[WEEK_KEY],
  #                   home_team=game[HOME_KEY],
  #                   away_team=game[AWAY_KEY])
  # Add defaults for Sue, Jean, SMB, SLB
  for game in games:
    game[players.SMB_PICK_KEY] = game[players.SMB_PICK_KEY] or game[espn_game_results.HOME_KEY]
    game[players.SLB_PICK_KEY] = game[players.SLB_PICK_KEY] or game[espn_game_results.HOME_KEY]
    game[players.SUE_PICK_KEY] = game[players.SUE_PICK_KEY] or game[espn_game_results.HOME_KEY]
    game[players.JEAN_PICK_KEY] = game[players.JEAN_PICK_KEY] or game[espn_game_results.HOME_KEY]
  espn_game_results.write_games_csv(games, os.path.join(FOOTBALL_SEASON,'games.csv'))
