import csv
import enum
import os
import shutil
from typing import Any, Dict
import pytz

from collections import defaultdict
from datetime import datetime
from current_season import FOOTBALL_SEASON
from players import PLAYER_DISPLAY_NAMES

# TODO: Move this to the players module.
players = ['smb', 'slb', 'sue', 'jean', 'morgan', 'adam', 'constance', 'max']

# TODO: Make the csv files a command line argument.

class BetResult(enum.Enum):
    UNDECIDED = enum.auto()
    WIN = enum.auto()
    LOSE = enum.auto()
    TIE = enum.auto()

def get_image_path(team_code):
    """Constructs the image path for a team code."""
    if team_code and team_code != "?":
        return f"images2/nfl/{team_code}.png"
    else:
        return None


def read_csv(filename):
    """Reads the CSV file and returns a list of games."""
    games = []
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader]
    return games

def generate_weekly_results(games):
    """Generates weekly results with winners and scores."""
    weekly_results : Dict[int, Dict[str, Any]] = defaultdict(lambda: {'games': [], 'scores': defaultdict(int)})
    for game in games:
        week = int(game['week'])
        weekly_results[week]['games'].append(game)
        for player in players:
            pick = game[f'{player}_pick'].split(' ')[0]
            if pick == game['bet_win_key']:
                weekly_results[week]['scores'][player] += 1
    return weekly_results

def find_current_week(weekly_results):
    """Finds the current week: the first week with any incomplete games,
    or the last week if all games are complete."""
    weeks = sorted(weekly_results.keys())
    for week in weeks:
        for game in weekly_results[week]['games']:
            if not game['away_score'] or not game['home_score']:
                return week
    return weeks[-1] if weeks else None

