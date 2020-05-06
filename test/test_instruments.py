import pytest
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from unittest.mock import patch

from src.models.institutions import InstitutionType
from src.models.instruments import InstrumentType
from src.operations.instruments import add_instrument, get_instruments, modify_instrument, delete_instrument
from .fixtures import bank, bank_input, currency, currency_in, currency_input, exchange, exchange_input, security, \
    security_in, security_input, normal_user, normal_user_input


@patch('src.operations.instruments.database.institutions')
@patch('src.operations.instruments.database.instruments')
def test_add_currency_failure(collection_mock, institutions_mock, currency_in):
    collection_mock.insert_one.side_effect = DuplicateKeyError('currency already exists')
    with pytest.raises(HTTPException):
        add_instrument(currency_in)

    assert not institutions_mock.find_one.called


@patch('src.operations.instruments.database.institutions')
@patch('src.operations.instruments.database.instruments')
def test_add_currency_success(collection_mock, institutions_mock, currency_in, currency):
    res = add_instrument(currency_in)

    assert not institutions_mock.find_one.called
    collection_mock.insert_one.assert_called_once_with(currency.dict(exclude_unset=True))
    assert res == currency.dict(exclude_none=True)


@patch('src.operations.instruments.database.institutions')
@patch('src.operations.instruments.database.instruments')
def test_add_security_exchange_missing(collection_mock, institutions_mock, security_in):
    security_in.exchange = None

    with pytest.raises(HTTPException):
        add_instrument(security_in)

    assert not collection_mock.insert_one.called
    assert not institutions_mock.find_one.called


@patch('src.operations.instruments.database.institutions')
@patch('src.operations.instruments.database.instruments')
def test_add_security_exchange_not_found(collection_mock, institutions_mock, security_in):
    institutions_mock.find_one.return_value = None

    with pytest.raises(HTTPException):
        add_instrument(security_in)

    institutions_mock.find_one.assert_called_once_with({'code': security_in.exchange, 'type': InstitutionType.exchange})
    assert not collection_mock.insert_one.called


@patch('src.operations.instruments.database.institutions')
@patch('src.operations.instruments.database.instruments')
def test_add_security_success(collection_mock, institutions_mock, exchange, security, security_in):
    institutions_mock.find_one.return_value = exchange.dict(exclude_none=True)

    res = add_instrument(security_in)

    assert res == security.dict(exclude_none=True)
    institutions_mock.find_one.assert_called_once_with({'code': exchange.code, 'type': exchange.type})
    collection_mock.insert_one.assert_called_once_with(security.dict(exclude_none=True))


@patch('src.operations.instruments.database.instruments')
def test_get_instruments(collection_mock, currency, security):
    collection_mock.find.return_value.sort.return_value = [
        currency.dict(exclude_none=True),
        security.dict(exclude_none=True),
    ]

    res = get_instruments()

    assert len(res) == 2
    assert res[0] == currency.dict(exclude_none=True)
    assert res[1] == security.dict(exclude_none=True)
    collection_mock.find.assert_called_once_with({})


@patch('src.operations.instruments.database.instruments')
def test_get_instruments_by_type(collection_mock, currency, security, normal_user):
    collection_mock.find.return_value.sort.return_value = [
        currency.dict(exclude_none=True),
    ]

    res = get_instruments(normal_user, InstrumentType.currency)

    assert len(res) == 1
    assert res[0] == currency.dict(exclude_none=True)
    collection_mock.find.assert_called_once_with({'type': InstrumentType.currency})


@patch('src.operations.instruments.database.institutions')
@patch('src.operations.instruments.database.instruments')
def test_modify_currency_success(collection_mock, institutions_mock, currency_in, currency):
    currency_in.description = 'EuroMoneda'
    currency.description = currency_in.description
    res = modify_instrument(currency_in.symbol, currency_in)

    assert res == currency
    assert not institutions_mock.find_one.called
    collection_mock.replace_one.assert_called_once_with(
        {'code': currency.symbol},
        currency.dict(exclude_none=True)
    )


@patch('src.operations.instruments.database.instruments')
def test_modify_currency_not_found(collection_mock, currency_in, currency):
    currency_in.description = 'EuroMoneda'
    currency.description = currency_in.description
    collection_mock.replace_one.return_value.modified_count = 0

    with pytest.raises(HTTPException):
        modify_instrument(currency_in.symbol, currency_in)


@patch('src.operations.instruments.database.institutions')
@patch('src.operations.instruments.database.instruments')
def test_modify_security_failure(collection_mock, institutions_mock, security_in):
    security_in.exchange = None

    with pytest.raises(HTTPException):
        modify_instrument(f'{security_in.exchange}:{security_in.symbol}', security_in)

    # No DB ops done due to validation error
    assert not collection_mock.insert_one.called
    assert not institutions_mock.find_one.called


@patch('src.operations.instruments.database.institutions')
@patch('src.operations.instruments.database.instruments')
def test_modify_security_success(collection_mock, institutions_mock, security_in, security):
    institutions_mock.find_one.return_value = security.exchange.dict(exclude_none=True)
    security_in.description = 'Amazon Inc'
    security.description = security_in.description
    res = modify_instrument(f'{security_in.exchange}:{security_in.symbol}', security_in)

    assert res == security
    institutions_mock.find_one.assert_called_once_with(
        {'code': security.exchange.code, 'type': security.exchange.type}
    )
    collection_mock.replace_one.assert_called_once_with(
        {'code': security.code},
        security.dict(exclude_none=True)
    )


@patch('src.operations.instruments.database.instruments')
def test_delete_currency_success(collection_mock, currency):
    delete_instrument(currency.code)

    collection_mock.delete_one.assert_called_once_with(
        {'code': currency.code}
    )


@patch('src.operations.instruments.database.instruments')
def test_delete_security_success(collection_mock, security):
    delete_instrument(security.code)

    collection_mock.delete_one.assert_called_once_with(
        {'code': security.code}
    )
