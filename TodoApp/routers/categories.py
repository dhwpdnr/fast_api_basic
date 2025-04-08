from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from TodoApp.database import SessionLocal
from TodoApp.models import Category
from typing import Annotated
from starlette import status

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


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryRequest, db: db_dependency):
    existing_category = db.query(Category).filter(Category.name == category.name).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    new_category = Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return {"id": new_category.id, "name": new_category.name}


@router.get("/", response_model=list[dict])
def list_categories(db: db_dependency):
    categories = db.query(Category).all()
    return [{"id": category.id, "name": category.name} for category in categories]


@router.get("/{category_id}", response_model=dict)
def get_category(category_id: int, db: db_dependency):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"id": category.id, "name": category.name}


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: db_dependency):
    category_model = db.query(Category).filter(Category.id == category_id).first()
    if not category_model:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category_model)
    db.commit()
