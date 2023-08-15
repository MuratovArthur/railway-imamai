from fastapi import Depends, HTTPException, status, Response
from typing import Any
from pydantic import Field

from app.utils import AppModel

from ..service import Service, get_service
from . import router
from app.auth.adapters.jwt_service import JWTData
from app.auth.router.dependencies import parse_jwt_user_data
from datetime import datetime


@router.get(
    "/{language}/new",
)
def imam_answer(
    language: str,
    svc: Service = Depends(get_service),
):
    conv_id = svc.repository.create_conv(language)

    if conv_id:
        print(conv_id)
        return str(conv_id)
    else:
        return Response(status_code=404)
