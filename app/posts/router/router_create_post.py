from fastapi import Depends, Response
from app.auth.adapters.jwt_service import JWTData
from app.auth.router.dependencies import parse_jwt_user_data
from app.utils import AppModel
from ..service import Service, get_service
from . import router


class CreatePostRequest(AppModel):
    title: str
    imageURL: str
    description: str


@router.post("/{language}")
def create_post(
    language: str,
    input: CreatePostRequest,
    svc: Service = Depends(get_service),
):
    post = {
        "title": input.title,
        "imageURL": input.imageURL,
        "description": input.description,
    }
    post_id = svc.repository.create_post(post, language)

    if post_id:
        return Response(status_code=200)
    else:
        return Response(status_code=501)
