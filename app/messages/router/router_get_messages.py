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
    "/{chat_id}",
)
def imam_answer(
    chat_id: str,
    svc: Service = Depends(get_service),
):
    messages = svc.repository.get_30_last_messages(chat_id)
    if messages:
        return messages
    else:
        return Response(status_code=404)
