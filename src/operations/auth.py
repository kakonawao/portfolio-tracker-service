from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from ..config import database
from ..models.auth import UserIn


def add_user(user: UserIn):
    try:
        database.users.insert_one(user.dict())

    except DuplicateKeyError:
        raise HTTPException(
            status_code=400,
            detail=f'User with username {user.username} already exists.'
        )

    return user
