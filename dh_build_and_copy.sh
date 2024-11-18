#!/bin/bash

# go to dir
cd /home/bileschi_2016/proj/pierogi_pickem
# use virtual env
source venv/bin/activate
# regenerate csv & html
python3 main.py
python3 generate_html.py
# copy output to web.
cp html/2024_2025/nfl_pickem.html /home/bileschi_2016/bileschi.com/nfl/index.html
