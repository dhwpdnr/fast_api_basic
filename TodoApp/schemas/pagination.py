from typing import Generic, TypeVar, List, Optional
from pydantic.generics import GenericModel

T = TypeVar("T")


class PaginatedResponse(GenericModel, Generic[T]):
    """페이지네이션된 응답 모델"""

    totalCnt: int
    pageCnt: int
    curPage: int
    nextPage: Optional[int]
    previousPage: Optional[int]
    data: List[T]
