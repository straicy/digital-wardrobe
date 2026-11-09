import os
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import engine
from .models import User

router = APIRouter(prefix="/auth", tags=["auth"])
password_hash = PasswordHash.recommended()
dummy_hash = password_hash.hash("unused-password")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
jwt_secret = os.environ["JWT_SECRET"]


def get_db():
    with Session(engine) as db:
        yield db


Database = Annotated[Session, Depends(get_db)]


class RegisterRequest(BaseModel):
    username: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=3, max_length=50)
    ]
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def unauthorized() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="Невірні дані для входу або токен",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: RegisterRequest, db: Database):
    user = User(
        username=data.username,
        email=data.email,
        password_hash=password_hash.hash(data.password),
        created_at=datetime.now(UTC).replace(tzinfo=None),
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        message = str(exc.orig)
        if "(2627)" in message or "(2601)" in message:
            raise HTTPException(
                status_code=409,
                detail="Користувач із таким іменем або email уже існує",
            ) from exc
        raise

    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: Database):
    user = db.scalar(select(User).where(User.username == form.username.strip()))
    stored_hash = user.password_hash if user is not None else dummy_hash
    valid_password = password_hash.verify(form.password, stored_hash)
    if user is None or not valid_password:
        raise unauthorized()

    token = jwt.encode(
        {"sub": str(user.id), "exp": datetime.now(UTC) + timedelta(minutes=30)},
        jwt_secret,
        algorithm="HS256",
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(token: Annotated[str, Depends(oauth2_scheme)], db: Database):
    try:
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            options={"require": ["sub", "exp"]},
        )
        user_id = int(payload["sub"])
    except (InvalidTokenError, ValueError) as exc:
        raise unauthorized() from exc

    user = db.get(User, user_id)
    if user is None:
        raise unauthorized()
    return user