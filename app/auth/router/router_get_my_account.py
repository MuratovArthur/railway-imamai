from typing import Any, Optional

from fastapi import Depends, Response
from pydantic import Field

from app.utils import AppModel

from ..adapters.jwt_service import JWTData
from ..service import Service, get_service
from . import router
from .dependencies import parse_jwt_user_data


class GetMyAccountResponse(AppModel):
    id: Any = Field(alias="_id")
    email: str
    phone: Optional[str]
    name: Optional[str]
    city: Optional[str]
    avatar_url: Optional[Any]


@router.get("/users/me", response_model=GetMyAccountResponse)
def get_my_account(
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
) -> dict[str, str]:
    user = svc.repository.get_user_by_id(jwt_data.user_id)
    if user:
        return user
    else:
        return Response(status_code=404)
