import pytest
from unittest.mock import patch

from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from src.models.accounts import AccountType
from src.models.institutions import InstitutionType
from src.operations.accounts import add_account, get_accounts, modify_account, delete_account
from .fixtures import account_bank, account_bank_in, account_bank_input, account_cash, account_cash_in, \
    account_cash_input, normal_user, normal_user_input, bank_input, account_broker, account_broker_in, \
    account_broker_input, broker, broker_input


@patch('src.operations.accounts.database.institutions')
@patch('src.operations.accounts.database.accounts')
def test_add_account_cash_duplicate(mock_collection, mock_institutions, account_cash_in, normal_user):
    mock_collection.insert_one.side_effect = DuplicateKeyError('account already exists')

    with pytest.raises(HTTPException):
        add_account(account_cash_in, normal_user)

    assert not mock_institutions.find_one.called


@patch('src.operations.accounts.database.institutions')
@patch('src.operations.accounts.database.accounts')
def test_add_account_cash_success(mock_collection, mock_institutions, account_cash_in, normal_user, account_cash):
    res = add_account(account_cash_in, normal_user)

    assert res == account_cash.dict()
    mock_collection.insert_one.assert_called_once_with(account_cash.dict(exclude_none=True))
    assert not mock_institutions.find_one.called


@patch('src.operations.accounts.database.institutions')
@patch('src.operations.accounts.database.accounts')
def test_add_account_bank_missing_holder(mock_collection, mock_institutions, account_bank_in, normal_user):
    account_bank_in.holder = None

    with pytest.raises(HTTPException):
        add_account(account_bank_in, normal_user)

    # Holder validation failed before DB ops
    assert not mock_institutions.find_one.called
    assert not mock_collection.insert_one.called


@patch('src.operations.accounts.database.institutions')
@patch('src.operations.accounts.database.accounts')
def test_add_account_bank_holder_not_found(mock_collection, mock_institutions, account_bank_in, normal_user):
    mock_institutions.find_one.return_value = None

    with pytest.raises(HTTPException):
        add_account(account_bank_in, normal_user)

    mock_institutions.find_one.assert_called_once_with({'type': InstitutionType.bank, 'code': account_bank_in.holder})
    assert not mock_collection.insert_one.called


@patch('src.operations.accounts.database.institutions')
@patch('src.operations.accounts.database.accounts')
def test_add_account_bank_success(mock_collection, mock_institutions, account_bank_in, normal_user, account_bank,
                                  bank_input):
    mock_institutions.find_one.return_value = bank_input

    res = add_account(account_bank_in, normal_user)

    assert res == account_bank.dict()
    mock_collection.insert_one.assert_called_once_with(account_bank.dict(exclude_none=True))
    mock_institutions.find_one.assert_called_once_with({'type': InstitutionType.bank, 'code': account_bank.holder.code})

@patch('src.operations.accounts.database.institutions')
@patch('src.operations.accounts.database.accounts')
def test_add_account_broker_success(mock_collection, mock_institutions, account_broker_in, normal_user,
                                    account_broker, broker_input):
    mock_institutions.find_one.return_value = broker_input

    res = add_account(account_broker_in, normal_user)

    assert res == account_broker.dict()
    mock_collection.insert_one.assert_called_once_with(account_broker.dict(exclude_none=True))
    mock_institutions.find_one.assert_called_once_with(
        {'type': InstitutionType.broker, 'code': account_broker.holder.code}
    )


@patch('src.operations.accounts.database.accounts')
def test_get_accounts(mock_collection, normal_user, account_cash, account_bank):
    mock_collection.find.return_value.sort.return_value = [
        account_cash.dict(exclude_none=True),
        account_bank.dict(exclude_none=True)
    ]

    res = get_accounts(normal_user)

    assert len(res) == 2
    assert res[0] == account_cash.dict(exclude_none=True)
    assert res[1] == account_bank.dict(exclude_none=True)
    mock_collection.find.assert_called_once_with({'owner': normal_user.username})


@patch('src.operations.accounts.database.accounts')
def test_get_accounts_by_type(mock_collection, normal_user, account_cash):
    mock_collection.find.return_value.sort.return_value = [
        account_cash.dict(exclude_none=True),
    ]

    res = get_accounts(normal_user, AccountType.cash)

    assert len(res) == 1
    assert res[0] == account_cash.dict(exclude_none=True)
    mock_collection.find.assert_called_once_with({'owner': normal_user.username, 'type': AccountType.cash})


@patch('src.operations.accounts.database.institutions')
@patch('src.operations.accounts.database.accounts')
def test_modify_account_bank_missing_holder(mock_collection, mock_institutions, account_bank_in, normal_user):
    account_bank_in.holder = None

    with pytest.raises(HTTPException):
        modify_account(account_bank_in.code, account_bank_in, normal_user)

    # Holder validation failed before DB ops
    assert not mock_institutions.find_one.called
    assert not mock_collection.insert_one.called


@patch('src.operations.accounts.database.institutions')
@patch('src.operations.accounts.database.accounts')
def test_modify_account_bank_success(mock_collection, mock_institutions, account_bank_in, normal_user, account_bank,
                                     bank_input):
    mock_institutions.find_one.return_value = bank_input
    account_bank_in.description = 'My old account with a new name'
    account_bank.description = account_bank_in.description

    res = modify_account(account_bank_in.code, account_bank_in, normal_user)

    assert res == account_bank.dict()
    mock_collection.replace_one.assert_called_once_with(
        {'owner': normal_user.username, 'code': account_bank.code},
        account_bank.dict(exclude_none=True)
    )
    mock_institutions.find_one.assert_called_once_with({'type': InstitutionType.bank, 'code': account_bank.holder.code})


@patch('src.operations.accounts.database.institutions')
@patch('src.operations.accounts.database.accounts')
def test_modify_account_bank_not_found(mock_collection, mock_institutions, account_bank_in, normal_user,
                                       account_bank, bank_input):
    mock_institutions.find_one.return_value = bank_input
    mock_collection.replace_one.return_value.modified_count = 0
    account_bank_in.description = 'My old account with a new name'
    account_bank.description = account_bank_in.description

    with pytest.raises(HTTPException):
        modify_account(account_bank_in.code, account_bank_in, normal_user)


@patch('src.operations.accounts.database.accounts')
def test_delete_account_bank_success(mock_collection, normal_user, account_bank):
    delete_account(account_bank.code, normal_user)

    mock_collection.delete_one.assert_called_once_with({'owner': normal_user.username, 'code': account_bank.code})
