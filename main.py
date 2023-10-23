import requests
from bs4 import BeautifulSoup

# week	home	away	line	home_score	away_score	Stanley M	Aunt Sue	Stanley L	Jean	Morgan	game_id

espn_url = 'https://www.espn.com/nfl/schedule/_/week/1/year/2023/seasontype/2'
# url = 'https://www.bbc.com/news'
response = requests.get(espn_url,headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
soup = BeautifulSoup(response.content, 'html.parser')

rows = soup.find_all('tr', class_='Table__TR Table__TR--sm Table__even')

one_game = dict()
for i_r, row in enumerate(rows):
  print(f'row = {i_r}')
  teams = row.find_all('span', class_='Table__Team')
  for i_t, team in enumerate(teams):
    print(f'  team = {i_t}')
    print('   ' + team.get_text())
    if i_t == 0:
      one_game['away_team'] = team.get_text()
    if i_t == 1:
      one_game['home_team'] = team.get_text()
  result = row.find('td', class_='teams__col Table__TD')
  print(result.get_text())
  print(str(one_game))

  # #print(article.attrs)
#   print(len(article.contents))
#   print(article.contents)
#   print(len(list(article.descendants)))
#   print(list(article.descendants))
#   # title = article.find('a').text
  # print(title)


print('hello_world')