from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    Request
)
from models.user_session import UserSession
from models.failed_login import FailedLogin
from datetime import datetime, timedelta
from user_agents import parse
from sqlalchemy.orm import Session

from database import SessionLocal
from models.user import User

from schemas.auth_schema import (
    RegisterSchema,
    LoginSchema
)

from utils.password import (
    hash_password,
    verify_password
)

from utils.jwt_handler import (
    create_access_token,
    create_refresh_token
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from jose import jwt, JWTError
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY")

# SECRET_KEY = "MYSECRETKEY"

ALGORITHM = "HS256"


# DATABASE SESSION
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# REGISTER API
@router.post("/register")
def register(
    user: RegisterSchema,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    hashed_password = hash_password(
        user.password
    )

    new_user = User(
        fullname=user.fullname,
        designation=user.designation,
        email=user.email,
        mobile=user.mobile,
        organization=user.organization,
        country=user.country,
        password=hashed_password
    )

    db.add(new_user)

    db.commit()

    return {
        "message": "User Registered Successfully"
    }


# # LOGIN API OLD
# @router.post("/login")
# def login(
#     user: LoginSchema,
#     db: Session = Depends(get_db)
# ):

#     db_user = db.query(User).filter(
#         User.email == user.email
#     ).first()

#     if not db_user:

#         raise HTTPException(
#             status_code=400,
#             detail="Invalid Email"
#         )

#     valid_password = verify_password(
#         user.password,
#         db_user.password
#     )

#     if not valid_password:

#         raise HTTPException(
#             status_code=400,
#             detail="Invalid Password"
#         )

#     token = create_access_token({
#         "email": db_user.email,
#         "id": db_user.id
#     })

#     return {
#         "access_token": token,
#         "fullname": db_user.fullname
#     }

@router.post("/login")
def login(
    request: Request,
    response: Response,
    user: LoginSchema,
    db: Session = Depends(get_db)
):

    db_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not db_user:

        # STORE FAILED LOGIN
        failed = FailedLogin(
            email=user.email,
            ip_address=request.client.host,
            attempt_time=datetime.utcnow()
        )

        db.add(failed)

        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Invalid Email"
        )

    valid_password = verify_password(
        user.password,
        db_user.password
    )

    if not valid_password:

        raise HTTPException(
            status_code=400,
            detail="Invalid Password"
        )

    access_token = create_access_token({
        "email": db_user.email,
        "id": db_user.id,
    })

    refresh_token = create_refresh_token({
        "email": db_user.email,
        "id": db_user.id,
        "type": "refresh"
    })

    user_agent = request.headers.get(
        "user-agent"
    )

    parsed_agent = parse(user_agent)

    ip_address = request.client.host

    browser = parsed_agent.browser.family

    device = parsed_agent.device.family

    expiry = datetime.utcnow() + timedelta(days=7)

    session = UserSession(
        user_id=db_user.id,
        refresh_token=refresh_token,
        ip_address=ip_address,
        browser=browser,
        device=device,
        login_time=datetime.utcnow(),
        session_expiry=expiry,
        status="active"
    )

    db.add(session)

    db.commit()

    # STORE REFRESH TOKEN IN COOKIE
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=7 * 24 * 60 * 60
    )

    return {
        "access_token": access_token,
        "fullname": db_user.fullname
    }


@router.post("/refresh")
def refresh_token(
    request: Request
):

    refresh_token = request.cookies.get(
        "refresh_token"
    )

    if not refresh_token:

        raise HTTPException(
            status_code=401,
            detail="Refresh token missing"
        )

    try:

        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "refresh":

            raise HTTPException(
                status_code=401,
                detail="Invalid token type"
            )

        new_access_token = create_access_token({
            "email": payload["email"],
            "id": payload["id"]
        })

        return {
            "access_token": new_access_token
        }

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):

    refresh_token = request.cookies.get(
        "refresh_token"
    )

    # FIND SESSION
    session = db.query(UserSession).filter(
        UserSession.refresh_token == refresh_token
    ).first()

    if session:

        session.logout_time = datetime.utcnow()

        session.status = "logged_out"

        db.commit()

    # DELETE COOKIE
    response.delete_cookie(
        key="refresh_token"
    )

    return {
        "message": "Logged out successfully"
    }


# GET CURRENT USER
@router.get("/me")
def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_email = payload.get("email")

        user = db.query(User).filter(
            User.email == user_email
        ).first()

        if not user:

            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return {
            "id": user.id,
            "fullname": user.fullname,
            "email": user.email,
            "designation": user.designation,
            "mobile": user.mobile,
            "organization": user.organization,
            "country": user.country
        }

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


