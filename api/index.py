# Vercel serverless function entry point
# This file serves as the main entry point for Vercel deployment
# Updated to force new deployment

from flask import Flask
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from main import app
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback app jika import gagal
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return "HAR GI Dashboard - Import Error"

# This is the entry point for Vercel
if __name__ == '__main__':
    app.run()
else:
    # Untuk Vercel deployment
    application = app