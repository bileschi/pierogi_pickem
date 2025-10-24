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

# Sept 3 (email)
MANUAL_PICKS[games_col_keys.SLB_PICK_KEY][1] = {
    "PHI",
    "KC",
    "ARI",
    "JAX",
    "CIN",
    "NE",
    "MIA",
    "WSH",
    "PIT",
    "TB",
    "SF",
    "DEN",
    "DET",
    "HOU",
    "BUF",
    "CHI",
}
# Sept 4 (sms)
MANUAL_PICKS[games_col_keys.JEAN_PICK_KEY][1] = {
    "DAL",
}
# Sept 16 (sms)
MANUAL_PICKS[games_col_keys.SUE_PICK_KEY][3] = {
    "MIA",
    "CLE",
    "TEN",
    "MIN",
    "PIT",
    "DAL",
    "SF",
    "KC",
    "BAL",
    "PHI",
    "TB",
    "WSH",
    "ATL",
    "JAX",
    "LAC",
    "SEA",
}
MANUAL_PICKS[games_col_keys.SMB_PICK_KEY][3] = {
    "BUF",
    "CLE",
    "IND",
    "MIN",
    "PIT",
    "PHI",
    "TB",
    "WSH",
    "ATL",
    "JAX",
    "LAC",
    "NO",
    "DAL",
    "SF",
    "KC",
    "BAL",
}
# Week 8
MANUAL_PICKS[games_col_keys.SMB_PICK_KEY][8] = {
    "LAC",
    "ATL",
    "CIN",
    "NE",
    "PHI",
    "BUF",
    "CHI",
    "SF",
    "NO",
    "DEN",
    "TEN",
    "PIT",
    "WSH",
}
MANUAL_PICKS[games_col_keys.ADAM_PICK_KEY][8] = {
    "MIN",
    "ATL",
    "CIN",
    "NE",
    "NYG",
    "BUF",
    "BAL",
    "SF",
    "TB",
    "DAL",
    "IND",
    "PIT",
    "WSH"
}
MANUAL_PICKS[games_col_keys.SUE_PICK_KEY][8] = {
    "LAC",
    "ATL",
    "CIN",
    "NE",
    "NYG",
    "BUF",
    "CHI",
    "SF",
    "TB",
    "DAL",
    "IND",
    "PIT",
    "KC"
}
