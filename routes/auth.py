# from fastapi import APIRouter, Depends, HTTPException
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

# from utils.jwt_handler import create_access_token

# router = APIRouter()

# # DATABASE SESSION
# def get_db():

#     db = SessionLocal()

#     try:
#         yield db

#     finally:
#         db.close()

# # REGISTER API
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
#         name=user.name,
#         email=user.email,
#         password=hashed_password
#     )

#     db.add(new_user)

#     db.commit()

#     return {
#         "message": "User Registered Successfully"
#     }

# # LOGIN API
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
#         "name": db_user.name
#     }

from fastapi import APIRouter, Depends, HTTPException
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

from utils.jwt_handler import create_access_token

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from jose import jwt, JWTError

router = APIRouter()

security = HTTPBearer()

SECRET_KEY = "MYSECRETKEY"

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


# LOGIN API
@router.post("/login")
def login(
    user: LoginSchema,
    db: Session = Depends(get_db)
):

    db_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not db_user:

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

    token = create_access_token({
        "email": db_user.email,
        "id": db_user.id
    })

    return {
        "access_token": token,
        "fullname": db_user.fullname
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