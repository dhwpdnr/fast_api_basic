from fastapi import APIRouter, Depends, HTTPException, Path, Query
from TodoApp.models import Todos
from TodoApp.database import SessionLocal
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field
from datetime import datetime
from .auth import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool
    category_id: Optional[int] = None


@router.get("/")
async def read_all(
    user: user_dependency,
    db: db_dependency,
    complete: Optional[bool] = Query(None, description="완료 여부 필터 (true 또는 false)"),
    category_id: Optional[int] = Query(None, description="카테고리 ID 필터"),
):
    """전체 todo 목록을 반환합니다."""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    query = db.query(Todos).filter(Todos.owner_id == user.get("id"))

    if complete is not None:
        query = query.filter(Todos.complete == complete)
    if category_id is not None:
        query = query.filter(Todos.category == category_id)

    return query.all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    """id에 해당하는 todo를 반환합니다."""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )

    if todo_model:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(
    user: user_dependency, db: db_dependency, todo_request: TodoRequest
):
    """새로운 todo를 생성합니다."""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    new_todo = Todos(**todo_request.dict(), owner_id=user.get("id"))
    db.add(new_todo)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    user: user_dependency,
    db: db_dependency,
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    if todo_request.complete and not todo_model.completed_at:
        todo_model.completed_at = datetime.now()
    elif not todo_request.complete:
        todo_model.completed_at = None

    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
