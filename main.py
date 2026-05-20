from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes.auth import router as auth_router
import models.user_session
import models.failed_login
import models.user

app = FastAPI()


# CREATE TABLES
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://culture-portal-frontend.onrender.com",
        "https://icpdelhistage.nvli.in"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTES
app.include_router(auth_router)


@app.get("/")
def home():

    return {"message": "Backend Running Successfully"}
