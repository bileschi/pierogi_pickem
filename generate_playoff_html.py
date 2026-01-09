import csv
import enum
from typing import Any, Dict
import pytz

from collections import defaultdict
from datetime import datetime
from current_season import FOOTBALL_SEASON

# TODO: Move this to the players module.
players = ['smb', 'max', 'slb', 'sue', 'jean', 'morgan', 'adam']
IMG_HEIGHT=48
IMG_WIDTH=48

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

# TODO: Make the csv files a command line argument.

def read_csv(filename):
    """Reads the CSV file and returns a list of games."""
    games = []
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader]
    return games

score_per_week = {
    1: 2,
    2: 3,
    3: 5,
    4: 8
}

def generate_weekly_results(games):
    """Generates weekly results with winners and scores."""
    weekly_results : Dict[int, Dict[str, Any]] = defaultdict(lambda: {'games': [], 'scores': defaultdict(int)})
    for game in games:
        week = int(game['week'])
        weekly_results[week]['games'].append(game)
        for player in players:
            pick = game[f'{player}_pick'].split(' ')[0]
            if week == 5:  # superbowl prop bets have conditional scores
                if pick == game['bet_win_key']:
                    weekly_results[week]['scores'][player] += int(game['home_line'])
                if pick == 'YES':
                    weekly_results[week]['scores'][player] -= 1                    
            else: # normal week - calculate winner based on score and line
                if game['away_score'] and game['home_score']:
                    diff_w_line = float(game['home_score']) + float(game['home_line']) - float(game['away_score'])
                    if diff_w_line > 0:
                        winner = game['home_team']
                    elif diff_w_line == 0:
                        winner = 'TIE'
                    else:
                        winner = game['away_team']
                    if pick == winner:
                        weekly_results[week]['scores'][player] += score_per_week[week]
    return weekly_results

