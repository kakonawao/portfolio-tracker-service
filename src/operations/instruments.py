from datetime import datetime

import pymongo
from fastapi import Depends
from pymongo.errors import DuplicateKeyError

from ..config import database
from ..exceptions import handled, ValidationError, NotFoundError
from ..models.auth import User
from ..models.institutions import InstitutionType
from ..models.instruments import InstrumentIn, InstrumentType, ValueIn
from .auth import validate_admin_user, resolve_user


def _get_date_from_code(date_code):
    try:
        return datetime(*(int(p) for p in date_code.split('-')))

    except Exception:
        raise ValidationError(f'Incorrect date format {date_code}')


def _get_exchange_data(code: str = None):
    if not code:
        raise ValidationError('Instrument of type security must have an exchange')

    data = database.institutions.find_one({'code': code, 'type': InstitutionType.exchange})
    if not data:
        raise ValidationError(f'Exchange with code {code} not found')

    return data


@handled
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

    except DuplicateKeyError:
        raise ValidationError(f'Instrument with code {data["code"]} already exists.')

    return data


@handled
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


@handled
def modify_instrument(code: str, instrument: InstrumentIn, _: User = Depends(validate_admin_user)):
    data = instrument.dict(exclude_none=True)
    if instrument.type == InstrumentType.security:
        data['exchange'] = _get_exchange_data(getattr(instrument, 'exchange'))
        data['code'] = f'{data["exchange"]["code"]}:{instrument.symbol}'
    else:
        data['code'] = instrument.symbol
        data.pop('exchange', None)

    res = database.instruments.replace_one({'code': code}, data)
    if not res.modified_count:
        raise NotFoundError(f'Instrument with code {data["code"]} does not exist.')

    return data


@handled
def delete_instrument(code: str, _: User = Depends(validate_admin_user)):
    database.instruments.delete_one({'code': code})



@handled
def set_value(code: str, date_code: str, value: ValueIn, _: User = Depends(validate_admin_user)):
    date = _get_date_from_code(date_code)
    instrument_data = database.instruments.find_one({'code': code})
    if not instrument_data:
        raise NotFoundError(f'Instrument with code {code} does not exist.')

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

    return return_data


@handled
def get_value(code: str, date_code: str,  _: User = Depends(resolve_user)):
    date = _get_date_from_code(date_code)
    filters = {
        'instrument.code': code,
        'date': date
    }
    data = database.values.find_one(
        filters
    )
    if not data:
        raise NotFoundError(f'Instrument {code} value for date {date_code} not found.')

    return data
