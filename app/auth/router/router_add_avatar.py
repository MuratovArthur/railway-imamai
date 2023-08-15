from fastapi import Depends, HTTPException, status, UploadFile

from app.utils import AppModel

from ..service import Service, get_service
from . import router
from ..adapters.jwt_service import JWTData
from .dependencies import parse_jwt_user_data
from fastapi.responses import Response


@router.post(
    "/users/avatar",
)
def upload_avatar(
    avatar: UploadFile,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    url = svc.s3_service.upload_media(avatar.file, avatar.filename)
    added_media = svc.repository.add_avatar(jwt_data.user_id, url)

    if added_media:
        return Response(status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
