import csv
import os


import espn_picks
import espn_game_results
import players
import propositions
# import morgans_picks

from current_season import FOOTBALL_SEASON


# week	home	away	line	home_score	away_score	Stanley M	Aunt Sue	Stanley L	Jean	Morgan	game_id

one_game = dict()

def game_as_str(game_dict):
  return(','.join([str(game_dict[k]) for k in espn_game_results.GAME_COL_KEYS]))


SKIP_LOAD_PICKS = True
SKIP_LOAD_GAMES = True

if __name__ == "__main__":
  # Load the list of "propositions" - the bets that are available for each game.
  if not os.path.exists(os.path.join(FOOTBALL_SEASON, "propositions.csv")):
    props = propositions.get_propositions()
    propositions.write_propositions_csv(propositions)
  else:
    props = propositions.load_propositions_csv()

  # Load picks from ESPN for those who use ESPN.
  picks = {}
  if not SKIP_LOAD_PICKS:
    for (player, espn_pick_id) in players.ESPN_PLAYER_IDS.items():
      picks[player] = espn_picks.get_picks(espn_pick_id)
      espn_picks.write_picks_csv(
        picks[player],
        os.path.join(FOOTBALL_SEASON,f'{player}.csv'))
  # Load the picks from disk (even though we just wrote them to disk).
  # This pattern is useful for testing.
  for (player, espn_pick_id) in players.ESPN_PLAYER_IDS.items():
      espn_picks.write_picks_csv(picks[player], f'{player}.csv')

  # Load the actual results from ESPN.
  if not SKIP_LOAD_GAMES:
    games = espn_game_results.get_game_scores()
    espn_game_results.write_games_csv(games, 'base_games.csv')
  # Read the results from disk (even though we just wrote them to disk).
  # Again, this is useful for testing.
  games = espn_game_results.load_games_csv('base_games.csv')
  
  # At this point we are done with network calls.  All can be done locally.

  # Populate lines & picks. A faster, non n^2 way to do this would be to build
  # an index but this dumb way is so much faster than the
  # fetches that it doesn't matter.
  for game in games:
    for prop in propositions:
      if game[GAME_ID_KEY] == prop[GAME_ID_KEY]:
        game[LINE_KEY] = prop[LINE_KEY]
        game[PROPOSITION_ID_KEY] = prop[PROPOSITION_ID_KEY]
        game[CORRECT_OUTCOME_ABBREV_KEY] = prop[CORRECT_OUTCOME_ABBREV_KEY]
        game[INCORRECT_OUTCOME_ABBREV_KEY] = prop[INCORRECT_OUTCOME_ABBREV_KEY]
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
