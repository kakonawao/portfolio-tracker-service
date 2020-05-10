from datetime import datetime

import pymongo
from fastapi import HTTPException, status, Depends
from pymongo.errors import DuplicateKeyError

from src.config import database
from .auth import validate_admin_user, resolve_user
from ..models.auth import User
from ..models.institutions import InstitutionType
from ..models.instruments import InstrumentIn, InstrumentType, ValueIn


def _get_exchange_data(code: str = None):
    if not code:
        raise ValueError('Instrument of type security must have an exchange')

    data = database.institutions.find_one({'code': code, 'type': InstitutionType.exchange})
    if not data:
        raise ValueError(f'Exchange with code {code} not found')

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
            detail=f'{ve}.'
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
            detail=f'{ve}.'
        )

    return data


def delete_instrument(code: str, _: User = Depends(validate_admin_user)):
    database.instruments.delete_one({'code': code})


def _get_date_from_code(date_code):
    try:
        return datetime(*(int(p) for p in date_code.split('-')))

    except Exception:
        raise ValueError(f'Incorrect date format {date_code}')



def set_value(code: str, date_code: str, value: ValueIn, _: User = Depends(validate_admin_user)):
    try:
        date = _get_date_from_code(date_code)
        instrument_data = database.instruments.find_one({'code': code})
        if not instrument_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Instrument with code {code} does not exist.'
            )

        set_data = {
            'instrument': instrument_data,
            'date': date,
        }
        return_data = {**set_data, 'values': {}}

        for currency_code, quantity in value.values.items():
            set_data[f'values.{currency_code}'] = quantity
            return_data['values'][currency_code] = quantity

        database.values.update_one(
            {'instrument.code': code, 'date': date},
            {'$set': set_data},
            upsert=True
        )

    except ValueError as ve:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f'{ve}.'
        )

    return return_data


def get_value(code: str, date_code: str,  _: User = Depends(resolve_user)):
    try:
        date = _get_date_from_code(date_code)
        filters = {
            'instrument.code': code,
            'date': date
        }
        data = database.values.find_one(
            filters
        )
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Instrument {code} value for date {date_code} not found.'
            )

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'{ve}.'
        )

    return data
