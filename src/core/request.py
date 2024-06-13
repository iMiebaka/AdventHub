from settings import Engine, ENV
from src.models.user import User, FollowerFollowing
from src.schema.request import FollowerFollowingSchema, FollowerFollowingListSchema, FollowUserSchema
from src.utils.exceptions import *
import logging, math
from typing import List
from src.models.exhortation import Exhortation

LOGGER = logging.getLogger(__name__)
engine = Engine


async def followers_list(users: List[FollowerFollowing]) -> Exhortation:
    payload = []
    for user in users:
        user_data = user.model_dump()

        payload.append(FollowerFollowingSchema(**user_data))
    return payload
   


async def follow_user(payload: FollowUserSchema, current_user:User):
    username = payload.username
    user = await engine.find_one(User, User.username == username)
    if user is None:
        raise UserNotFoundException()
    
    query = (FollowerFollowing.friend == user.id) & (FollowerFollowing.user == current_user.id)
    is_following = await engine.find_one(FollowerFollowing, query)
    if user.id == current_user.id:
        return {"message": "User already following"}
    elif is_following is None:
        follower_init = FollowerFollowing(user=current_user, friend=user)
        await engine.save(follower_init)
        return {"message": "User Followed"}
    else:
        await engine.delete(is_following)
        return {"message": "User Unfollowed"}



async def followers(
    current_user:User,
    page: int,
    limit: int,
):
    count = await engine.count(FollowerFollowing, FollowerFollowing.user == current_user.id)
    skip = (page - 1) * limit
    total_page = math.ceil(count/limit) if count >= limit else 1
    followers = await engine.find(FollowerFollowing, FollowerFollowing.user == current_user.id, skip=skip, limit=limit)
    data = await followers_list(users=followers)    
    if len(data) == 0:
        return FollowerFollowingListSchema(page=1, data=data, total_page=0, count=0)

    return FollowerFollowingListSchema(page=page, data=data, total_page=total_page, count=count)



async def following(
    current_user:User,
    page: int,
    limit: int,
):
    count = await engine.count(FollowerFollowing, FollowerFollowing.friend == current_user.id)
    skip = (page - 1) * limit
    total_page = math.ceil(count/limit) if count >= limit else 1
    followers = await engine.find(FollowerFollowing, FollowerFollowing.friend == current_user.id, skip=skip, limit=limit)
    data = await followers_list(users=followers)    
    if len(data) == 0:
        return FollowerFollowingListSchema(page=1, data=data, total_page=0, count=0)

    return FollowerFollowingListSchema(page=page, data=data, total_page=total_page, count=count)
