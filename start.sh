#!/bin/sh
set -e
pip install -r requirements.txt
playwright install chromium
python app.py
