import sys
import os

# Add parent directory to sys.path so backend package is importable
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.main import app

# Export app for Vercel Serverless Function handler
app = app
