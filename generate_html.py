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
            score = results['scores'][player]
            leaderboard[player] += score
    html += '<h2>Leaderboard</h2>'
    html += '<div width=400>'
    html += '<table style="table-layout: fixed; width: 500px;">'
    html += '<tr><th>Player</th><th>Total Score</th></tr>'
    for player, score in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True):
        score = leaderboard[player]
        html += f'<tr><td>{player}</td><td>{score}</td></tr>'
    html += '</table>'

    # Find the current week for expansion
    current_week = find_current_week(weekly_results)

    # Generate weekly results, each in a collapsible <details> element
    for week, results in sorted(weekly_results.items()):
        if results['scores']:
            winner = max(results['scores'], key=results['scores'].get)
        else:
            winner = None

        open_attr = " open" if week == current_week else ""
        html += f'<details id="week{week}"{open_attr}>'
        html += f'<summary>Week {week}</summary>'
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
                    html += f"<img src='{pick_team_img_path}' height={height} width={width} alt='{pick}' title='{pick}'><br>"
                    html += f"{pick}"
                else:
                    html += f"{pick}"
                html+="</td>"
            html += '</tr>\n'
        html += '<tr>'
        html += f'<td>TOTAL</td><td></td>'
        for player in players:
            score = results['scores'][player]
            html += f"<td class='{ 'winner' if player == winner else ''}'>{score}</td>"
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