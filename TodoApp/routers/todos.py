from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from TodoApp.models import Todos
from TodoApp.database import SessionLocal
from typing import Annotated, Optional
from math import ceil
from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc, func
from starlette import status
from pydantic import BaseModel, Field
from datetime import datetime
from .auth import get_current_user
from ..schemas.todos import TodoResponse
from ..schemas.pagination import PaginatedResponse
from ..utils.pagination import paginate

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
@paginate(TodoResponse)
async def read_all(
    request: Request,  # pagination을 위한 request
    user: user_dependency,
    db: db_dependency,
    complete: Optional[bool] = Query(None, description="완료 여부 필터 (true 또는 false)"),
    category_id: Optional[int] = Query(None, description="카테고리 ID 필터"),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query(None, description="정렬 기준 (예: priority, -priority)"),
):
    """전체 todo 목록을 반환합니다."""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    query = db.query(Todos).filter(Todos.owner_id == user.get("id"))

    # 검색 필터
    if search:
        query = query.filter(
            or_(
                Todos.title.ilike(f"%{search}%"), Todos.description.ilike(f"%{search}%")
            )
        )

    # 완료 필터
    if complete is not None:
        query = query.filter(Todos.complete == complete)

    # 카테고리 필터
    if category_id is not None:
        query = query.filter(Todos.category == category_id)

    # 정렬
    if sort:
        is_desc = sort.startswith("-")
        sort_field = sort.lstrip("-")

        if hasattr(Todos, sort_field):
            column = getattr(Todos, sort_field)
            query = query.order_by(desc(column) if is_desc else asc(column))
        else:
            raise HTTPException(
                status_code=400, detail=f"Invalid sort field: {sort_field}"
            )

    return query


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
