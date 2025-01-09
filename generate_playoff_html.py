import csv
import pytz

from collections import defaultdict
from datetime import datetime

# TODO: Move this to the players module.
players = ['smb', 'max', 'slb', 'sue', 'jean', 'morgan', 'adam']


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

score_per_week = [2, 3, 5, 8]

def generate_weekly_results(games):
    """Generates weekly results with winners and scores."""
    weekly_results = defaultdict(lambda: {'games': [], 'scores': defaultdict(int)})
    for game in games:
        week = int(game['week'])
        weekly_results[week]['games'].append(game)
        for player in players:
            pick = game[f'{player}_pick'].split(' ')[0]
            if pick == game['bet_win_key']:
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
    table {
      border-collapse: collapse;
      width: 100%;
    }
    th, td {
      border: 1px solid black;
      padding: 8px;
      text-align: center;
    }
    .correct_pick {
      background-color: lightgreen;
    }
    .winner {
      font-weight: bold;
    }
    .default_pick {
      color: gray; 
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

    # Generate weekly results
    for week, results in sorted(weekly_results.items()):
        if results['scores']:
            winner = max(results['scores'], key=results['scores'].get)
        else:
            winner = None
        if week == 1:
            html += f'<h2 id="week{week}">Wildcard Round (2 points per game)</h2>'
        if week == 2:
            html += f'<h2 id="week{week}">Divisional Round (3 points per game)</h2>'
        if week == 3:
            html += f'<h2 id="week{week}">Conference Championships (5 points per game)</h2>'
        if week == 4:
            html += f'<h2 id="week{week}">Super Bowl (8 points)</h2>'
        html += '<table>'
        # Table Header
        html += '<tr><th>Game</th><th>Result</th>'
        for player in players:
            html += f'<th>{player}</th>'
        html += '</tr>\n'
        for game in results['games']:
            html += '<tr>'
            line_str = game['home_line']
            if line_str and line_str[0] != '-':
                line_str = '+' + line_str
            # Game illustration
            away_team_img_path = get_image_path(game['away_team'])
            home_team_img_path = get_image_path(game['home_team'])
            html += "<td>"
            height=50
            width=50
            if away_team_img_path and home_team_img_path:
                html += f"<img src='{away_team_img_path}' height={height} width={width} alt='{game['away_team']}' title='{game['away_team']}'> @ "
                html += f"<img src='{home_team_img_path}' height={height} width={width} alt='{game['home_team']}' title='{game['home_team']}'><br>"
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
                if pick == game['bet_win_key']:
                    classes.append('correct_pick')
                html += f"<td class='{ ' '.join(classes)}'>"
                if pick_team_img_path:
                    html += f"<img src='{pick_team_img_path}' height={height} width={width} alt='{pick}' title='{pick}'><br>"
                else:
                    html += f"{pick}"
                html+="</td>"
            html += '</tr>\n'
        html += '<tr>'
        html += f'<td>TOTAL</td><td></td>'
        # for player, score in results['scores'].items():
        for player in players:
            score = results['scores'][player]
            html += f"<td class='{ 'winner' if player == winner else ''}'>{score}</td>"
        html += '</tr>'
        html += '</table>'

    html += f'<h2 id="superbowl_props">SuperBowl Prop Bets (TBD)</h2>'


    html += '</body></html>'
    return html

if __name__ == '__main__':
    # TODO: Read the right year from current_season.py
    games = read_csv('2024_2025/playoffs.csv')
    weekly_results = generate_weekly_results(games)
    html = generate_html(weekly_results)
    with open('html/2024_2025/playoffs.html', 'w') as f:
        f.write(html)