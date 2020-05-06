import pymongo
from fastapi import HTTPException, status, Depends
from pymongo.errors import DuplicateKeyError

from src.config import database
from .auth import validate_admin_user, resolve_user
from ..models.auth import User
from ..models.institutions import InstitutionType
from ..models.instruments import InstrumentIn, InstrumentType


def _get_exchange_data(code: str = None):
    if not code:
        raise ValueError('Instrument of type security must have an exchange.')

    data = database.institutions.find_one({'code': code, 'type': InstitutionType.exchange})
    if not data:
        raise ValueError(f'Exchange with code {code} not found.')

    return data


def add_instrument(instrument: InstrumentIn, _: User = Depends(validate_admin_user)):
    try:
        data = instrument.dict(exclude_none=True)

        if instrument.type == InstrumentType.security:
            data['exchange'] = _get_exchange_data(getattr(instrument, 'exchange'))
            data['code'] = f'{data["exchange"]["code"]}:{instrument.symbol}'
        else:
            data['code'] = instrument.symbol
            data.pop('exchange', None)

        database.instruments.insert_one(data)

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'{ve}'
        )

    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Instrument with code {data["code"]} already exists.'
        )

    return data


def get_instruments(_: User = Depends(resolve_user), t: InstrumentType = None):
    filters = {}
    if t:
        filters['type'] = t

    return [i for i in database.instruments.find(filters).sort(
        [
            ('type', pymongo.ASCENDING),
            ('code', pymongo.ASCENDING)
        ]
    )]


def modify_instrument(code: str, instrument: InstrumentIn, _: User = Depends(validate_admin_user)):
    try:
        data = instrument.dict(exclude_none=True)
        if instrument.type == InstrumentType.security:
            data['exchange'] = _get_exchange_data(getattr(instrument, 'exchange'))
            data['code'] = f'{data["exchange"]["code"]}:{instrument.symbol}'
        else:
            data['code'] = instrument.symbol
            data.pop('exchange', None)

        res = database.instruments.replace_one({'code': code}, data)
        if not res.modified_count:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Instrument with code {data["code"]} does not exist.'
            )

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'{ve}'
        )

    return data


def delete_instrument(code: str, _: User = Depends(validate_admin_user)):
    database.instruments.delete_one({'code': code})
