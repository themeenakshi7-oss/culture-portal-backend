from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base

from routes.auth import router as auth_router

import models.user

app = FastAPI()

# CREATE TABLES
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTES
app.include_router(auth_router)

@app.get("/")
def home():

    return {
        "message": "Backend Running Successfully"
    }