def generate_html(weekly_results):
    """Generates the HTML for the website."""
    nyc_timezone = pytz.timezone('America/New_York')
    timestamp = datetime.now(nyc_timezone).strftime('%Y-%m-%d %H:%M:%S')
    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <title>Bileschi Family Pierogi Pigskin Pick'em</title>
    <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 16px;
      color: #1e293b;
      background-color: #f8fafc;
      margin: 0;
      padding: 24px;
    }
    .header-card {
      background: linear-gradient(135deg, #0f355e 0%, #1b4b7a 100%);
      color: #ffffff;
      padding: 24px 28px;
      border-radius: 12px;
      box-shadow: 0 4px 14px rgba(15, 53, 94, 0.15);
      margin-bottom: 24px;
    }
    .header-card h1 {
      margin: 0 0 10px 0;
      font-size: 2.2em;
      font-weight: 800;
      letter-spacing: -0.5px;
    }
    .header-meta {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 12px;
      font-size: 0.9em;
    }
    .season-badge {
      display: inline-block;
      background: rgba(255, 255, 255, 0.2);
      padding: 3px 10px;
      border-radius: 12px;
      font-weight: 600;
      letter-spacing: 0.3px;
    }
    .last-updated {
      color: #cbd5e1;
    }
    .legend-bar {
      margin-top: 14px;
      padding-top: 12px;
      border-top: 1px solid rgba(255, 255, 255, 0.2);
      font-size: 0.9em;
      line-height: 1.6;
      color: #e2e8f0;
    }
    .legend-note {
      color: #cbd5e1;
      margin-left: 6px;
    }
    .badge {
      font-size: 0.65em;
      font-weight: 600;
      padding: 1px 4px;
      border-radius: 3px;
      display: inline-block;
      vertical-align: 1px;
      line-height: 1.1;
      letter-spacing: 0.3px;
    }
    .badge-site {
      background: #ecfdf5;
      color: #047857;
      border: 1px solid #a7f3d0;
    }
    .badge-manual {
      background: #e0f2fe;
      color: #0369a1;
      border: 1px solid #bae6fd;
    }
    .badge-espn {
      background: #fef2f2;
      color: #b91c1c;
      border: 1px solid #fecaca;
    }
    .badge-default {
      background: #f1f5f9;
      color: #94a3b8;
      border: 1px solid #e2e8f0;
    }
    .header-card .badge-site {
      background: rgba(52, 211, 153, 0.2);
      color: #6ee7b7;
      border: 1px solid rgba(52, 211, 153, 0.35);
    }
    .header-card .badge-manual {
      background: rgba(56, 189, 248, 0.2);
      color: #7dd3fc;
      border: 1px solid rgba(56, 189, 248, 0.35);
    }
    .header-card .badge-espn {
      background: rgba(239, 68, 68, 0.2);
      color: #fca5a5;
      border: 1px solid rgba(239, 68, 68, 0.35);
    }
    .header-card .badge-default {
      background: rgba(255, 255, 255, 0.12);
      color: #cbd5e1;
      border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .legend-note {
      color: #cbd5e1;
      font-size: 0.85em;
    }
    h2 {
      color: #0f355e;
      font-size: 1.5em;
      margin: 24px 0 10px 0;
      letter-spacing: -0.3px;
    }
    .leaderboard-table {
      font-size: 16px;
      width: 100%;
      max-width: 520px;
      border-collapse: collapse;
      background: #ffffff;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .leaderboard-table th, .leaderboard-table td {
      border: 1px solid #e2e8f0;
      padding: 10px 14px;
      text-align: center;
    }
    .leaderboard-table th {
      background: linear-gradient(135deg, #0f355e, #1b4b7a);
      color: #fff;
      letter-spacing: 0.6px;
      text-transform: uppercase;
      font-size: 0.85em;
      font-weight: 700;
    }
    .leader-row {
      background: #fef08a !important;
      font-weight: bold;
      border: 2px solid #eab308;
      animation: pop 0.7s;
    }
    .leaderboard-table tr:nth-child(even):not(.leader-row) {
      background: #f8fafc;
    }
    .rank-cell {
      font-weight: bold;
      font-size: 1.05em;
      width: 4em;
    }
    .score-cell {
      font-weight: 700;
      font-size: 1.1em;
    }
    .table-responsive {
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      border-radius: 6px;
    }
    table.week-table {
      border-collapse: collapse;
      width: 100%;
      min-width: 780px;
      font-size: 14px;
      background: #ffffff;
    }
    table.week-table th, table.week-table td {
      border: 1px solid #e2e8f0;
      padding: 4px 6px;
      text-align: center;
    }
    table.week-table tbody tr {
      height: 56px;
      transition: background-color 0.15s ease;
    }
    table.week-table tbody tr:nth-child(even) {
      background: #f8fafc;
    }
    table.week-table tbody tr:hover {
      background: #e2edfb !important;
    }
    table.week-table th {
      background: #eef5ff;
      color: #0f355e;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      font-weight: 700;
      padding: 8px 6px;
    }
    .matchup-logos {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
    }
    .at-symbol {
      color: #94a3b8;
      font-size: 0.9em;
      font-weight: 600;
    }
    .matchup-text {
      font-size: 0.85em;
      color: #475569;
      margin-top: 2px;
      font-weight: 500;
    }
    .time-pill {
      display: inline-block;
      background: #f1f5f9;
      color: #475569;
      padding: 3px 10px;
      border-radius: 12px;
      font-size: 0.85em;
      font-weight: 600;
      white-space: nowrap;
    }
    .final-score {
      font-weight: 700;
      font-size: 1.05em;
      color: #0f172a;
    }
    .correct_pick {
      background-color: #bbf7d0 !important;
    }
    .incorrect_pick {
      background-color: #f1f5f9 !important;
      filter: grayscale(100%) opacity(65%);
    }
    .tie {
      background: repeating-linear-gradient(
        45deg,
        #bbf7d0,
        #bbf7d0 10px,
        #f1f5f9 10px,
        #f1f5f9 20px
      ) !important;
    }
    .winner {
      font-weight: bold;
    }
    .default_pick {
      color: #64748b; 
    }
    .totals-row {
      font-size: 1.15em;
      font-weight: bold;
      background: #fef9c3 !important;
      border-top: 2px solid #cbd5e1;
    }
    .totals-row td {
      padding: 8px 6px;
    }
    .totals-max {
      background: #fde047 !important;
      color: #0f172a;
      box-shadow: 0 0 6px rgba(250, 204, 21, 0.6);
      font-size: 1.25em;
      font-weight: 800;
      animation: pop 0.7s;
    }
    @keyframes pop {
      0% { transform: scale(1.05);}
      70% { transform: scale(1.12);}
      100% { transform: scale(1);}
    }
    summary {
      font-size: 1.25em;
      font-weight: 700;
      cursor: pointer;
      background: #eef5ff;
      color: #0f355e;
      padding: 10px 16px;
      border-radius: 8px;
      margin-bottom: 6px;
      letter-spacing: 0.3px;
      user-select: none;
    }
    details {
      margin-bottom: 18px;
      border: 1px solid #d4e3f5;
      border-radius: 8px;
      padding: 6px 12px 12px 12px;
      background: #ffffff;
      box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    img {
      height: 44px;
      width: 44px;
      vertical-align: middle;
    }
    .greyscale-img {
      opacity: 0.45;
      filter: grayscale(100%);
    }
    </style>
    </head>
    <body>
    <div class="header-card">
      <h1>🥟 Bileschi Family Pierogi Pigskin Pick'em 🏈</h1>
      <div class="header-meta">
        <span class="season-badge">""" + FOOTBALL_SEASON.replace("_", "–") + """ Season</span>
        <span class="last-updated">⏱️ Last updated: """ + timestamp + """ (East Coast)</span>
      </div>
      <div class="legend-bar">
        User made pick : <span class="badge badge-site">S</span> On Site, <span class="badge badge-espn">E</span> On ESPN, <span class="badge badge-manual">M</span> Manually, <span class="badge badge-default">D</span> Via their defaults. <span class="legend-note">Please contact Stan to change how you make default picks (e.g., all home).</span>
      </div>
      <div style="margin-top: 14px;">
        <a href="pick.html" style="display: inline-flex; align-items: center; gap: 6px; background: #2563eb; color: #ffffff; text-decoration: none; font-weight: 600; font-size: 0.88rem; padding: 7px 16px; border-radius: 9999px; box-shadow: 0 2px 8px rgba(37,99,235,0.3); transition: background 0.15s;">🏈 Make Your Picks →</a>
      </div>
    </div>
    """

    # Generate overall leaderboard
    leaderboard = defaultdict(int)
    for week, results in weekly_results.items():
        for player in players:
            score = results['scores'][player]
            leaderboard[player] += score

    # Prepare leaderboard sorted list with ranks
    sorted_leaderboard = sorted(
        leaderboard.items(), key=lambda item: item[1], reverse=True
    )
    max_score = sorted_leaderboard[0][1] if sorted_leaderboard else None

    html += '<h2>Leaderboard</h2>'
    html += '<div class="leaderboard-container">'
    html += '<table class="leaderboard-table" style="table-layout: fixed; width: 500px;">'
    html += '<tr><th>Rank</th><th>Player</th><th>Total Score</th></tr>'
    rank = 1
    prev_score = None
    for idx, (player, score) in enumerate(sorted_leaderboard):
        # 2. Rank numbers and tie handling
        if prev_score is not None and score < prev_score:
            rank = idx + 1
        prev_score = score
        # 1 & 3. Gold background and larger font for leader(s) (only when season has started)
        has_started = (max_score is not None and max_score > 0)
        row_class = "leader-row" if (has_started and score == max_score and rank == 1) else ""
        # 2. Add emoji for top 3 (only when games have been scored)
        rank_display = f"{rank}"
        if has_started:
            if rank == 1:
                rank_display = "1 👑"
            elif rank == 2:
                rank_display = "2 🥈"
            elif rank == 3:
                rank_display = "3 🥉"
        html += f'<tr class="{row_class}">'
        html += f'<td class="rank-cell">{rank_display}</td>'
        html += f'<td>{PLAYER_DISPLAY_NAMES.get(player, player)}</td>'
        html += f'<td class="score-cell">{score}</td>'
        html += '</tr>'
    html += '</table></div>'

    # Find the current week for expansion
    current_week = find_current_week(weekly_results)

    # Generate weekly results, each in a collapsible <details> element
    for week, results in sorted(weekly_results.items()):
        if results['scores']:
            winner = max(results['scores'], key=results['scores'].get)
        else:
            winner = None

        # Find the max score(s) for the totals row for this week
        max_score = max(results['scores'].values()) if results['scores'] else None

        open_attr = " open" if week == current_week else ""
        html += f'<details id="week{week}"{open_attr}>'
        html += f'<summary>Week {week}</summary>'
        html += '<div class="table-responsive">'
        html += '<table class="week-table">'
        # Table Header
        player_headers = ''.join(f'<th>{PLAYER_DISPLAY_NAMES.get(p, p)}</th>' for p in players)
        html += f'<thead><tr><th>Game</th><th>Result</th>{player_headers}</tr></thead>\n'
        html += '<tbody>\n'
        for game in results['games']:
            html += '<tr>'
            line_str = game['home_line']
            if line_str and line_str[0] != '-':
                line_str = '+' + line_str
            # Game illustration
            away_team_img_path = get_image_path(game['away_team'])
            home_team_img_path = get_image_path(game['home_team'])
            html += "<td>"
            if away_team_img_path and home_team_img_path:
                html += f"<div class='matchup-logos'><img src='{away_team_img_path}' alt='{game['away_team']}' title='{game['away_team']}'>"
                html += f"<span class='at-symbol'>@</span>"
                html += f"<img src='{home_team_img_path}' alt='{game['home_team']}' title='{game['home_team']}'></div>"
            html += f"<div class='matchup-text'>{game['away_team']} @ {game['home_team']} {line_str}</div>"
            html += "</td>"

            if game['away_score'] and game['home_score']:
                html += f"<td><div class='final-score'>{game['away_score']} — {game['home_score']}</div></td>"
            else:
                game_day_datetime = datetime.fromtimestamp(int(game['prop_date'])//1000, tz=nyc_timezone)
                game_day_string = game_day_datetime.strftime('%a %b %d · %-I%p')
                html += f"<td><span class='time-pill'>{game_day_string}</span></td>"
            for player in players:
                pick, source = game[f'{player}_pick'].split(' ')
                pick_team_img_path = get_image_path(pick)
                if pick == "":
                    pick = "?"
                classes = []
                img_classes = []
                bet_status = BetResult.UNDECIDED
                if game['away_score'] and game['home_score']:
                    diff_w_line = float(game['home_score']) + float(game['home_line']) - float(game['away_score'])
                    if diff_w_line > 0:
                        winner_team = game['home_team']
                    elif diff_w_line == 0:
                        winner_team = 'TIE'
                    else:
                        winner_team = game['away_team']
                    if pick == winner_team:
                        bet_status = BetResult.WIN
                    elif winner_team == 'TIE':
                        bet_status = BetResult.TIE
                    else:
                        bet_status = BetResult.LOSE
                if bet_status == BetResult.WIN:
                    classes.append('correct_pick')
                if bet_status == BetResult.LOSE:
                    classes.append('incorrect_pick')
                if bet_status == BetResult.TIE:
                    classes.append('tie')
                if bet_status == BetResult.UNDECIDED:
                    classes.append('undecided')
                pick_team = pick
                pick_display = pick
                if source == "DEFAULT":
                    classes.append('default_pick')
                    pick_display = f"{pick}&nbsp;<span class='badge badge-default'>D</span>"
                    if bet_status == BetResult.UNDECIDED:
                        img_classes.append("greyscale-img")
                if source == "SITE":
                    classes.append('site_pick')
                    pick_display = f"{pick}&nbsp;<span class='badge badge-site'>S</span>"
                if source == "MANUAL":
                    classes.append('manual_pick')
                    pick_display = f"{pick}&nbsp;<span class='badge badge-manual'>M</span>"
                if source == "ESPN":
                    classes.append('espn_pick')
                    pick_display = f"{pick}&nbsp;<span class='badge badge-espn'>E</span>"

                html += f"<td class='{ ' '.join(classes)}'>"
                if pick_team_img_path:
                    html += f"<img src='{pick_team_img_path}' alt='{pick_team}' title='{pick_team}' class='{ ' '.join(img_classes) }'><br>"
                    html += f"{pick_display}"
                else:
                    html += f"{pick_display}"
                html+="</td>"
            html += '</tr>\n'
        html += '</tbody>\n'
        # Totals row with engaging style
        html += '<tfoot>\n'
        html += '<tr class="totals-row">'
        html += f'<td>TOTAL</td><td></td>'
        for player in players:
            score = results['scores'][player]
            cell_classes = []
            if score == max_score:
                cell_classes.append('totals-max')
            if player == winner:
                cell_classes.append('winner')
            html += f"<td class=\"{' '.join(cell_classes)}\">{score}</td>"
        html += '</tr>\n'
        html += '</tfoot>\n'
        html += '</table>\n'
        html += '</div>\n'
        html += '</details>'

    html += """
    <script>
      (function() {
        try {
          var u = localStorage.getItem('pierogi_u');
          var k = localStorage.getItem('pierogi_k');
          if (u && k) {
            document.querySelectorAll('a[href^="pick.html"]').forEach(function(el) {
              el.href = 'pick.html?u=' + encodeURIComponent(u) + '&k=' + encodeURIComponent(k);
            });
          }
        } catch(e) {}
      })();
    </script>
    </body></html>"""
    return html

if __name__ == '__main__':
    games = read_csv(FOOTBALL_SEASON + '/games.csv')
    weekly_results = generate_weekly_results(games)
    html = generate_html(weekly_results)
    output_dir = f'html/{FOOTBALL_SEASON}'
    os.makedirs(output_dir, exist_ok=True)
    images_dest = os.path.join(output_dir, 'images2')
    if not os.path.exists(images_dest) and os.path.exists('images2'):
        shutil.copytree('images2', images_dest)
    with open(f'{output_dir}/nfl_pickem.html', 'w') as f:
        f.write(html)