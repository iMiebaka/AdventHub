from fastapi import APIRouter, Depends
from settings import Engine
from src.models.user import User
from src.models.exhortation import Exhortation
from src.schema.exhortation import CreateExhortationSchema, ExhortationSchema, ExhortationListSchema, UpdateExhortationSchema
from src.schema.comment import CreateCommentSchema
from src.utils.security import get_current_user_instance
from src.utils.exceptions import *
import logging, math
from typing import Optional
from datetime import datetime

LOGGER = logging.getLogger(__name__)
engine = Engine
router = APIRouter(
    prefix="/exhortation",
    tags=["exhortation"],
    responses={404: {"details": "Not found"}},
)



@router.post("", response_model=ExhortationSchema)
async def create(
    exhortation: CreateExhortationSchema,
    current_user: User = Depends(get_current_user_instance)
):
    try:
        exhortation = Exhortation(**exhortation.model_dump(), author=current_user)
        current_user.exhortation.append(exhortation.id)
        await engine.save_all([exhortation, current_user])
        return exhortation
    except Exception as ex:
        raise HTTPException(400, detail=str(ex))


@router.get("")
async def get(
    slug: Optional[str] = None,
    page: Optional[int] = 1,
    limit: Optional[int] = 20,
):  
    if slug:
        exhortation = await engine.find_one(Exhortation, Exhortation.slug == slug)
        if exhortation is None:
            raise HTTPException(404, detail="We could not find this Exhortation")
        return ExhortationSchema(**exhortation.model_dump())
    else:
        count = await engine.count(model=Exhortation)
        skip = (page - 1) * limit
        exhortation = await engine.find(model=Exhortation, skip=skip, limit=limit)
        total_page = math.ceil(count/limit) if count >= limit else 1
        data = [ExhortationSchema(**e.model_dump()) for e in exhortation]
        return ExhortationListSchema(page=page, data=data, total_page=total_page, count=count)
    

@router.put("", response_model=ExhortationSchema)
async def update(
    slug: str,
    patch: UpdateExhortationSchema,
    current_user: User = Depends(get_current_user_instance)
):
    result = await engine.find_one(Exhortation, Exhortation.slug == slug)
    if result is None:
        raise HTTPException(404, detail="We could not find this Exhortation")
    if result.author.id != current_user.id:
        raise HTTPException(401, detail="We could not find this Exhortation")
    try:
        result.model_update(patch)
        result.edited = True
        result.edited_at = datetime.utcnow()
        await engine.save(result)
        return result
    except Exception as ex:
        raise HTTPException(400, detail=str(ex))


@router.delete("", status_code=204)
async def delete(
    slug: str,
    current_user: User = Depends(get_current_user_instance)
):
    exhortation = await engine.find_one(Exhortation, Exhortation.slug == slug)
    if exhortation is None:
            raise HTTPException(404, detail="We could not find this Exhortation")
    if exhortation.author.id != current_user.id:
        raise HTTPException(401, detail="We could not find this Exhortation")
    current_user.exhortation.remove(exhortation.id)
    await engine.delete(exhortation)
    await engine.save(current_user)
    return {"message": "Exhortation deleted"}
