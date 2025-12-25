from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db.base import engine
from app.db.models import Base
from app.routers import infer, history, models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="img2LaTeX AI API")

static_dir = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

uploads_dir = Path(__file__).parent.parent / "uploads"
uploads_dir.mkdir(exist_ok=True)
app.mount("/api/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(infer.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(models.router, prefix="/api")


@app.get("/health")
def health():
    return {"ok": True} 