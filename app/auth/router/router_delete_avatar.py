from fastapi import Depends, HTTPException, status, UploadFile

from app.utils import AppModel

from ..service import Service, get_service
from . import router
from ..adapters.jwt_service import JWTData
from .dependencies import parse_jwt_user_data
from fastapi.responses import Response


@router.delete(
    "/users/avatar",
)
def delete_avatar(
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    deleted = svc.s3_service.delete_avatar(jwt_data.user_id)

    if deleted:
        modified = svc.repository.remove_avatar_url_user(jwt_data.user_id)
        if modified:
            return Response(status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
