#!/bin/bash

# go to dir
cd /home/bileschi_2016/proj/pierogi_pickem
# Update to most recent version
git checkout master
git pull origin master
# use virtual env
source venv/bin/activate
# regenerate csv & html
python3 main.py
python3 generate_html.py  # <-- Regular season
# python3 generate_playoff_html.py  # Playoffs

# copy output to web.
# cp html/2024_2025/nfl_pickem.html /home/bileschi_2016/bileschi.com/nfl/index.html # <-- Regular season
# cp html/2024_2025/playoffs.html /home/bileschi_2016/bileschi.com/nfl/index.html # <-- Playoffs
cp html/2025_2026/nfl_pickem.html /home/bileschi_2016/bileschi.com/nfl/index.html # <-- Regular season