# from fastapi import (
#     APIRouter,
#     Depends,
#     HTTPException,
#     Response,
#     Request
# )

# from sqlalchemy.orm import Session

# from database import SessionLocal

# from models.user import User

# from schemas.auth_schema import (
#     RegisterSchema,
#     LoginSchema
# )

# from utils.password import (
#     hash_password,
#     verify_password
# )

# from utils.jwt_handler import (
#     create_access_token,
#     create_refresh_token,
#     verify_token
# )

# from fastapi.security import (
#     HTTPBearer,
#     HTTPAuthorizationCredentials
# )
# from fastapi.responses import JSONResponse

# router = APIRouter()

# security = HTTPBearer()


# # =========================
# # DATABASE SESSION
# # =========================

# def get_db():

#     db = SessionLocal()

#     try:
#         yield db

#     finally:
#         db.close()


# # =========================
# # REGISTER API
# # =========================

# @router.post("/register")
# def register(
#     user: RegisterSchema,
#     db: Session = Depends(get_db)
# ):

#     existing_user = db.query(User).filter(
#         User.email == user.email
#     ).first()

#     if existing_user:

#         raise HTTPException(
#             status_code=400,
#             detail="Email already exists"
#         )

#     hashed_password = hash_password(
#         user.password
#     )

#     new_user = User(
#         fullname=user.fullname,
#         designation=user.designation,
#         email=user.email,
#         mobile=user.mobile,
#         organization=user.organization,
#         country=user.country,
#         password=hashed_password
#     )

#     db.add(new_user)

#     db.commit()

#     return {
#         "message": "User Registered Successfully"
#     }


# # =========================
# # LOGIN API
# # =========================

# @router.post("/login")
# def login(
#     user: LoginSchema,
#     response: Response,
#     db: Session = Depends(get_db)
# ):

#     db_user = db.query(User).filter(
#         User.email == user.email
#     ).first()

#     if not db_user:

#         raise HTTPException(
#             status_code=400,
#             detail="Invalid Email"
#         )

#     valid_password = verify_password(
#         user.password,
#         db_user.password
#     )

#     if not valid_password:

#         raise HTTPException(
#             status_code=400,
#             detail="Invalid Password"
#         )

#     access_token = create_access_token({
#         "email": db_user.email,
#         "id": db_user.id
#     })

#     refresh_token = create_refresh_token({
#         "email": db_user.email,
#         "id": db_user.id
#     })

#     response.set_cookie(
#         key="refresh_token",
#         value=refresh_token,
#         httponly=True,

#         # localhost testing
#         secure=False,

#         # production
#         # secure=True,

#         samesite="lax",
#         max_age=60 * 60 * 24 * 7
#     )

#     return {
#         "access_token": access_token,
#         "fullname": db_user.fullname
#     }


# # =========================
# # REFRESH TOKEN API
# # =========================

# from fastapi import Request

# @router.post("/refresh")
# def refresh_token(request: Request):

#     refresh_token = request.cookies.get("refresh_token")

#     if not refresh_token:
#         return {
#             "detail": "Refresh token missing"
#         }

#     payload = verify_token(refresh_token)

#     if not payload:
#         return {
#             "detail": "Invalid refresh token"
#         }

#     if payload.get("type") != "refresh":
#         return {
#             "detail": "Invalid token type"
#         }

#     email = payload.get("sub")

#     new_access_token = create_access_token({
#         "sub": email
#     })

#     return {
#         "access_token": new_access_token
#     }

# # =========================
# # LOGOUT API
# # =========================

# @router.post("/logout")
# def logout():

#     response = JSONResponse(content={
#         "message": "Logged out successfully"
#     })

#     response.delete_cookie("refresh_token")

#     return response

# # =========================
# # GET CURRENT USER
# # =========================

# @router.get("/me")
# def get_me(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     db: Session = Depends(get_db)
# ):

#     token = credentials.credentials

#     payload = verify_token(token)

#     if not payload:

#         raise HTTPException(
#             status_code=401,
#             detail="Invalid token"
#         )

#     user_email = payload.get("email")

#     user = db.query(User).filter(
#         User.email == user_email
#     ).first()

#     if not user:

#         raise HTTPException(
#             status_code=401,
#             detail="User not found"
#         )

#     return {
#         "id": user.id,
#         "fullname": user.fullname,
#         "email": user.email,
#         "designation": user.designation,
#         "mobile": user.mobile,
#         "organization": user.organization,
#         "country": user.country
#     }