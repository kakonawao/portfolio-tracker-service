import pytest
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from unittest.mock import patch

from src.operations.core import add_institution, get_institutions, modify_institution, delete_institution, \
    add_instrument, get_instruments, modify_instrument, delete_instrument
from .fixtures import bank, bank_input, currency, currency_in, currency_input, \
    exchange, exchange_input, security, security_in, security_input


@patch('src.operations.core.database.institutions')
def test_add_institution_failure(collection_mock, bank):
    collection_mock.insert_one.side_effect = DuplicateKeyError('Bank already exists')
    with pytest.raises(HTTPException):
        add_institution(bank)


@patch('src.operations.core.database.institutions')
def test_add_institution_success(collection_mock, bank):
    res = add_institution(bank)

    assert res == bank
    collection_mock.insert_one.assert_called_once_with(bank.dict(exclude_none=True))


@patch('src.operations.core.database.institutions')
def test_get_institutions(collection_mock, bank):
    collection_mock.find.return_value = [
        bank.dict(exclude_none=True),
    ]

    res = get_institutions()

    assert len(res) == 1
    assert res[0] == bank


@patch('src.operations.core.database.institutions')
def test_modify_institution(collection_mock, bank):
    bank.name = 'Boys Over Internet'
    res = modify_institution(bank.code, bank)

    assert res == bank
    collection_mock.update_one.assert_called_once_with({'code': bank.code}, {'$set': bank.dict(exclude_none=True)})


@patch('src.operations.core.database.institutions')
def test_delete_institution(collection_mock, bank):
    delete_institution(bank.code)

    collection_mock.delete_one.assert_called_once_with({'code': bank.code})


@patch('src.operations.core.database.institutions')
@patch('src.operations.core.database.instruments')
def test_add_currency_failure(collection_mock, institutions_mock, currency_in):
    collection_mock.insert_one.side_effect = DuplicateKeyError('currency already exists')
    with pytest.raises(HTTPException):
        add_instrument(currency_in)

    assert not institutions_mock.find_one.called


@patch('src.operations.core.database.institutions')
@patch('src.operations.core.database.instruments')
def test_add_currency_success(collection_mock, institutions_mock, currency_in, currency):
    res = add_instrument(currency_in)

    assert not institutions_mock.find_one.called
    collection_mock.insert_one.assert_called_once_with(currency.dict(exclude_unset=True))
    assert res == currency.dict(exclude_none=True)


@patch('src.operations.core.database.institutions')
@patch('src.operations.core.database.instruments')
def test_add_security_failure(collection_mock, institutions_mock, security_in):
    security_in.exchange = None

    with pytest.raises(HTTPException):
        add_instrument(security_in)

    # No DB ops done due to validation error
    assert not collection_mock.insert_one.called
    assert not institutions_mock.find_one.called


@patch('src.operations.core.database.institutions')
@patch('src.operations.core.database.instruments')
def test_add_security_success(collection_mock, institutions_mock, exchange, security, security_in):
    institutions_mock.find_one.return_value = exchange.dict(exclude_none=True)

    res = add_instrument(security_in)

    assert res == security.dict(exclude_none=True)
    institutions_mock.find_one.assert_called_once_with({'code': exchange.code, 'type': exchange.type})
    collection_mock.insert_one.assert_called_once_with(security.dict(exclude_none=True))


@patch('src.operations.core.database.instruments')
def test_get_instruments(collection_mock, currency, security):
    collection_mock.find.return_value = [
        currency.dict(exclude_none=True),
        security.dict(exclude_none=True),
    ]

    res = get_instruments()

    assert len(res) == 2
    assert res[0] == currency.dict(exclude_none=True)
    assert res[1] == security.dict(exclude_none=True)

@patch('src.operations.core.database.institutions')
@patch('src.operations.core.database.instruments')
def test_modify_currency_success(collection_mock, institutions_mock, currency_in, currency):
    currency_in.description = 'EuroMoneda'
    currency.description = currency_in.description
    res = modify_instrument(currency_in.code, currency_in)

    assert res == currency
    assert not institutions_mock.find_one.called
    collection_mock.update_one.assert_called_once_with(
        {'exchange.code': None, 'symbol': currency.symbol},
        {'$set': currency.dict(exclude_none=True)}
    )


@patch('src.operations.core.database.institutions')
@patch('src.operations.core.database.instruments')
def test_modify_security_success(collection_mock, institutions_mock, security_in, security):
    institutions_mock.find_one.return_value = security.exchange.dict(exclude_none=True)
    security_in.description = 'Amazon Inc'
    security.description = security_in.description
    res = modify_instrument(security_in.code, security_in)

    assert res == security
    institutions_mock.find_one.assert_called_once_with(
        {'code': security.exchange.code, 'type': security.exchange.type}
    )
    collection_mock.update_one.assert_called_once_with(
        {'exchange.code': security.exchange.code, 'symbol': security.symbol},
        {'$set': security.dict(exclude_none=True)}
    )


@patch('src.operations.core.database.instruments')
def test_delete_currency_success(collection_mock, currency):
    delete_instrument(currency.code)

    collection_mock.delete_one.assert_called_once_with(
        {'exchange.code': None, 'symbol': currency.symbol}
    )


@patch('src.operations.core.database.instruments')
def test_delete_security_success(collection_mock, security):
    delete_instrument(security.code)

    collection_mock.delete_one.assert_called_once_with(
        {'exchange.code': security.exchange.code, 'symbol': security.symbol}
    )
