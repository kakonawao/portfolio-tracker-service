from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from src.operations.transactions import add_transaction
from .fixtures import transaction_in, transaction_input, normal_user_in, normal_user_input, account_cash, \
    account_cash_input, currency, currency_input, transaction, account_broker_input


@patch('src.operations.transactions.database.instruments')
@patch('src.operations.transactions.database.accounts')
@patch('src.operations.transactions.database.transactions')
def test_add_transaction_account_not_found(mock_collection, mock_accounts, mock_instruments, transaction_in,
                                           normal_user_in, currency):
    mock_accounts.find_one.return_value = None
    mock_instruments.find_one.return_value = currency.dict(exclude_none=True)

    with pytest.raises(HTTPException):
        add_transaction(transaction_in, normal_user_in)

    assert not mock_collection.insert_one.called


@patch('src.operations.transactions.database.instruments')
@patch('src.operations.transactions.database.accounts')
@patch('src.operations.transactions.database.transactions')
def test_add_transaction_instrument_not_found(mock_collection, mock_accounts, mock_instruments, transaction_in,
                                              normal_user_in, account_cash):
    mock_accounts.find_one.return_value = account_cash.dict(exclude_none=True)
    mock_instruments.find_one.return_value = None

    with pytest.raises(HTTPException):
        add_transaction(transaction_in, normal_user_in)

    assert not mock_collection.insert_one.called


@patch('src.operations.transactions.datetime')
@patch('src.operations.transactions.database.instruments')
@patch('src.operations.transactions.database.accounts')
@patch('src.operations.transactions.database.transactions')
def test_add_transaction_success(mock_collection, mock_accounts, mock_instruments, mock_dt, transaction_in, normal_user_in,
                                 account_cash, currency, transaction):
    mock_dt.utcnow.return_value = datetime(2020, 4, 20, 4, 20)
    mock_accounts.find_one.return_value = account_cash.dict(exclude_none=True)
    mock_instruments.find_one.return_value = currency.dict(exclude_none=True)

    res = add_transaction(transaction_in, normal_user_in)

    stored_transaction_data = transaction.dict(exclude_none=True)
    stored_transaction_data['code'] = '2020-04-20T04:20:00'
    assert res == stored_transaction_data
    mock_collection.insert_one.assert_called_once_with(stored_transaction_data)
