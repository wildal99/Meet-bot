#!/bin/bash
# 1. Start the Flask server in the background (&)
# We use gunicorn for stability in production
gunicorn server:app &

# 2. Start the Discord bot in the foreground
python bot.py