from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db.base import engine
from app.db.models import Base
from app.routers import infer, history, dataset, train, models, evaluate

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="img2LaTeX AI API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

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
app.include_router(dataset.router, prefix="/api")
app.include_router(train.router, prefix="/api")
app.include_router(models.router, prefix="/api")
app.include_router(evaluate.router, prefix="/api")


@app.get("/health")
def health():
    return {"ok": True} 