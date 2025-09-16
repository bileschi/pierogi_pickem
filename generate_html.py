import csv
import enum
from typing import Any, Dict
import pytz

from collections import defaultdict
from datetime import datetime
from current_season import FOOTBALL_SEASON

# TODO: Move this to the players module.
players = ['smb', 'slb', 'sue', 'jean', 'morgan', 'adam']

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
    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <title>Bileschi Family Pierogi Pigskin Pick'em</title>
    <style>
    body {
      font-size: 18px;
    }
    h1, h2 {
      font-size: 2em;
    }
    .leaderboard-table {
      font-size: 18px;
      width: 100%;
      border-collapse: collapse;
    }
    .leaderboard-table th, .leaderboard-table td {
      border: 1px solid #bbb;
      padding: 6px 8px;
      text-align: center;
    }
    .leader-row {
      background: #ffd700 !important;
      font-size: 1.3em;
      font-weight: bold;
      border: 2px solid #bfa100;
      box-shadow: 0 0 8px 2px #ffd700;
      animation: pop 0.7s;
    }
    .leaderboard-table tr:nth-child(even):not(.leader-row) {
      background: #f9f9f9;
    }
    .rank-cell {
      font-weight: bold;
      font-size: 1.1em;
      width: 2em;
    }
    /* --- Weekly Table Styling --- */
    table.week-table {
      border-collapse: collapse;
      width: 100%;
      font-size: 14px;
    }
    table.week-table th, table.week-table td {
      border: 1px solid #ddd;
      padding: 1px;
      text-align: center;
    }
    .correct_pick {
      background-color: lightgreen;
    }
    .incorrect_pick {
      background-color: lightgrey;
      filter: grayscale(100%) saturate(0%);
    }
    .tie {
      background: repeating-linear-gradient(
      45deg,
      lightgreen,
      lightgreen 10px,
      lightgrey 10px,
      lightgrey 20px
    );
    }
    .winner {
      font-weight: bold;
    }
    .default_pick {
      color: gray; 
    }
    .totals-row {
      font-size: 1.3em;
      font-weight: bold;
      background: #ffe066;
      border-top: 3px solid #888;
    }
    .totals-row td {
      padding-top: 6px;
      padding-bottom: 6px;
    }
    .totals-max {
      background: #ffd700 !important;
      color: #222;
      box-shadow: 0 0 8px 2px #ffd700;
      border: 2px solid #bfa100;
      font-size: 1.4em;
      animation: pop 0.7s;
    }
    @keyframes pop {
      0% { transform: scale(1.1);}
      70% { transform: scale(1.18);}
      100% { transform: scale(1);}
    }
    summary {
      font-size: 1.2em;
      font-weight: bold;
      cursor: pointer;
      background: #f0f0f0;
      padding: 6px;
      border-radius: 4px;
      margin-bottom: 4px;
    }
    details {
      margin-bottom: 12px;
      border: 1px solid #ccc;
      border-radius: 4px;
      padding: 2px 8px 8px 8px;
      background: #fafafa;
    }
    img {
      height: 36px;
      width: 36px;
    }
    </style>
    </head>
    <body>
    <h1>Bileschi Family Pierogi Pigskin Pick'em """+FOOTBALL_SEASON+"</h1>"
    # Add the timestamp
    nyc_timezone = pytz.timezone('America/New_York')
    timestamp = datetime.now(nyc_timezone).strftime('%Y-%m-%d %H:%M:%S')
    html += f"<p>Last updated: {timestamp} (East Coast)</p>"
    html += """
    <p>
    Manual picks are marked with an <sup>(M)</sup>.
    Default picks are marked in gray an <sup>(D)</sup>.  Please contact me to
    update your way of making default choices.
    <p>
    <ul>
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
    html += '<div width=400>'
    html += '<table class="leaderboard-table" style="table-layout: fixed; width: 500px;">'
    html += '<tr><th>Rank</th><th>Player</th><th>Total Score</th></tr>'
    rank = 1
    prev_score = None
    for idx, (player, score) in enumerate(sorted_leaderboard):
        # 2. Rank numbers and tie handling
        if prev_score is not None and score < prev_score:
            rank = idx + 1
        prev_score = score
        # 1 & 3. Gold background and larger font for leader(s)
        row_class = "leader-row" if score == max_score and rank == 1 else ""
        # 2. Add emoji for top 3
        rank_display = f"{rank}"
        if rank == 1:
            rank_display = "1 👑"
        elif rank == 2:
            rank_display = "2 🥈"
        elif rank == 3:
            rank_display = "3 🥉"
        html += f'<tr class="{row_class}">'
        html += f'<td class="rank-cell">{rank_display}</td>'
        html += f'<td>{player}</td>'
        html += f'<td>{score}</td>'
        html += '</tr>'
    html += '</table>'

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
        html += '<table class="week-table">'
        # Table Header
        html += '<tr><th>Game</th><th>Result</th><th>smb</th><th>slb</th><th>sue</th><th>jean</th><th>morgan</th><th>adam</th></tr>\n'
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
                html += f"<img src='{away_team_img_path}' alt='{game['away_team']}' title='{game['away_team']}'>"
                html += f"<img src='{home_team_img_path}' alt='{game['home_team']}' title='{game['home_team']}'><br>"
            html += f"{game['away_team']} @ {game['home_team']} {line_str}"
            html += "</td>"

            if game['away_score'] and game['home_score']:
                html += f"<td><div>{game['away_score']} — {game['home_score']}</div></td>"
            else:
                game_day_datetime = datetime.fromtimestamp(int(game['prop_date'])//1000, tz=nyc_timezone)
                game_day_string = game_day_datetime.strftime('%a %b %d @ %-I%p')
                html += f"<td>{game_day_string} </td>"
            for player in players:
                pick, source = game[f'{player}_pick'].split(' ')
                pick_team_img_path = get_image_path(pick)
                if pick == "":
                    pick = "?"
                classes = []
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
                if source == "DEFAULT":
                    classes.append('default_pick')
                    pick += "<sup>(D)</sup>"
                if source == "MANUAL":
                    classes.append('manual_pick')
                    pick += "<sup>(M)</sup>"
                if source == "ESPN":
                    classes.append('espn_pick')

                html += f"<td class='{ ' '.join(classes)}'>"
                if pick_team_img_path:
                    html += f"<img src='{pick_team_img_path}' alt='{pick}' title='{pick}'><br>"
                    html += f"{pick}"
                else:
                    html += f"{pick}"
                html+="</td>"
            html += '</tr>\n'
        # Totals row with engaging style
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
        html += '</tr>'
        html += '</table>'
        html += '</details>'

    html += '</body></html>'
    return html

if __name__ == '__main__':
    games = read_csv(FOOTBALL_SEASON + '/games.csv')
    weekly_results = generate_weekly_results(games)
    html = generate_html(weekly_results)
    with open(f'html/{FOOTBALL_SEASON}/nfl_pickem.html', 'w') as f:
        f.write(html)