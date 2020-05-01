from fastapi import HTTPException, status, Depends
from pymongo.errors import DuplicateKeyError

from src.config import database
from .auth import validate_admin_user, resolve_user
from ..models.auth import User
from ..models.core import Institution, InstitutionType, InstrumentIn, InstrumentType


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
    database.institutions.update_one(
        {'code': code},
        {'$set': institution.dict()}
    )
    return institution


def delete_institution(code: str):
    database.institutions.delete_one({'code': code})


def add_instrument(instrument: InstrumentIn, _: User = Depends(validate_admin_user)):
    try:
        if instrument.type == InstrumentType.security:
            _set_instrument_exchange(instrument)

        data = instrument.dict(exclude_none=True)
        database.instruments.insert_one(data)

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'{ve}'
        )

    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Institution with symbol {instrument.symbol} in exchange '
                   f'{instrument.exchange} already exists.'
        )

    return data


def get_instruments(_: User = Depends(resolve_user)):
    return [i for i in database.instruments.find()]


def modify_instrument(code: str, instrument: InstrumentIn, _: User = Depends(validate_admin_user)):
    try:
        if instrument.type == InstrumentType.security:
            exchange_code, symbol = code.split(':')
            _set_instrument_exchange(instrument)

        else:
            exchange_code = None
            symbol = code

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'{ve}'
        )

    data = instrument.dict(exclude_none=True)
    database.instruments.update_one(
        {'exchange.code': exchange_code, 'symbol': symbol},
        {'$set': data}
    )
    return data


def _set_instrument_exchange(instrument):
    if not instrument.exchange:
        raise ValueError('Instrument of type security must have an exchange.')

    instrument.exchange = database.institutions.find_one(
        {
            'code': instrument.exchange,
            'type': InstitutionType.exchange
        }
    )
    return instrument


def delete_instrument(code: str, _: User = Depends(validate_admin_user)):
    if ':' in code:
        exchange_code, symbol = code.split(':')
    else:
        exchange_code = None
        symbol = code

    database.instruments.delete_one({'exchange.code': exchange_code, 'symbol': symbol})
