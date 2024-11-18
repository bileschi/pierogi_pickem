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

# Sept 2 (text)
MANUAL_PICKS[players.MORGAN_PICK_KEY][1] = {
    "BAL",
    "PHI",
    "ATL",
    "BUF",
    "CHI",
    "NE",
    "HOU",
    "MIA",
    "NO",
    "MIN",
    "LAC",
    "SEA",
    "DAL",
    "TB",
    "DET",
    "NYJ",
}
# Sept 5 (text)
MANUAL_PICKS[players.ADAM_PICK_KEY][1] = {
    "KC",
    "PHIL",
    "ATL",
    "BUF",
    "TEN",
    "CIN",
    "HOU",
    "NO",
    "MIN",
    "LV",
    "DEN",
    "DAL",
    "TB",
    "SF",
}
# Sept 15 (text)
MANUAL_PICKS[players.MORGAN_PICK_KEY][2] = {
    "DAL",
    "DET",
    "IND",
    "NYJ",
    "SF",
    "NE",
    "WAS",
    "LAC",
    "JAX",
    "BAL",
    "LAR",
    "PIT",
    "KC",
    "CHI",
    "PHI",
}
# Sept 19 (text)
MANUAL_PICKS[players.MORGAN_PICK_KEY][3] = {
    "NYJ",
    "CLE",
    "GB",
    "CHI",
    "MIN",
    "NO",
    "PIT",
    "TB",
    "LV",
    "SEA",
    "BAL",
    "SF",
    "DET",
    "KC",
    "BUF",
    "WAS",
}
# Sept 24 (text)
MANUAL_PICKS[players.ADAM_PICK_KEY][4] = {
    "DAL",
    "NO",
    "LAC",
    "MIN",
    "PIT",
    "DEN",
    "PHIL",
    "CIN",
    "HOU",
    "WAS",
    "SF",
    "LV",
    "KC",
    "BUF",
    "MIA",
    "DET",
}
# Sept 29 (text)
MANUAL_PICKS[players.MORGAN_PICK_KEY][4] = {
    "NO",
    "LAR",
    "MIN",
    "PIT",
    "NYJ",
    "PHI",
    "CAR",
    "HOU",
    "ARI",
    "SF",
    "CLE",
    "LAC",
    "BUF",
    "MIA",
}
# Oct 06 (text)
MANUAL_PICKS[players.MORGAN_PICK_KEY][5] = {
    "CHI",
    "BAL",
    "NE",
    "WAS",
    "IND",
    "BUF",
    "DEN",
    "ARI",
    "GB",
    "SEA",
    "PIT",
    "NO",
}
# Oct 10 (text)
MANUAL_PICKS[players.MORGAN_PICK_KEY][6] = {
    "CHI",
    "GB",
    "IND",
    "HOU",
    "TB",
    "CHI",
    "WAS",
    "LAC",
    "PIT",
    "DET",
    "ATL",
    "CIN",
    "BUF",
}
# Oct 20 (text)
MANUAL_PICKS[players.MORGAN_PICK_KEY][7] = {
    "ATL",
    "BUF",
    "CHI",
    "GB",
    "MIA",
    "MIN",
    "PHI",
    "LAR",
    "WAS",
    "KC",
    "NYJ",
    "BAL",
    "LAC",
}
# Oct 24 (text)
MANUAL_PICKS[players.MORGAN_PICK_KEY][8] = {
    "MIN",
    "BAL",
    "DET",
    "MIA",
    "NE",
    "ATL",
    "GB",
    "HOU",
    "PHI",
    "NO",
    "BUF",
    "CHI",
    "DEN",
    "KC",
    "SF",
    "PIT",
}
# Nov 10 (text)
MANUAL_PICKS[players.MORGAN_PICK_KEY][10] = {
    "CHI",
    "BUF",
    "KC",
    "ATL",
    "TB",
    "WAS",
    "MIN",
    "LAC",
    "PHI",
    "NYJ",
    "DET",
    "LAR",
}
# Nov 11 (email)
MANUAL_PICKS[players.SLB_PICK_KEY][10] = {
    "CIN",
    "NYG",
    "TB",
    "MIN",
    "CHI",
    "BUF",
    "KC",
    "NO",
    "PIT",
    "TEN",
    "DAL",
    "NYJ",
    "DET",
    "MIA",
}
