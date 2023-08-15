from fastapi import Depends, HTTPException, status, Response, Query

from app.auth.adapters.jwt_service import JWTData
from app.auth.router.dependencies import parse_jwt_user_data
from app.utils import AppModel

from ..service import Service, get_service
from . import router
from typing import Any, Optional, List
from pydantic import Field


class GetPostResponse(AppModel):
    id: Any = Field(alias="_id")
    title: str
    imageURL: str
    description: str


class GetShanyraksResponse(AppModel):
    total: int
    objects: List[GetPostResponse]


@router.get("/get_posts/{language}", response_model=GetShanyraksResponse)
def get_shanyraks(
    language: str,
    svc: Service = Depends(get_service),
    limit: int = Query(None, description="Number of records to display per page"),
    offset: int = Query(
        None, description="Starting point of data display in the dataset"
    ),
) -> GetShanyraksResponse:
    if limit is None or offset is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit and offset are mandatory to specify",
        )

    result = svc.repository.get_posts_from_db(limit, offset, language)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No shanyraks found",
        )

    return GetShanyraksResponse(total=result["total"], objects=result["objects"])
