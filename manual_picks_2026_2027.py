# Picks[player][week] = set of strings
# If unset, assume no manual pick.
# It is possible to represent picks which are nonsensical if, e.g.,
# somone picked both sides of the same game.  The business logic handling this
# will be managaged later by perhaps assuming no pick was made.

import players
import games_col_keys

from collections import defaultdict

MANUAL_PICKS = {}
for player in players.PLAYER_IDS:
    MANUAL_PICKS[player] = defaultdict(set)

# Week 1
MANUAL_PICKS[games_col_keys.SMB_PICK_KEY][1] = {
    "NE",
    "SF",
    "TB",
    "NO",
    "NYJ",
    "BAL",
    "ATL",
    "CAR",
    "CLE",
    "HOU",
    "MIA",
    "MIN",
    "WSH",
    "ARI",
    "NYG",
    "DEN",
}
