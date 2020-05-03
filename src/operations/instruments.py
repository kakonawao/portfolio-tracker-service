from fastapi import HTTPException, status, Depends
from pymongo.errors import DuplicateKeyError

from src.config import database
from .auth import validate_admin_user, resolve_user
from ..dal import get_instrument_filter
from ..models.auth import User
from ..models.institutions import InstitutionType
from ..models.instruments import InstrumentIn, InstrumentType


def add_instrument(instrument: InstrumentIn, _: User = Depends(validate_admin_user)):
    try:
        if instrument.type == InstrumentType.security:
            _set_security_exchange(instrument)

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
            _set_security_exchange(instrument)

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'{ve}'
        )

    data = instrument.dict(exclude_none=True)
    database.instruments.replace_one(get_instrument_filter(code), data)
    return data


def _set_security_exchange(instrument):
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
    database.instruments.delete_one(get_instrument_filter(code))
