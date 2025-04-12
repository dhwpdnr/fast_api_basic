from fastapi import Depends
from typing import Annotated
from ..routers.auth import get_current_user

user_dependency = Annotated[dict, Depends(get_current_user)]
