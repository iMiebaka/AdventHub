from fastapi import APIRouter, Depends, UploadFile, File, Form
from settings import Engine
from src.models.user import User
from src.schema.exhortation import  ExhortationSchema, UpdateExhortationSchema
from src.utils.security import get_current_user_instance, get_current_user_optional_instance
from src.core import exhortation
from src.utils.exceptions import *
import logging
from typing import Optional, List


LOGGER = logging.getLogger(__name__)
engine = Engine
router = APIRouter(
    prefix="/exhortation",
    tags=["exhortation"],
    responses={404: {"details": "Not found"}},
)



@router.post("", response_model=ExhortationSchema, status_code=201)
async def create(
    body: str = Form(...),
    medias: List[UploadFile] = File(None),
    # payload: CreateExhortationSchema,
    current_user: User = Depends(get_current_user_instance)
):
    return await exhortation.create(exhortation=body, user=current_user)


@router.get("/{username}")
async def get(
    username: str,
    page: Optional[int] = 1,
    limit: Optional[int] = 20,
    current_user: User = Depends(get_current_user_optional_instance)
):  
    return await exhortation.get_exhortation_via_username(page=page, limit=limit, username=username, user=current_user)


@router.get("")
async def get(
    slug: Optional[str] = None,
    page: Optional[int] = 1,
    limit: Optional[int] = 20,
    current_user: User = Depends(get_current_user_optional_instance)

):  
    return await exhortation.get(slug=slug, page=page, limit=limit, user=current_user)


@router.put("", response_model=ExhortationSchema)
async def update(
    slug: str,
    patch: UpdateExhortationSchema,
    current_user: User = Depends(get_current_user_instance)
):
    return await exhortation.update(slug=slug, patch=patch, user=current_user)


@router.delete("", status_code=204)
async def delete(
    slug: str,
    current_user: User = Depends(get_current_user_instance)
):
    return await exhortation.delete(slug=slug, user=current_user)
