import pytest
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from unittest.mock import patch

from src.models.core import Instrument
from src.operations.core import add_institution, get_institutions, modify_institution, delete_institution, \
    add_instrument, get_instruments
from .fixtures import admin_user_in, admin_user_input, bank, bank_input, currency, currency_input, \
    exchange, exchange_input, security, security_data, security_in, security_input


@patch('src.operations.core.database.institutions')
def test_add_institution_failure(collection_mock, bank):
    collection_mock.insert_one.side_effect = DuplicateKeyError('Bank already exists')
    with pytest.raises(HTTPException):
        add_institution(bank)


@patch('src.operations.core.database.institutions')
def test_add_institution_success(collection_mock, bank, bank_input):
    res = add_institution(bank)

    assert res == bank
    collection_mock.insert_one.assert_called_once_with(bank_input)


@patch('src.operations.core.database.institutions')
def test_get_institutions(collection_mock, bank_input, bank):
    collection_mock.find.return_value = [
        bank_input,
    ]

    res = get_institutions()

    assert len(res) == 1
    assert res[0] == bank


@patch('src.operations.core.database.institutions')
def test_modify_institution(collection_mock, bank_input, bank):
    bank_input['name'] = 'Boys Over Internet'
    bank.name = bank_input['name']
    res = modify_institution(bank.code, bank)

    assert res == bank
    collection_mock.update_one.assert_called_once_with({'code': bank.code}, {'$set': bank_input})


@patch('src.operations.core.database.institutions')
def test_delete_institution(collection_mock, bank):
    delete_institution(bank.code)

    collection_mock.delete_one.assert_called_once_with({'code': bank.code})


@patch('src.operations.core.database.institutions')
@patch('src.operations.core.database.instruments')
def test_add_currency_failed(collection_mock, institutions_mock, currency):
    collection_mock.insert_one.side_effect = DuplicateKeyError('currency already exists')
    with pytest.raises(HTTPException):
        add_instrument(currency)

    assert not institutions_mock.find_one.called


@patch('src.operations.core.database.institutions')
@patch('src.operations.core.database.instruments')
def test_add_currency_success(collection_mock, institutions_mock, currency, currency_input):
    res = add_instrument(currency)

    assert not institutions_mock.find_one.called
    currency_input['exchange'] = None
    collection_mock.insert_one.assert_called_once_with(currency_input)
    assert res == currency


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
def test_add_security_success(collection_mock, institutions_mock, exchange, security, security_data, security_in):
    institutions_mock.find_one.return_value = security_data['exchange']

    res = add_instrument(security_in)

    assert res == security
    institutions_mock.find_one.assert_called_once_with({'code': exchange.code, 'type': exchange.type})
    collection_mock.insert_one.assert_called_once_with(security_data)
    assert res.exchange == exchange


@patch('src.operations.core.database.instruments')
def test_get_instruments(collection_mock, currency_input, security_data, currency, security):
    collection_mock.find.return_value = [
        currency_input,
        security_data,
    ]

    res = get_instruments()

    assert len(res) == 2
    assert Instrument(**res[0]) == currency
    assert Instrument(**res[1]) == security
