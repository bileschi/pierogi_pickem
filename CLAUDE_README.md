# Pierogi Pick'em — Agent Guide (`CLAUDE_README.md`)

This guide is designed for AI agents (such as Claude) working on the **Pierogi Pick'em** codebase. It outlines how the system operates, key development workflows, and the specific credentials/keys that must be extracted or supplied by the human operator.

---

## 1. Credentials, Keys & Secrets Reference

> [!IMPORTANT]
> **No passwords or private keys are stored in this repository.** Do not commit tokens, private keys, or credentials to git.

To enable full end-to-end functionality (including pulling/pushing code and deploying to production), the user may need to extract or provide the following keys and configurations:

| Credential / Key | Where It Lives | Purpose | How to Extract / Provide |
|---|---|---|---|
| **GitHub SSH Key** | `~/.ssh/id_rsa` or `~/.ssh/id_ed25519` on host | Pushing and pulling repository changes to/from `git@github.com:bileschi/pierogi_pickem.git`. | Ensure host SSH agent has the key loaded (`ssh-add -l`) or pass SSH access in the shell environment. |
| **DreamHost SSH Key** | `~/.ssh/id_ed25519` (matches `Host pdx1-shared-a2-09.dreamhost.com` in `~/.ssh/config`) | Deploying to production server (`bileschi_2016@pdx1-shared-a2-09.dreamhost.com`) and running `dh_build_and_copy.sh`. | Ensure the key registered with DreamHost user `bileschi_2016` is accessible in the terminal or SSH agent. |
| **Player Pick Tokens** | Local or remote SQLite database: `picks.db` (`players` table) | Authenticating users on `pick.html` (`?u=<id>&k=<token>`) and testing CGI API endpoints. | Extract via shell if needed for local test accounts: <br>`sqlite3 picks.db "SELECT id, display_name, token FROM players;"` <br>*(Do not commit token strings to repository files).* |
| **ESPN APIs** | None (Public) | Fetching betting propositions, spreads, live scores, and game clocks. | No credentials or API keys required. ESPN endpoints used in `espn_game_results.py` and `propositions.py` are public JSON feeds. |

---

## 2. System Architecture

The codebase has three primary parts:

1. **Batch Pipeline (`main.py`)**:
   - Fetches game scores, status (live clock, final), and point spreads from ESPN.
   - Evaluates bet outcomes against spreads (`bet_win_key`).
   - Merges player picks in order of precedence:
     1. `manual_picks_<season>.py` (**MANUAL**, badge `M`)
     2. `picks.db` SQLite event log (**SITE**, badge `S`)
     3. Scraped ESPN picks (**ESPN**, badge `E`)
     4. Default fallback strategy from `players.DEFAULT_STRATEGY` (**DEFAULT**, badge `D`)
   - Writes the aligned dataset to `<season>/games.csv`.

2. **Static Scoreboard Generator (`generate_html.py`, `generate_playoff_html.py`)**:
   - Reads `<season>/games.csv`.
   - Computes cumulative points and weekly winner honors.
   - Generates the styled dashboard (`html/<season>/nfl_pickem.html`).
   - Filters out provisional/inactive players (e.g. Max) from the public leaderboard and weekly charts unless they have submitted a manual pick (`players.player_has_manual_pick()`).

3. **Mobile Web App & API (`pick.html`, `api/api.py`, `db.py`)**:
   - `pick.html`: Responsive mobile web app for selecting picks. Persists user tokens in `localStorage`.
   - `api/api.py`: Lightweight Python CGI endpoint handling `GET` (schedule, lockout times, player picks) and `POST` (saving pick events).
   - `db.py`: SQLite helper managing `picks.db` with WAL mode and append-only audit trail (`pick_events`).

---

## 3. Local Development & Testing

### Python Environment
- A virtual environment containing dependencies (like `requests`) is located at:
  ```bash
  ./pierogi/bin/python3
  ```
- Lightweight scripts (`generate_html.py`, `dev_server.py`, `db.py`) can also run with the system `python3`.

### Running Local Development Server
To test the site, picking UI, and API locally without Apache:
```bash
python3 dev_server.py
```
This serves:
- `http://localhost:8080/` -> Standings / Scoreboard HTML
- `http://localhost:8080/pick.html` -> Mobile picking UI
- `http://localhost:8080/api/api.py` -> CGI API endpoint

### Regenerating Scoreboard HTML
```bash
python3 generate_html.py
```
Output is written to `html/<season>/nfl_pickem.html`.

### Running the Full Local Ingestion Pipeline
```bash
./pierogi/bin/python3 main.py
python3 generate_html.py
```

---

## 4. Production Deployment Workflow

1. **Commit and Push Code Changes**:
   ```bash
   git add <modified-files>
   git commit -m "Your descriptive commit message"
   git push origin master
   ```

2. **Trigger Remote Build on DreamHost**:
   The DreamHost production server hosts the site at `/home/bileschi_2016/bileschi.com/nfl/`. The build script pulls the latest `master` from GitHub, rebuilds the data and HTML, and updates the web assets:
   ```bash
   ssh bileschi_2016@pdx1-shared-a2-09.dreamhost.com "cd /home/bileschi_2016/proj/pierogi_pickem && ./dh_build_and_copy.sh"
   ```

---

## 5. Critical Code Conventions & Rules

- **Timezones**: All game kickoff times and timestamps must use Eastern Time (`America/New_York`). Always include the fallback:
  ```python
  try:
      import pytz
      nyc_timezone = pytz.timezone('America/New_York')
  except ImportError:
      from zoneinfo import ZoneInfo
      nyc_timezone = ZoneInfo('America/New_York')
  ```
- **Point Spreads**:
  - Negative lines (e.g. `home_line = -3.5`) indicate the home team is favored.
  - A game where the score plus the line equals the opponent score is a push (`bet_win_key = 'TIE'`), awarding 0 points.
- **Player Accounts & Privacy**:
  - Do not hardcode secret tokens into test files or documentation.
  - Keep provisional players registered in `db.py` and `players.py` so they can log in, but respect `player_has_manual_pick()` so they do not clutter the public scoreboard until they play.
