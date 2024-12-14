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
    <title>Bileschi Family Pierogi Pigskin Pick'em</title>
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
    Manual picks are marked with an <sup>(M)</sup>.
    Default picks are marked in gray an <sup>(D)</sup>.  Please contact me to
    update your way of making default choices.
    <p>
    <ul>
    """

    for week in sorted(weekly_results.keys()):
        html += f'<li><a href="#week{week}">Week {week}</a></li>'
    html += '</ul>'

    # Generate overall leaderboard
    leaderboard = defaultdict(int)
    for week, results in weekly_results.items():
        for player in players:
        # for player, score in results['scores'].items():
            score = results['scores'][player]
            leaderboard[player] += score
    html += '<h2>Leaderboard</h2>'
    html += '<table>'
    html += '<tr><th>Player</th><th>Total Score</th></tr>'
    for player, score in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True):
    # for player in players:
        score = leaderboard[player]
        html += f'<tr><td>{player}</td><td>{score}</td></tr>'
    html += '</table>'

    # Generate weekly results
    for week, results in sorted(weekly_results.items()):
        if results['scores']:
            winner = max(results['scores'], key=results['scores'].get)
        else:
            winner = None
        html += f'<h2 id="week{week}">Week {week}</h2>'
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
                game_day_datetime = datetime.fromtimestamp(int(game['prop_date'])//1000)
                game_day_string = game_day_datetime.strftime('%a %b %d @ %-I%p')
                html += f"<td>{game_day_string} </td>"
            for player in players:
                # pick = game[f'{player}_pick']
                # The pick has two parts "team_code" e.g. "TB", and source_suffix" e.g. "ESPN"
                # For picks sourced from ESPN, the source suffix is "ESPN".
                # For picks made manually, the source suffix is "MANUAL".
                # For picks made by default mechanis, the source suffix is "DEFAULT".
                pick, source = game[f'{player}_pick'].split(' ')
                classes = []
                if pick == game['bet_win_key']:
                    classes.append('correct_pick')
                if source == "DEFAULT":
                    classes.append('default_pick')
                    pick += "<sup>(D)</sup>"  # Add a superscript D to the pick 
                if source == "MANUAL":
                    classes.append('manual_pick')
                    pick += "<sup>(M)</sup>"  # Add a superscript M to the pick 
                if source == "ESPN":
                    classes.append('espn_pick')
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
    games = read_csv('2024_2025/games.csv')
    weekly_results = generate_weekly_results(games)
    html = generate_html(weekly_results)
    with open('html/2024_2025/nfl_pickem.html', 'w') as f:
        f.write(html)