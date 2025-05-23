from fastapi import APIRouter, HTTPException, Path, Query, Request
from TodoApp.models import Todos
from typing import Optional
from sqlalchemy import or_, asc, desc
from starlette import status
from pydantic import BaseModel, Field, validator
from datetime import datetime
from ..schemas.todos import TodoResponse
from ..schemas.pagination import PaginatedResponse
from ..schemas.error import ErrorResponse
from ..utils.pagination import paginate
from ..dependencies.db import db_dependency
from ..dependencies.auth import user_dependency

router = APIRouter(
    prefix="/todo",
    tags=["todos"],
)


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool = Field(default=False)
    category_id: Optional[int] = None

    @validator("title")
    def title_not_blank(cls, v):
        if not v.strip():
            raise ValueError("제목은 공백만으로 이뤄질 수 없습니다.")
        return v

    @validator("description")
    def description_min_length(cls, v):
        if v and len(v.strip()) < 10:
            raise ValueError("설명은 최소 10자 이상이어야 합니다.")
        return v

    @validator("category")
    def validate_category(cls, v):
        valid_categories = {"work", "personal", "study", "health"}
        if v and v not in valid_categories:
            raise ValueError(f"'{v}'는 유효하지 않은 카테고리입니다. 가능한 값: {valid_categories}")
        return v


@router.get(
    "",
    response_model=PaginatedResponse[TodoResponse],
    status_code=status.HTTP_200_OK,
    description="유저의 전체 todo 목록을 반환합니다.",
    responses={
        401: {
            "description": "Authentication Failed",
            "model": ErrorResponse,
        },
        404: {
            "description": "Invalid sort field: {sort_field}",
            "model": ErrorResponse,
        },
    },
)
@paginate(TodoResponse)
async def read_all(
    request: Request,  # pagination을 위한 request
    user: user_dependency,
    db: db_dependency,
    complete: Optional[bool] = Query(None, description="완료 여부 필터 (true 또는 false)"),
    category_id: Optional[int] = Query(None, description="카테고리 ID 필터"),
    search: Optional[str] = Query(None, description="검색어 (제목에 포함된 단어)"),
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


@router.get(
    "/{todo_id}",
    status_code=status.HTTP_200_OK,
    response_model=TodoResponse,
    responses={
        401: {
            "description": "Authentication Failed",
            "model": ErrorResponse,
        },
        404: {
            "description": "Todo not found",
            "model": ErrorResponse,
        },
    },
)
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


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
    responses={
        401: {
            "description": "Authentication Failed",
            "model": ErrorResponse,
        },
    },
)
async def create_todo(
    user: user_dependency, db: db_dependency, todo_request: TodoRequest
):
    """새로운 todo를 생성합니다."""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    new_todo = Todos(**todo_request.dict(), owner_id=user.get("id"))
    db.add(new_todo)
    db.commit()


@router.put(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    responses={
        401: {
            "description": "Authentication Failed",
            "model": ErrorResponse,
        },
        404: {
            "description": "Todo not found",
            "model": ErrorResponse,
        },
    },
)
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


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    responses={
        401: {
            "description": "Authentication Failed",
            "model": ErrorResponse,
        },
        404: {
            "description": "Todo not found",
            "model": ErrorResponse,
        },
    },
)
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
