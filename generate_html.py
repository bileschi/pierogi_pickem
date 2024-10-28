import csv
from collections import defaultdict

# TODO: Move this to the players module.
players = ['smb', 'slb', 'sue', 'jean', 'morgan', 'adam']

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
            if game[f'{player}_pick'] == game['bet_win_key']:
                weekly_results[week]['scores'][player] += 1
    return weekly_results

def generate_html(weekly_results):
    """Generates the HTML for the website."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
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
    .correct {
      background-color: lightgreen;
    }
    .winner {
      font-weight: bold;
    }
    </style>
    </head>
    <body>
    <h1>Bileschi Family Pierogi Pigskin Pick'em</h1>
    <ul>
    """

    for week in sorted(weekly_results.keys()):
        html += f'<li><a href="#week{week}">Week {week}</a></li>'
    html += '</ul>'

    for week, results in sorted(weekly_results.items()):
        if results['scores']:
            winner = max(results['scores'], key=results['scores'].get)
        else:
            winner = None
        html += f'<h2 id="week{week}">Week {week}</h2>'
        html += '<table>'
        html += '<tr><th>Game</th><th>smb</th><th>slb</th><th>sue</th><th>jean</th><th>morgan</th><th>adam</th></tr>'
        for game in results['games']:
            html += '<tr>'
            html += f"<td>{game['away_team']} @ {game['home_team']}</td>"
            for player in players:
                pick = game[f'{player}_pick']
                html += f"<td class='{ 'correct' if pick == game['bet_win_key'] else ''}'>{pick}</td>"
            html += '</tr>'
        html += '<tr>'
        html += f'<td>TOTAL</td>'
        # for player, score in results['scores'].items():
        for player in players:
            score = results['scores'][player]
            html += f"<td class='{ 'winner' if player == winner else ''}'>{score}</td>"
        html += '</tr>'
        html += '</table>'

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
    # for player, score in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True):
    for player in players:
        score = leaderboard[player]
        html += f'<tr><td>{player}</td><td>{score}</td></tr>'
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