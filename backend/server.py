#!/usr/bin/env python3
"""
Housing Safety Advisory Agent - FastAPI Server
"""
import uvicorn
from app.config import Config

if __name__ == '__main__':
    uvicorn.run(
        "app.main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG
    )
