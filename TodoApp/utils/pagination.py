from functools import wraps
from fastapi import Request
from typing import Callable, Type, TypeVar, Awaitable
from sqlalchemy.orm import Query as SAQuery
from sqlalchemy import func as sql_func
from pydantic import BaseModel
from ..schemas.pagination import PaginatedResponse
from math import ceil

T = TypeVar("T", bound=BaseModel)


def paginate(schema: Type[T]) -> Callable:
    """pagination decorator"""

    def decorator(func: Callable[..., Awaitable[SAQuery]]) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> PaginatedResponse[T]:
            # request 가져오기
            request: Request = kwargs.get("request")
            if request is None:
                raise ValueError(
                    "Missing 'request' in kwargs. Make sure it's declared in your route function."
                )

            # 쿼리 파라미터에서 페이지와 페이지 크기 가져오기
            query_params = request.query_params
            page = int(query_params.get("page", 1))
            page_size = int(query_params.get("page_size", 10))

            # 기존 쿼리 실행
            query = await func(*args, **kwargs)

            # 쿼리 결과가 SQLAlchemy Query인지 확인
            if not isinstance(query, SAQuery):
                raise TypeError("Paginate target must return SQLAlchemy Query.")

            # 페이지네이션 처리
            total_count = query.with_entities(sql_func.count()).scalar()
            page_count = ceil(total_count / page_size)

            offset = (page - 1) * page_size
            items = query.offset(offset).limit(page_size).all()

            # 결과를 Pydantic 모델로 변환
            return PaginatedResponse[schema](
                totalCnt=total_count,
                pageCnt=page_count,
                curPage=page,
                nextPage=page + 1 if page < page_count else None,
                previousPage=page - 1 if page > 1 else None,
                data=[schema.model_validate(obj) for obj in items],
            )

        return wrapper

    return decorator
