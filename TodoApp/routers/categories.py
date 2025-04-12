from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from TodoApp.database import SessionLocal
from TodoApp.models import Category
from typing import Annotated
from starlette import status
from ..utils.pagination import paginate
from ..schemas.error import ErrorResponse
from ..schemas.categories import CategoryResponse
from ..schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/categories", tags=["Categories"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class CategoryRequest(BaseModel):
    name: str


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    description="카테고리 생성",
    responses={
        400: {
            "description": "Bad Request: Category already exists",
            "model": ErrorResponse,
        },
    },
)
async def create_category(category: CategoryRequest, db: db_dependency):
    existing_category = (
        db.query(Category).filter(Category.name == category.name).first()
    )
    if existing_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    new_category = Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@router.get(
    "/",
    response_model=PaginatedResponse[CategoryResponse],
    status_code=status.HTTP_200_OK,
    description="모든 카테고리 목록을 반환합니다.",
)
@paginate(CategoryResponse)
async def list_categories(db: db_dependency, request: Request):
    categories = db.query(Category)
    return categories


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    description="카테고리 상세 조회",
    responses={
        404: {"description": "Category not found", "model": ErrorResponse},
    },
)
async def get_category(category_id: int, db: db_dependency):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete(
    "/{category_id}",
    status_code=204,
    response_model=None,
    description="카테고리 삭제",
    responses={
        404: {"description": "Category not found", "model": ErrorResponse},
    },
)
async def delete_category(category_id: int, db: db_dependency):
    category_model = db.query(Category).filter(Category.id == category_id).first()
    if not category_model:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category_model)
    db.commit()
