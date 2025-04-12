from fastapi import APIRouter, HTTPException
from ..models import Users
from starlette import status
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from ..schemas.users import UserResponse
from ..schemas.error import ErrorResponse
from ..dependencies.db import db_dependency
from ..dependencies.auth import user_dependency

router = APIRouter(prefix="/user", tags=["user"])

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
    responses={
        401: {"description": "Authentication Failed", "model": ErrorResponse},
    },
)
async def get_user(user: user_dependency, db: db_dependency):
    """사용자 정보를 반환합니다."""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    return db.query(Users).filter(Users.id == user.get("id")).first()


@router.put(
    "/password",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {
            "description": "Unauthorized: Either not logged in or password verification failed",
            "model": ErrorResponse,
        },
    },
)
async def change_password(
    user: user_dependency, db: db_dependency, user_verification: UserVerification
):
    """사용자 비밀번호를 변경합니다."""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bcrypt_context.verify(
        user_verification.password, user_model.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Error on password verification")

    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()


@router.put(
    "/phonenumver/{phone_number}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"description": "Authentication Failed", "model": ErrorResponse},
    },
)
async def change_phone_number(
    user: user_dependency, db: db_dependency, phone_number: str
):
    """사용자 전화번호를 변경합니다."""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()
