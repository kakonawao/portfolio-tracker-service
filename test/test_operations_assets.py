import pytest
from unittest.mock import patch

from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from src.models.core import InstitutionType
from src.operations.assets import add_account, get_accounts, modify_account, delete_account
from .fixtures import account_bank, account_bank_in, account_bank_input, account_cash, account_cash_in, \
    account_cash_input, normal_user_in, normal_user_input, bank_input, account_broker, account_broker_in, \
    account_broker_input, broker, broker_input


@patch('src.operations.assets.database.institutions')
@patch('src.operations.assets.database.accounts')
def test_add_account_cash_duplicate(mock_collection, mock_institutions, account_cash_in, normal_user_in):
    mock_collection.insert_one.side_effect = DuplicateKeyError('account already exists')

    with pytest.raises(HTTPException):
        add_account(account_cash_in, normal_user_in)

    assert not mock_institutions.find_one.called


@patch('src.operations.assets.database.institutions')
@patch('src.operations.assets.database.accounts')
def test_add_account_cash_success(mock_collection, mock_institutions, account_cash_in, normal_user_in, account_cash):
    res = add_account(account_cash_in, normal_user_in)

    assert res == account_cash.dict(exclude_none=True)
    mock_collection.insert_one.assert_called_once_with(account_cash.dict(exclude_none=True))
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

    mock_institutions.find_one.assert_called_once_with({'type': InstitutionType.bank, 'code': account_bank_in.holder})
    assert not mock_collection.insert_one.called


@patch('src.operations.assets.database.institutions')
@patch('src.operations.assets.database.accounts')
def test_add_account_bank_success(mock_collection, mock_institutions, account_bank_in, normal_user_in, account_bank,
                                  bank_input):
    mock_institutions.find_one.return_value = bank_input

    res = add_account(account_bank_in, normal_user_in)

    assert res == account_bank.dict()
    mock_collection.insert_one.assert_called_once_with(account_bank.dict(exclude_none=True))
    mock_institutions.find_one.assert_called_once_with({'type': InstitutionType.bank, 'code': account_bank.holder.code})

@patch('src.operations.assets.database.institutions')
@patch('src.operations.assets.database.accounts')
def test_add_account_broker_success(mock_collection, mock_institutions, account_broker_in, normal_user_in,
                                    account_broker, broker_input):
    mock_institutions.find_one.return_value = broker_input

    res = add_account(account_broker_in, normal_user_in)

    assert res == account_broker.dict()
    mock_collection.insert_one.assert_called_once_with(account_broker.dict(exclude_none=True))
    mock_institutions.find_one.assert_called_once_with(
        {'type': InstitutionType.broker, 'code': account_broker.holder.code}
    )


@patch('src.operations.assets.database.accounts')
def test_get_accounts(mock_collection, normal_user_in, account_cash, account_bank):
    mock_collection.find.return_value = [
        account_cash.dict(exclude_none=True),
        account_bank.dict(exclude_none=True)
    ]

    res = get_accounts(normal_user_in)

    assert len(res) == 2
    assert res[0] == account_cash.dict(exclude_none=True)
    assert res[1] == account_bank.dict(exclude_none=True)


@patch('src.operations.assets.database.institutions')
@patch('src.operations.assets.database.accounts')
def test_modify_account_bank_missing_holder(mock_collection, mock_institutions, account_bank_in, normal_user_in):
    account_bank_in.holder = None

    with pytest.raises(HTTPException):
        modify_account(account_bank_in.code, account_bank_in, normal_user_in)

    # Holder validation failed before DB ops
    assert not mock_institutions.find_one.called
    assert not mock_collection.insert_one.called


@patch('src.operations.assets.database.institutions')
@patch('src.operations.assets.database.accounts')
def test_modify_account_bank_success(mock_collection, mock_institutions, account_bank_in, normal_user_in, account_bank,
                                     bank_input):
    mock_institutions.find_one.return_value = bank_input
    account_bank_in.description = 'My old account with a new name'
    account_bank.description = account_bank_in.description

    res = modify_account(account_bank_in.code, account_bank_in, normal_user_in)

    assert res == account_bank.dict()
    mock_collection.update_one.assert_called_once_with(
        {'owner': normal_user_in.username, 'code': account_bank.code},
        {'$set': account_bank.dict(exclude_none=True)}
    )
    mock_institutions.find_one.assert_called_once_with({'type': InstitutionType.bank, 'code': account_bank.holder.code})


@patch('src.operations.assets.database.accounts')
def test_delete_account_bank_success(mock_collection, normal_user_in, account_bank):
    delete_account(account_bank.code, normal_user_in)

    mock_collection.delete_one.assert_called_once_with({'owner': normal_user_in.username, 'code': account_bank.code})
