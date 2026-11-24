"""Keeps point spreads stable across pipeline runs and records their history.

main.py re-fetches every line from ESPN on each run. This module guards that:

* A line we already have is never replaced by a blank one (ESPN sometimes
  returns propositions without a `spread`, or none at all for a week).
* Once a game has kicked off, its line is frozen at the last value we had,
  so a later change on ESPN's side cannot re-score a game.
* Every time the line ESPN reports (or the line we use) changes for a game,
  a row is appended to `<season>/line_history.csv`, so we can see when
  lines first appear and whether they ever move.
"""
import csv
import os
import time
from datetime import datetime
from typing import Dict, List, Optional

try:
    import pytz
    nyc_timezone = pytz.timezone('America/New_York')
except ImportError:
    from zoneinfo import ZoneInfo
    nyc_timezone = ZoneInfo('America/New_York')

HISTORY_COLS = (
    'recorded_at_et', 'week', 'game_id', 'away_team', 'home_team',
    'espn_line', 'used_line', 'prop_date', 'note',
)


def _blank(value: Optional[str]) -> bool:
    return value is None or str(value).strip() in ('', 'None', 'nan')


def _same_line(a: Optional[str], b: Optional[str]) -> bool:
    if _blank(a) or _blank(b):
        return _blank(a) and _blank(b)
    try:
        return float(a) == float(b)
    except ValueError:
        return str(a).strip() == str(b).strip()


def _has_kicked_off(game, now_ms: float) -> bool:
    if game.game_status in ('in', 'post'):
        return True
    try:
        return bool(game.prop_date) and now_ms >= float(game.prop_date)
    except ValueError:
        return False


def load_previous_games(games_csv_path: str) -> Dict[str, dict]:
    """Returns {game_id: row} from the previous run's games.csv, if any."""
    if not os.path.exists(games_csv_path):
        return {}
    with open(games_csv_path, newline='') as f:
        return {row['game_id']: row for row in csv.DictReader(f) if row.get('game_id')}


def stabilize_lines(games: list, previous: Dict[str, dict], now_ms: Optional[float] = None) -> Dict[str, dict]:
    """Applies the keep-previous and freeze-at-kickoff rules to `games` in place.

    Must be called right after games are aligned with fresh ESPN propositions.
    Returns {game_id: {'espn_line': ..., 'note': ...}} for history logging.
    """
    if now_ms is None:
        now_ms = time.time() * 1000
    report = {}
    for game in games:
        espn_line = game.home_line
        note = ''
        prev = previous.get(game.game_id) or {}
        prev_line = prev.get('home_line')

        if _blank(game.prop_date) and not _blank(prev.get('prop_date')):
            game.prop_date = prev.get('prop_date')

        if not _blank(prev_line):
            if _has_kicked_off(game, now_ms) and not _same_line(espn_line, prev_line):
                game.home_line = prev_line
                note = 'frozen_at_kickoff'
            elif _blank(espn_line):
                game.home_line = prev_line
                note = 'espn_blank_kept_previous'
        if _blank(game.home_line):
            game.home_line = ''
            note = note or 'no_line'
        report[game.game_id] = {'espn_line': '' if _blank(espn_line) else espn_line, 'note': note}
    return report


def append_line_history(games: list, report: Dict[str, dict], history_path: str) -> int:
    """Appends a row for each game whose ESPN or used line changed since the
    last recorded row. Returns the number of rows written."""
    last: Dict[str, dict] = {}
    exists = os.path.exists(history_path)
    if exists:
        with open(history_path, newline='') as f:
            for row in csv.DictReader(f):
                last[row['game_id']] = row

    now_et = datetime.now(nyc_timezone).strftime('%Y-%m-%d %H:%M:%S %Z')
    rows = []
    for game in games:
        info = report.get(game.game_id, {})
        espn_line = info.get('espn_line', '')
        used_line = game.home_line or ''
        prev = last.get(game.game_id)
        if prev and _same_line(prev.get('espn_line'), espn_line) and _same_line(prev.get('used_line'), used_line):
            continue
        rows.append({
            'recorded_at_et': now_et,
            'week': game.week,
            'game_id': game.game_id,
            'away_team': game.away_team,
            'home_team': game.home_team,
            'espn_line': espn_line,
            'used_line': used_line,
            'prop_date': game.prop_date or '',
            'note': info.get('note', ''),
        })

    if rows:
        os.makedirs(os.path.dirname(history_path) or '.', exist_ok=True)
        with open(history_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=HISTORY_COLS)
            if not exists:
                writer.writeheader()
            writer.writerows(rows)
    return len(rows)
