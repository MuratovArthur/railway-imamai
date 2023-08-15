from fastapi import Depends, HTTPException, status, Response
from typing import Any
from pydantic import Field

from app.utils import AppModel

from ..service import Service, get_service
from . import router
from app.auth.adapters.jwt_service import JWTData
from app.auth.router.dependencies import parse_jwt_user_data
from datetime import datetime


class ImamAnswerRequest(AppModel):
    question: str


@router.post(
    "/{chat_id}",
)
def imam_answer(
    chat_id: str,
    input: ImamAnswerRequest,
    svc: Service = Depends(get_service),
):
    messages = svc.repository.get_messages(chat_id)
    messages.append({"role": "user", "content": f"{input.question}"})
    messages_with_response = svc.openai_service.get_response(messages)
    print(messages_with_response)
    updated = svc.repository.update_messages(chat_id, messages_with_response)
    if updated:
        return messages_with_response[-1]["content"]
    else:
        return Response(status_code=404)
