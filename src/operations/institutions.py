from fastapi import HTTPException, status, Depends
from pymongo.errors import DuplicateKeyError

from src.config import database
from .auth import validate_admin_user, resolve_user
from ..models.auth import User
from ..models.institutions import Institution


def add_institution(institution: Institution, _: User = Depends(validate_admin_user)):
    try:
        database.institutions.insert_one(institution.dict(exclude_none=True))

    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Institution with code {institution.code} already exists.'
        )

    return institution


def get_institutions(_: User = Depends(resolve_user)):
    return [i for i in database.institutions.find()]


def modify_institution(code: str, institution: Institution, _: User = Depends(validate_admin_user)):
    database.institutions.replace_one({'code': code}, institution.dict(exclude_none=True))
    return institution


def delete_institution(code: str):
    database.institutions.delete_one({'code': code})
