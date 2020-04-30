import pytest
from unittest.mock import patch

from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from src.operations.assets import add_account
from .fixtures import account_bank, account_bank_data, account_bank_in, account_bank_input, \
    account_cash, account_cash_data, account_cash_in, account_cash_input, normal_user_in, normal_user_input, \
    bank_input


@patch('src.operations.assets.database.institutions')
@patch('src.operations.assets.database.accounts')
def test_add_account_cash_duplicate(mock_collection, mock_institutions, account_cash_in, normal_user_in):
    mock_collection.insert_one.side_effect = DuplicateKeyError('account already exists')

    with pytest.raises(HTTPException):
        add_account(account_cash_in, normal_user_in)

    assert not mock_institutions.find_one.called


@patch('src.operations.assets.database.institutions')
@patch('src.operations.assets.database.accounts')
def test_add_account_cash_success(mock_collection, mock_institutions, account_cash_in, normal_user_in, account_cash, account_cash_data):
    res = add_account(account_cash_in, normal_user_in)

    assert res == account_cash
    mock_collection.insert_one.assert_called_once_with(account_cash_data)
    assert not mock_institutions.find_one.called


@patch('src.operations.assets.database.institutions')
@patch('src.operations.assets.database.accounts')
def test_add_account_bank_missing_holder(mock_collection, mock_institutions, account_bank_in, normal_user_in):
    account_bank_in.holder = None

    with pytest.raises(HTTPException):
        add_account(account_bank_in, normal_user_in)

    # Holder validation failed before DB ops
    assert not mock_institutions.find_one.called
    assert not mock_collection.insert_one.called


@patch('src.operations.assets.database.institutions')
@patch('src.operations.assets.database.accounts')
def test_add_account_bank_holder_not_found(mock_collection, mock_institutions, account_bank_in, normal_user_in):
    mock_institutions.find_one.return_value = None

    with pytest.raises(HTTPException):
        add_account(account_bank_in, normal_user_in)

    mock_institutions.find_one.assert_called_once_with({'code': account_bank_in.holder})
    assert not mock_collection.insert_one.called


@patch('src.operations.assets.database.institutions')
@patch('src.operations.assets.database.accounts')
def test_add_account_bank_success(mock_collection, mock_institutions, account_bank_in, normal_user_in, account_bank, account_bank_data, bank_input):
    mock_institutions.find_one.return_value = bank_input

    res = add_account(account_bank_in, normal_user_in)

    assert res == account_bank.dict()
    mock_collection.insert_one.assert_called_once_with(account_bank_data)
    mock_institutions.find_one.assert_called_once_with({'code': account_bank.holder.code})
