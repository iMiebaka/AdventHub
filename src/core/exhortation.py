from fastapi import Depends
from settings import Engine
from src.models.user import User
from src.models.exhortation import Exhortation, ExhortationReaction
from src.schema.exhortation import ExhortationSchema, ExhortationListSchema, UpdateExhortationSchema
from src.models.comment import CommentReaction
from src.utils.security import get_current_user_instance, get_current_user_optional_instance
from src.utils.exceptions import *
import logging, math, string, random
from typing import Optional, List
from datetime import datetime


LOGGER = logging.getLogger(__name__)
engine = Engine

def generate_alphanumeric(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


async def create(
    exhortation: str,
    user: User = Depends(get_current_user_instance)
):
    try:
        slug = generate_alphanumeric(10)
        exhortation = Exhortation(body=exhortation, author=user, slug=slug)
        await engine.save(exhortation)
        return exhortation
    except Exception as ex:
        raise HTTPException(400, detail=str(ex))


async def exhortation_list(user:User, exhortations: List[Exhortation], as_list=True) -> Exhortation:
    if as_list:
        payload = []
        for exhortation in exhortations:
            exhortation_data = exhortation.model_dump()
            # Check if liked
            if user:
                query = (ExhortationReaction.exhortation == exhortation_data["id"]) & (ExhortationReaction.user == user.id)
                isLiked = await engine.count(ExhortationReaction, query)
                exhortation_data["liked"] = isLiked > 0

            comment = await engine.count(
                CommentReaction, CommentReaction.comment == exhortation_data["id"])
            exhortation_data["comment"] = comment
            reaction = await engine.count(
                ExhortationReaction, ExhortationReaction.exhortation == exhortation_data["id"])
            exhortation_data["reaction"] = reaction
            payload.append(ExhortationSchema(**exhortation_data))
        return payload
    else:
        exhortation_data = exhortations[0].model_dump()
        if user:
            query = (ExhortationReaction.exhortation == exhortation_data["id"]) & (ExhortationReaction.user == user.id)
            isLiked = await engine.count(ExhortationReaction, query)
            exhortation_data["liked"] = isLiked > 0

        comment = await engine.count(CommentReaction, CommentReaction.comment == exhortation_data["id"])
        exhortation_data["comment"] = comment
        reaction = await engine.count(ExhortationReaction, ExhortationReaction.exhortation == exhortation_data["id"])
        exhortation_data["reaction"] = reaction
        return ExhortationSchema(**exhortation_data)


async def get(
    slug: Optional[str] = None,
    page: Optional[int] = 1,
    limit: Optional[int] = 20,
    user: User = Depends(get_current_user_optional_instance)

):  
    if slug:
        exhortation = await engine.find_one(Exhortation, Exhortation.slug == slug)
        if exhortation is None:
            raise ExhortationNotFoundException()
        return await exhortation_list(user=user, exhortations=[exhortation], as_list=False)
    else:
        count = await engine.count(model=Exhortation)
        skip = (page - 1) * limit
        exhortations = await engine.find(model=Exhortation, skip=skip, limit=limit)
        total_page = math.ceil(count/limit) if count >= limit else 1
        data = await exhortation_list(user=user, exhortations=exhortations)
        if len(data) == 0:
            return ExhortationListSchema(page=1, data=data, total_page=0, count=0)

        return ExhortationListSchema(page=page, data=data, total_page=total_page, count=count)


async def get_exhortation_via_username(
    username: str,
    page: Optional[int] = 1,
    limit: Optional[int] = 20,
    user: User = Depends(get_current_user_optional_instance)

):  
    current_user = await engine.find_one(User, User.username == username)
    if current_user is None:
        raise UserNotFoundException()
    
    count = await engine.count(Exhortation, Exhortation.author == current_user.id)
    skip = (page - 1) * limit
    exhortations = await engine.find(Exhortation, Exhortation.author == current_user.id, skip=skip, limit=limit)
    total_page = math.ceil(count/limit) if count >= limit else 1
    data = await exhortation_list(user=user, exhortations=exhortations)
    if len(data) == 0:
        return ExhortationListSchema(page=1, data=data, total_page=0, count=0)

    return ExhortationListSchema(page=page, data=data, total_page=total_page, count=count)


async def update(
    slug: str,
    patch: UpdateExhortationSchema,
    user: User = Depends(get_current_user_instance)
):
    result = await engine.find_one(Exhortation, Exhortation.slug == slug)
    if result is None:
        raise HTTPException(404, detail="We could not find this Exhortation")
    if result.author.id != user.id:
        raise HTTPException(401, detail="We could not find this Exhortation")
    try:
        result.model_update(patch)
        result.edited = True
        result.edited_at = datetime.utcnow()
        await engine.save(result)
        return result
    except Exception as ex:
        raise HTTPException(400, detail=str(ex))


async def delete(
    slug: str,
    user: User = Depends(get_current_user_instance)
):
    exhortation = await engine.find_one(Exhortation, Exhortation.slug == slug)
    if exhortation is None:
            raise HTTPException(404, detail="We could not find this Exhortation")
    if exhortation.author.id != user.id:
        raise HTTPException(401, detail="We could not find this Exhortation")
    await engine.delete(exhortation)
    return {"message": "Exhortation deleted"}
