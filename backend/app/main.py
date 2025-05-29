from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import csv

app = FastAPI(title="Comment Picker API", description="API for CSV upload and pagination")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Include routers
app.include_router(csv.router)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Comment Picker!"}
