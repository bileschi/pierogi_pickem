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
    .incorrect_pick {  /* New class for loss styling */
      background-color: lightgrey;
      filter: grayscale(100%) saturate(0%);  /* Desaturate and turn to grayscale */
    }
    .tie {
      background: repeating-linear-gradient(
      45deg,
      lightgreen,
      lightgreen 10px,
      lightgrey 10px,
      lightgrey 20px
    );
    .winner {
      font-weight: bold;
    }
    .default_pick {
      color: gray; 
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
    html += '<div width=400>' # add div to format the leaderboard table
    html += '<table style="table-layout: fixed; width: 500px;">'
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
                game_day_datetime = datetime.fromtimestamp(int(game['prop_date'])//1000, tz=nyc_timezone)
                game_day_string = game_day_datetime.strftime('%a %b %d @ %-I%p')
                html += f"<td>{game_day_string} </td>"
            for player in players:
                # pick = game[f'{player}_pick']
                # The pick has two parts "team_code" e.g. "TB", and source_suffix" e.g. "ESPN"
                # For picks sourced from ESPN, the source suffix is "ESPN".
                # For picks made manually, the source suffix is "MANUAL".
                # For picks made by default mechanis, the source suffix is "DEFAULT".
                pick, source = game[f'{player}_pick'].split(' ')
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
                    pick += "<sup>(D)</sup>"  # Add a superscript D to the pick 
                if source == "MANUAL":
                    classes.append('manual_pick')
                    pick += "<sup>(M)</sup>"  # Add a superscript M to the pick 
                if source == "ESPN":
                    classes.append('espn_pick')

                html += f"<td class='{ ' '.join(classes)}'>"
                if pick_team_img_path:
                    html += f"<img src='{pick_team_img_path}' height={height} width={width} alt='{pick}' title='{pick}'><br>"
                    html += f"{pick}"
                else:
                    html += f"{pick}"
                html+="</td>"

#                html += f"<td class='{ ' '.join(classes)}'>{pick}</td>"


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
    games = read_csv(FOOTBALL_SEASON + '/games.csv')
    weekly_results = generate_weekly_results(games)
    html = generate_html(weekly_results)
    with open(f'html/{FOOTBALL_SEASON}/nfl_pickem.html', 'w') as f:
        f.write(html)