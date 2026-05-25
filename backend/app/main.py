from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
from pathlib import Path

from app.config import Config
from app.api.routes_fastapi import router
from app.api.auth import router as auth_router
from app.models.user import init_db

logging.basicConfig(level=logging.INFO)

# Initialize database
init_db()

app = FastAPI(title="Housing Safety Advisory Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(router)

# Serve React frontend if built
frontend_path = Path(Config.FRONTEND_BUILD_PATH)
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path / "static")), name="static")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Issue 5 fix — resolve and verify path stays inside frontend_path
        # to prevent path traversal attacks (e.g. ../../secret)
        resolved = (frontend_path / full_path).resolve()
        if not str(resolved).startswith(str(frontend_path.resolve())):
            from fastapi.responses import Response
            return Response(status_code=400)
        if resolved.is_file():
            return FileResponse(resolved)
        return FileResponse(frontend_path / "index.html")
