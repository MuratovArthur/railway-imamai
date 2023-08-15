from fastapi import Depends, HTTPException, status

from app.utils import AppModel

from ..service import Service, get_service
from . import router
from ..adapters.jwt_service import JWTData
from .dependencies import parse_jwt_user_data
from fastapi.responses import Response


class UpdateUserRequest(AppModel):
    phone: str
    name: str
    city: str


class UpdateUserResponse(AppModel):
    phone: str
    name: str
    city: str


@router.patch("/users/me", response_model=UpdateUserResponse)
def update_user(
    input: UpdateUserRequest,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
) -> dict[str, str]:
    modified = svc.repository.update_user(jwt_data.user_id, input.dict())
    if modified:
        return Response(status_code=200)
    else:
        Response(status_code=417)
