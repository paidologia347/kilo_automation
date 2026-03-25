#!/bin/sh
pip install -r requirements.txt
playwright install chromium
python app.py
