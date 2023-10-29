import csv
import requests
from bs4 import BeautifulSoup

# week	home	away	line	home_score	away_score	Stanley M	Aunt Sue	Stanley L	Jean	Morgan	game_id

one_game = dict()

WEEK_KEY = 'week'
HOME_KEY = 'home_team'
AWAY_KEY = 'away_team'
GAME_ID_KEY = 'game_id'
LINE_KEY = 'home_line'
HOME_SCORE_KEY = 'home_score'
AWAY_SCORE_KEY = 'away_score'
SMB_PICK_KEY = 'smb_pick'
SLB_PICK_KEY = 'slb_pick'
SUE_PICK_KEY = 'sue_pick'
JEAN_PICK_KEY = 'jean_pick'

game_col_keys = (
  WEEK_KEY,
  HOME_KEY,
  AWAY_KEY,
  GAME_ID_KEY,
  HOME_SCORE_KEY,
  AWAY_SCORE_KEY,
  LINE_KEY,
  SMB_PICK_KEY,
  SLB_PICK_KEY,
  SUE_PICK_KEY,
  JEAN_PICK_KEY,
)

def parse_score_text(score_text):
  # expect text like "ATL 25, GB 24" or "BUF 38, LV 10"
  (away, home) = score_text.split(",")
  away_score = away.strip().split(" ")[1].strip()
  home_score = home.strip().split(" ")[1].strip()
  return(away_score, home_score)

def game_as_str(game_dict):
  return(','.join([str(game_dict[k]) for k in game_col_keys]))

games = []
for week in range(1, 19):
  espn_week_url = f'https://www.espn.com/nfl/schedule/_/week/{week}/year/2023/seasontype/2'
  # url = 'https://www.bbc.com/news'
  response = requests.get(espn_week_url,headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
  soup = BeautifulSoup(response.content, 'html.parser')

  football_days = soup.find_all('div', class_='ScheduleTables mb5 ScheduleTables--nfl ScheduleTables--football')
  print(f"week {week}")
  for football_day in football_days:
    rows = football_day.find_all('tr', class_='Table__TR Table__TR--sm Table__even')
    for i_r, row in enumerate(rows[:]):
      game = {k: '' for k in game_col_keys}
      game[WEEK_KEY] = week
      # print()
      # print(f'row = {i_r}')
      # Get the teams
      teams = row.find_all('span', class_='Table__Team')
      for i_t, team in enumerate(teams):
        team_link = team.find_all('a')[0]
        team_code = team_link['href'].split('/')[5].upper()
        # print(i_t, team_link['href'], team_code)
        if i_t == 0:
          game[AWAY_KEY] = team_code
        if i_t == 1:
          game[HOME_KEY] = team_code
      # Get the score and ESPN game ID.  This will be none if the game 
      # has not happened or is in progres.
      score_col = row.find('td', class_='teams__col Table__TD')
      if score_col:
        game_href = score_col.find_all('a')[0]['href']
        # print('game href ', game_href)
        game_id = game_href.split("=")[1]
        score_text = score_col.get_text()
        (away_score, home_score) = parse_score_text(score_text)
        game[HOME_SCORE_KEY] = home_score
        game[AWAY_SCORE_KEY] = away_score
        game[GAME_ID_KEY] = game_id
      games.append(game)
      print(game_as_str(game))

with open('games.csv', 'w', newline='') as csvfile:
  gamewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
  gamewriter.writerow(game_col_keys)
  for game in games:
    gamewriter.writerow([game[k] for k in game_col_keys])


  # #print(article.attrs)
#   print(len(article.contents))
#   print(article.contents)
#   print(len(list(article.descendants)))
#   print(list(article.descendants))
#   # title = article.find('a').text
  # print(title)


print('hello_world')