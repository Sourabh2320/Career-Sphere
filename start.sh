#!/usr/bin/env bash

# This script creates database tables if they don't exist,
# and then starts the Gunicorn web server.

# Create database tables
python create_db.py

# Start the Gunicorn server
gunicorn --bind 0.0.0.0:$PORT app:app