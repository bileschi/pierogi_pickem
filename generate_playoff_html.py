import csv
import pytz

from collections import defaultdict
from datetime import datetime

# TODO: Move this to the players module.
players = ['smb', 'slb', 'sue', 'jean', 'morgan', 'adam']

# TODO: Make the csv files a command line argument.

def read_csv(filename):
    """Reads the CSV file and returns a list of games."""
    games = []
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader]
    return games

def generate_weekly_results(games):
    """Generates weekly results with winners and scores."""
    weekly_results = defaultdict(lambda: {'games': [], 'scores': defaultdict(int)})
    for game in games:
        week = int(game['week'])
        weekly_results[week]['games'].append(game)
        for player in players:
            pick = game[f'{player}_pick'].split(' ')[0]
            if pick == game['bet_win_key']:
                weekly_results[week]['scores'][player] += 1
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
    <h1>Bileschi Family Pierogi Pigskin Pick'em</h1>"""
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
        html += '<tr><th>Game</th><th>Result</th><th>smb</th><th>slb</th><th>sue</th><th>jean</th><th>morgan</th><th>adam</th></tr>\n'
        for game in results['games']:
            html += '<tr>'
            line_str = game['home_line']
            if line_str and line_str[0] != '-':
                line_str = '+' + line_str
            html += f"<td>{game['away_team']} @ {game['home_team']} {line_str}</td>"
            if game['away_score'] and game['home_score']:
                html += f"<td><div>{game['away_score']} — {game['home_score']}</div></td>"
            else:
                game_day_string = game['prop_date']
                html += f"<td>{game_day_string} </td>"
            for player in players:
                pick = game[f'{player}_pick']
                # The pick has two parts "team_code" e.g. "TB", and source_suffix" e.g. "ESPN"
                # For picks sourced from ESPN, the source suffix is "ESPN".
                # For picks made manually, the source suffix is "MANUAL".
                # For picks made by default mechanis, the source suffix is "DEFAULT".
                
                pick = game[f'{player}_pick']
                if pick == "":
                    pick = "?"

                classes = []
                if pick == game['bet_win_key']:
                    classes.append('correct_pick')
                html += f"<td class='{ ' '.join(classes)}'>{pick}</td>"
            html += '</tr>\n'
        html += '<tr>'
        html += f'<td>TOTAL</td><td></td>'
        # for player, score in results['scores'].items():
        for player in players:
            score = results['scores'][player]
            html += f"<td class='{ 'winner' if player == winner else ''}'>{score}</td>"
        html += '</tr>'
        html += '</table>'


    html += '</body></html>'
    return html

if __name__ == '__main__':
    # TODO: Read the right year from current_season.py
    games = read_csv('2024_2025/playoffs.csv')
    weekly_results = generate_weekly_results(games)
    html = generate_html(weekly_results)
    with open('html/2024_2025/playoffs.html', 'w') as f:
        f.write(html)