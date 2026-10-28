# Pierogi Pick'em — Project Guide for Claude

Private NFL Pigskin Pick'em system for the Bileschi family, hosted at `https://bileschi.com/nfl/`.

---

## 1. System Architecture & Data Flow

The project consists of three main components:
1. **Batch Pipeline (`main.py`)**: Gathers lines, scores, and picks from multiple sources, resolves game outcomes against point spreads, and outputs `<season>/games.csv`.
2. **Scoreboard Generator (`generate_html.py`, `generate_playoff_html.py`)**: Reads `<season>/games.csv`, computes cumulative and weekly player scores, and renders the static dashboard (`html/<season>/nfl_pickem.html`).
3. **Mobile Pick App & API (`pick.html`, `api/api.py`, `db.py`)**: Standalone responsive mobile web app with a CGI backend for token-authenticated picking with kickoff lockouts.

### Data Flow Diagram
```
ESPN Scoreboard API / Props API
               │
               ▼
   [main.py Data Alignment]
       ├── Scrapes ESPN picks
       ├── Fetches base game scores & clock
       ├── Integrates site picks from picks.db (SQLite)
       ├── Overrides with manual picks from manual_picks_<season>.py
       └── Applies default pick strategies (from players.py)
               │
               ▼
     [<season>/games.csv]
               │
       ┌───────┴────────────────────────┐
       ▼                                ▼
[generate_html.py]           [api/api.py + pick.html]
       │                                │
       ▼                                ▼
[html/<season>/nfl_pickem.html]   [SQLite: picks.db]
       │                                │
       └──────────────┬─────────────────┘
                      ▼
        Deployed to DreamHost
        https://bileschi.com/nfl/
```

---

## 2. Key Files & Responsibilities

| File | Purpose |
|---|---|
| `current_season.py` | Defines `FOOTBALL_SEASON` (e.g. `"2026_2027"`) and `N_WEEKS_IN_SEASON = 18`. |
| `players.py` | Player IDs, display names, ESPN UUIDs, default pick strategies, and `player_has_manual_pick()`. |
| `games_col_keys.py` | String constants for game dict / CSV column headers (`smb_pick`, `max_pick`, etc.). |
| `main.py` | Main orchestrator pipeline; resolves against spreads and writes `<season>/games.csv`. |
| `generate_html.py` | Regular season HTML generator (Leaderboard, weekly collapsible tables, badges, live score pills). |
| `generate_playoff_html.py` | Playoff rounds & Super Bowl prop bet scoreboard generator. |
| `pick.html` | Client-side mobile picking interface with automatic URL token persistence in localStorage. |
| `api/api.py` | Python CGI backend; handles `GET` (matchups, status, lockouts) and `POST` (saves pick events). |
| `db.py` | SQLite helper (`picks.db` with WAL mode); manages `players` table and append-only `pick_events`. |
| `manual_picks_<season>.py` | Dictionary mapping player IDs to week-by-week manual pick overrides. |
| `dev_server.py` | Local development server that emulates Apache CGI for `/api/api.py` and serves static assets on port 8080. |
| `dh_build_and_copy.sh` | Production build and deploy script executed on DreamHost. |
| `upload_to_dreamhost.sh` | SCP helper to upload generated regular season HTML directly to DreamHost. |

---

## 3. Pick Precedence & Badges

Each pick in `games.csv` is stored as `"<TEAM_ABBR> <SOURCE>"`:
1. **`MANUAL`** (`M` badge): Explicitly coded in `manual_picks_<season>.py`. Overrides all.
2. **`SITE`** (`S` badge): Picked by player on `pick.html` and loaded from `picks.db`. Overrides ESPN & Default.
3. **`ESPN`** (`E` badge): Scraped from ESPN Pigskin Pick'em group.
4. **`DEFAULT`** (`D` badge): Automated fallback strategy from `players.DEFAULT_STRATEGY` (e.g. all home, all favorites, shortest name).

### Provisional / Inactive Players
- Players can be provisioned in `db.py` with tokens so they can log into `pick.html`, and their defaults/scores continue to be computed in `games.csv`.
- If a player is marked provisional (e.g. Max), `players.player_has_manual_pick(games, player_id)` checks if they have submitted any pick with source != `DEFAULT`. If `False`, they are omitted from the public leaderboard, weekly matchup charts, and weekly winner honors.

---

## 4. Local Development & Useful Commands

### Environment
- A virtual environment is located at `./pierogi/bin/python3` (contains `requests`, etc.).
- System `python3` can run `generate_html.py`, `dev_server.py`, and `db.py`.

### Running Local Dev Server
```bash
python3 dev_server.py
# Serves:
#   http://localhost:8080/          -> Standings HTML
#   http://localhost:8080/pick.html -> Mobile picking UI
#   http://localhost:8080/api/api.py-> CGI API endpoint
```

### Regenerating Standings HTML
```bash
python3 generate_html.py
# Writes output to html/<FOOTBALL_SEASON>/nfl_pickem.html
```

### Running Full Pipeline Locally
```bash
./pierogi/bin/python3 main.py
python3 generate_html.py
```

### Inspecting Database (`picks.db`)
```bash
sqlite3 picks.db "SELECT * FROM players;"
sqlite3 picks.db "SELECT * FROM pick_events ORDER BY id DESC LIMIT 10;"
```

---

## 5. Deployment Workflow

1. **Commit & Push to GitHub**:
   ```bash
   git add <files>
   git commit -m "Description of changes"
   git push origin master
   ```

2. **Deploy to DreamHost**:
   The DreamHost server runs `dh_build_and_copy.sh`, which pulls `master`, runs `main.py` + `generate_html.py`, and copies HTML and API files to web root `/home/bileschi_2016/bileschi.com/nfl/`:
   ```bash
   ssh bileschi_2016@pdx1-shared-a2-09.dreamhost.com "cd /home/bileschi_2016/proj/pierogi_pickem && ./dh_build_and_copy.sh"
   ```
   *(DreamHost also runs scheduled cron jobs to update scores and standings automatically.)*

---

## 6. Implementation Conventions & Pitfalls

- **Timezones**: Always use Eastern Time for game kickoffs and timestamps:
  ```python
  try:
      import pytz
      nyc_timezone = pytz.timezone('America/New_York')
  except ImportError:
      from zoneinfo import ZoneInfo
      nyc_timezone = ZoneInfo('America/New_York')
  ```
- **Spreads / Point Lines**: A negative line (e.g. `home_line = -3.5`) means the home team is favored by 3.5 points. If `(home_score + home_line) > away_score`, home covers. If equal, it's a push (`bet_win_key = 'TIE'`).
- **Kickoff Locks**: `prop_date` in `games.csv` is epoch time in milliseconds. When `now_ms >= prop_date`, picks lock for that game.
- **DreamHost Paths**: DreamHost production root is `/home/bileschi_2016/proj/pierogi_pickem` with web root `/home/bileschi_2016/bileschi.com/nfl/`. Database path is `/home/bileschi_2016/proj/pierogi_pickem/picks.db`.
