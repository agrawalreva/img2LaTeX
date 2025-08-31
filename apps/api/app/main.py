from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db.base import engine
from .db.models import Base
from .routers import infer, history

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="VisionLaTeX Studio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(infer.router, prefix="/api")
app.include_router(history.router, prefix="/api")


@app.get("/health")
def health():
    return {"ok": True} 