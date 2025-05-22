from fastapi import FastAPI

app = FastAPI(
    title="Comment Picker API",
    description="API for processing and analyzing lecture feedback comments.",
    version="0.1.0",
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Comment Picker API"}

from .routers import comments
from .database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app.include_router(comments.router, prefix="/api/v1/comments", tags=["comments"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
