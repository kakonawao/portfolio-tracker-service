import pymongo
from fastapi import Depends
from pymongo.errors import DuplicateKeyError

from ..config import database
from ..exceptions import handled, ValidationError, NotFoundError
from ..models.auth import User
from ..models.institutions import Institution, InstitutionType
from .auth import validate_admin_user, resolve_user


@handled
def add_institution(institution: Institution, _: User = Depends(validate_admin_user)):
    try:
        database.institutions.insert_one(institution.dict(exclude_none=True))

    except DuplicateKeyError:
        raise ValidationError(f'Institution with code {institution.code} already exists.')

    return institution


@handled
def get_institutions(_: User = Depends(resolve_user), t: InstitutionType = None):
    filters = {}
    if t:
        filters['type'] = t

    return [i for i in database.institutions.find(filters).sort(
        [
            ('type', pymongo.ASCENDING),
            ('code', pymongo.ASCENDING)
        ]
    )]


@handled
def modify_institution(code: str, institution: Institution, _: User = Depends(validate_admin_user)):
    res = database.institutions.replace_one({'code': code}, institution.dict(exclude_none=True))
    if not res.modified_count:
        raise NotFoundError(f'Institution with code {code} does not exist.')
    return institution


@handled
def delete_institution(code: str):
    database.institutions.delete_one({'code': code})