def generate_html(weekly_results):
    """Generates the HTML for the website."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <title>Bileschi Family PLAYOFF!! Pierogi Pigskin Pick'em</title>
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
    img {
      height: 48px;
      width: 48px;
    }
    </style>
    </head>
    <body>
    <h1>Bileschi Family PLAYOFF!! Pierogi Pigskin Pick'em</h1>"""
    # Add the timestamp
    nyc_timezone = pytz.timezone('America/New_York')
    timestamp = datetime.now(nyc_timezone).strftime('%Y-%m-%d %H:%M:%S')
    html += f"<p>Last updated: {timestamp} (East Coast)</p>"
    html += """
    <p>
    All picks are manual.
    <p>
    <ul>
    """

    # Generate overall leaderboard
    leaderboard = defaultdict(int)
    for week, results in weekly_results.items():
        for player in players:
        # for player, score in results['scores'].items():
            score = results['scores'][player]
            leaderboard[player] += score

    # Prepare leaderboard sorted list with ranks
    sorted_leaderboard = sorted(
        leaderboard.items(), key=lambda item: item[1], reverse=True
    )
    max_score = sorted_leaderboard[0][1] if sorted_leaderboard else None

    html += f'<h2 id="leaderboard">Leaderboard</h2>'
    html += '<div width=400>' # add div to format the leaderboard table
    html += '<table class="leaderboard-table" style="table-layout: fixed; width: 500px;">'
    html += '<tr><th>Rank</th><th>Player</th><th>Total Score</th></tr>'
    rank = 1
    prev_score = None
    for idx, (player, score) in enumerate(sorted_leaderboard):
        # Rank numbers and tie handling
        if prev_score is not None and score < prev_score:
            rank = idx + 1
        prev_score = score
        # Gold background and larger font for leader(s)
        row_class = "leader-row" if score == max_score and rank == 1 else ""
        # Add emoji for top 3
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
    html += '</div>'


    # Generate weekly results
    for week, results in sorted(weekly_results.items()):
        # Hide divisional round and beyond if matchups aren't determined yet
        if week >= 2:
            all_unknown = all(game['away_team'] == '?' and game['home_team'] == '?' 
                            for game in results['games'])
            if all_unknown:
                continue
        
        if results['scores']:
            winner = max(results['scores'], key=results['scores'].get)
            winner_score = results['scores'][winner]
            print(f"{week=}, {winner=}")
        else:
            winner = None
            winner_score = None
        if week == 1:
            html += f'<h2 id="week{week}">Wildcard Round (2 points per game)</h2>'
        if week == 2:
            html += f'<h2 id="week{week}">Divisional Round (3 points per game)</h2>'
        if week == 3:
            html += f'<h2 id="week{week}">Conference Championships (5 points per game)</h2>'
        if week == 4:
            html += f'<h2 id="week{week}">Super Bowl (8 points)</h2>'
        if week == 5:
            html += f'<h2 id="week{week}">Super Bowl Prop Bets</h2>'
            html += f'<p>Prop bets <b>cost one point</b> if you take the bet<br>'
            html += f'<p>They pay out X points as listed in the description.<br>'
        html += '<table class="week-table">'
        # Table Header
        if week == 5:
            html += '<tr><th>Bet Description</th><th>Points if Correct</th><th>Result</th>'
        else:
            html += '<tr><th>Game</th><th>Result</th>'
        for player in players:
            html += f'<th>{player}</th>'
        html += '</tr>\n'
        for game in results['games']:
            if week == 5: # superbowl prop bets
                # Bet Description is in away_team slot.
                html += '<tr>'
                html += f"<td>{game['away_team']}</td>"
                # Points if correct is in the home_line slot.
                html += f"<td>{game['home_line']}</td>"
                # Result is in the prop_date slot.
                html += f"<td>{game['prop_date']}</td>"
            else:
                html += '<tr>'
                line_str = game['home_line']
                if line_str and line_str[0] != '-':
                    line_str = '+' + line_str
                # Game illustration
                away_team_img_path = get_image_path(game['away_team'])
                home_team_img_path = get_image_path(game['home_team'])
                html += "<td>"
                if away_team_img_path and home_team_img_path:
                    html += f"<img src='{away_team_img_path}' height={IMG_HEIGHT} width={IMG_WIDTH} alt='{game['away_team']}' title='{game['away_team']}'> @ "
                    html += f"<img src='{home_team_img_path}' height={IMG_HEIGHT} width={IMG_WIDTH} alt='{game['home_team']}' title='{game['home_team']}'><br>"
                html += f"{game['away_team']} @ {game['home_team']} {line_str}"
                html += "</td>"
    
                if game['away_score'] and game['home_score']:
                    html += f"<td><div>{game['away_score']} — {game['home_score']}</div></td>"
                else:
                    game_day_string = game['prop_date']
                    html += f"<td>{game_day_string} </td>"
            for player in players:
                pick = game[f'{player}_pick']
                pick_team_img_path = get_image_path(pick)
                if pick == "":
                    pick = "?"
                classes = []
                bet_status = BetResult.UNDECIDED
                if game['away_score'] and game['home_score']:
                    diff_w_line = float(game['home_score']) + float(game['home_line']) - float(game['away_score'])
                    if diff_w_line > 0:
                        winner = game['home_team']
                    elif diff_w_line == 0:
                        winner = 'TIE'
                    else:
                        winner = game['away_team']
                    if pick == winner:
                        bet_status = BetResult.WIN
                    elif winner == 'TIE':
                        bet_status = BetResult.TIE
                    else:
                        bet_status = BetResult.LOSE
                if week == 5 and game['bet_win_key']:
                    if game['bet_win_key'] == 'YES' and pick == 'YES':
                        bet_status = BetResult.WIN
                    if game['bet_win_key'] == 'NO' and pick == 'YES':
                        bet_status = BetResult.LOSE
                if bet_status == BetResult.WIN:
                    classes.append('correct_pick')
                if bet_status == BetResult.LOSE:
                    classes.append('incorrect_pick')
                if bet_status == BetResult.TIE:
                    classes.append('tie')
                if bet_status == BetResult.UNDECIDED:
                    classes.append('undecided')

                html += f"<td class='{ ' '.join(classes)}'>"
                if week == 5 and pick == 'x':
                    pass
                else:
                    if pick_team_img_path:
                        html += f"<img src='{pick_team_img_path}' height={IMG_HEIGHT} width={IMG_WIDTH} alt='{pick}' title='{pick}'><br>"
                    else:
                        html += f"{pick}"
                html+="</td>"
            html += '</tr>\n'
        # Find the max score(s) for the totals row for this week
        max_score = max(results['scores'].values()) if results['scores'] else None
        html += '<tr class="totals-row">'
        html += f'<td>TOTAL</td><td></td>'
        if week == 5:  #extra column in prop bets
            html += f'<td></td>'
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

    html += '</body></html>'
    return html

if __name__ == '__main__':
    games = read_csv(FOOTBALL_SEASON + '/playoffs.csv')
    weekly_results = generate_weekly_results(games)
    html = generate_html(weekly_results)
    with open(f'html/{FOOTBALL_SEASON}/playoffs.html', 'w') as f:
        f.write(html)