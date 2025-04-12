from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    """사용자 응답 모델"""

    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    role: str
    phone_number: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
