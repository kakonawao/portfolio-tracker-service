from fastapi import HTTPException, status, Depends
from pymongo.errors import DuplicateKeyError

from src.config import database
from .auth import validate_admin_user, resolve_user
from ..models.auth import User
from ..models.core import Institution, InstitutionType, InstrumentIn, InstrumentType


def add_institution(institution: Institution, _: User = Depends(validate_admin_user)):
    try:
        database.institutions.insert_one(institution.dict())

    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Institution with code {institution.code} already exists.'
        )

    return institution


def get_institutions(_: User = Depends(resolve_user)):
    return [i for i in database.institutions.find()]


def add_instrument(instrument: InstrumentIn, _: User = Depends(validate_admin_user)):
    try:
        if instrument.type == InstrumentType.security:
            if not instrument.exchange:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Instrument of type security must have an exchange.'
                )

            instrument.exchange = database.institutions.find_one(
                {
                    'code': instrument.exchange,
                    'type': InstitutionType.exchange
                }
            )

        database.instruments.insert_one(instrument.dict())

    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Institution with symbol {instrument.symbol} in exchange '
                   f'{instrument.exchange} already exists.'
        )

    return instrument


def get_instruments(_: User = Depends(resolve_user)):
    return [i for i in database.instruments.find()]

