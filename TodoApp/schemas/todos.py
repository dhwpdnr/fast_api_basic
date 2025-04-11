from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class TodoResponse(BaseModel):
    """Todo 응답 모델"""

    id: int
    title: str
    description: str
    priority: int
    complete: bool
    owner_id: int
    category_id: Optional[int]
    completed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
