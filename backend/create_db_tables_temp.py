import sys
import os
from flask import Flask
from models.db import init_db

# Create a minimal Flask app just for database initialization
app = Flask(__name__)

# Initialize the database and create tables
init_db(app)

print("Database tables created successfully.")

sys.exit(0)