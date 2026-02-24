#!/usr/bin/env python3
"""
Housing Safety Advisory Agent - Backend Server
"""
from app import create_app
from app.config import Config

app = create_app()

if __name__ == '__main__':
    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )
