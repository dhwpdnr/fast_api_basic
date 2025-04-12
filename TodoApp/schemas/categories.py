from pydantic import BaseModel, ConfigDict


class CategoryResponse(BaseModel):
    """카테고리 응답 모델"""

    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
