# Picks[player][week] = set of strings
# If unset, assume no manual pick.
# It is possible to represent picks which are nonsensical if, e.g.,
# somone picked both sides of the same game.  The business logic handling this
# will be managaged later by perhaps assuming no pick was made.

import players

from collections import defaultdict

MANUAL_PICKS = {}
for player in players.PLAYER_IDS:
    MANUAL_PICKS[player] = defaultdict(set)

# Sept 3 (email)
MANUAL_PICKS[players.SLB_PICK_KEY][1] = {
    "PHI",
    "KC",
    "ARI",
    "JAX",
    "CIN",
    "NE",
    "MIA",
    "WAS",
    "PIT",
    "TB",
    "SF",
    "DEN",
    "DET",
    "HOU",
    "BUF",
    "CHI",
}
