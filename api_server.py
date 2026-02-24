#!/usr/bin/env python3
"""
Legacy entry point - redirects to new backend structure.
For new development, use: cd backend && python server.py
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app
from app.config import Config

app = create_app()

if __name__ == '__main__':
    print("⚠️  Using legacy entry point. Consider using: cd backend && python server.py")
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)