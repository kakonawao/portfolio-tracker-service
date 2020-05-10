from datetime import datetime
from unittest.mock import patch, call

import pytest
from fastapi import HTTPException

from src.models.transactions import TransactionStatus
from src.operations.transactions import add_transaction, complete_transaction, cancel_transaction, get_transactions
from .fixtures import atm_extraction_in, atm_extraction_input, normal_user, normal_user_input, account_bank, \
    account_bank_input, bank_input, broker_input, account_cash, account_cash_input, account_broker, \
    account_broker_input, currency, currency_input, atm_extraction, account_broker_input


@patch('src.operations.transactions.database.instruments')
@patch('src.operations.transactions.database.accounts')
@patch('src.operations.transactions.database.transactions')
def test_add_transaction_account_not_found(mock_collection, mock_accounts, mock_instruments, atm_extraction_in,
                                           normal_user, currency):
    mock_accounts.find_one.return_value = None
    mock_instruments.find_one.return_value = currency.dict(exclude_none=True)

    with pytest.raises(HTTPException):
        add_transaction(atm_extraction_in, normal_user)

    assert not mock_collection.insert_one.called


@patch('src.operations.transactions.database.instruments')
@patch('src.operations.transactions.database.accounts')
@patch('src.operations.transactions.database.transactions')
def test_add_transaction_instrument_not_found(mock_collection, mock_accounts, mock_instruments, atm_extraction_in,
                                              normal_user, account_bank, account_cash):
    mock_accounts.find_one.side_effect = [account_bank.dict(exclude_none=True), account_cash.dict(exclude_none=True)]
    mock_instruments.find_one.return_value = None

    with pytest.raises(HTTPException):
        add_transaction(atm_extraction_in, normal_user)

    assert not mock_collection.insert_one.called


@patch('src.operations.transactions.datetime')
@patch('src.operations.transactions.database.instruments')
@patch('src.operations.transactions.database.accounts')
@patch('src.operations.transactions.database.transactions')
def test_add_transaction_success(mock_collection, mock_accounts, mock_instruments, mock_dt, atm_extraction_in,
                                 normal_user, account_bank, account_cash, account_broker, currency, atm_extraction):
    mock_dt.utcnow.return_value = datetime(2020, 4, 20, 4, 20)
    mock_accounts.find_one.side_effect = [
        account_bank.dict(exclude_none=True),
        account_cash.dict(exclude_none=True),
        account_broker.dict(exclude_none=True)
    ]
    mock_instruments.find_one.return_value = currency.dict(exclude_none=True)

    res = add_transaction(atm_extraction_in, normal_user)

    stored_transaction_data = atm_extraction.dict(exclude_none=True)
    stored_transaction_data['code'] = '2020-04-20T04:20:00'
    assert res == stored_transaction_data
    mock_collection.insert_one.assert_called_once_with(stored_transaction_data)


@patch('src.operations.transactions.database.transactions')
def test_complete_transaction_not_found(mock_collection, atm_extraction, normal_user):
    mock_collection.find_one.return_value = None

    with pytest.raises(HTTPException):
        complete_transaction(atm_extraction.code, normal_user)


@patch('src.operations.transactions.database.transactions')
def test_complete_transaction_completed(mock_collection, atm_extraction, normal_user):
    transaction_data = atm_extraction.dict(exclude_none=True)
    transaction_data['status'] = TransactionStatus.completed
    mock_collection.find_one.return_value = transaction_data

    with pytest.raises(HTTPException):
        complete_transaction(atm_extraction.code, normal_user)


@patch('src.operations.transactions.database.accounts')
@patch('src.operations.transactions.database.transactions')
def test_complete_transaction_partial(mock_collection, mock_accounts, atm_extraction, normal_user):
    # Set all entries as already completed
    for entry in atm_extraction.entries:
        entry.status = TransactionStatus.completed
    mock_collection.find_one.return_value = atm_extraction.dict(exclude_none=True)

    res = complete_transaction(atm_extraction.code, normal_user)

    # Correct transaction object attributes as expected
    atm_extraction.status = TransactionStatus.completed

    # Assert only transaction status was changed
    assert res == atm_extraction
    assert not mock_accounts.update_one.called
    assert mock_collection.update_one.mock_calls == [
        call(
            {'owner': normal_user.username, 'code': atm_extraction.code},
            {'$set': {'status': TransactionStatus.completed}}
        )
    ]


@patch('src.operations.transactions.database.accounts')
@patch('src.operations.transactions.database.transactions')
def test_complete_transaction_full(mock_collection, mock_accounts, atm_extraction, account_bank, account_cash,
                                   account_broker, normal_user, currency):
    mock_collection.find_one.return_value = atm_extraction.dict(exclude_none=True)
    mock_accounts.find_one.side_effect = [account_bank.dict(exclude_none=True), None, None]

    res = complete_transaction(atm_extraction.code, normal_user)

    # Correct transaction object attributes as expected
    atm_extraction.status = TransactionStatus.completed
    for entry in atm_extraction.entries:
        entry.status = TransactionStatus.completed

    # Assert correct return value and update calls (accounts = 1/entry, transactions = 1/entry + 1)
    assert res == atm_extraction
    assert mock_accounts.update_one.mock_calls == [
        call(
            {'owner': normal_user.username, 'code': account_bank.code},
            {'$inc': {'assets.$[asset].quantity': atm_extraction.entries[0].balance.quantity}},
            array_filters=[{'asset.instrument.code': currency.code}]
        ),
        call(
            {'owner': normal_user.username, 'code': account_cash.code},
            {'$push': {'assets': atm_extraction.entries[1].balance.dict()}},
            array_filters=None
        ),
        call(
            {'owner': normal_user.username, 'code': account_broker.code},
            {'$push': {'assets': atm_extraction.entries[2].balance.dict()}},
            array_filters=None
        )

    ]
    assert mock_collection.update_one.mock_calls == [
        call(
            {'owner': normal_user.username, 'code': atm_extraction.code},
            {'$set': {'entries.0.status': TransactionStatus.completed}}
        ),
        call(
            {'owner': normal_user.username, 'code': atm_extraction.code},
            {'$set': {'entries.1.status': TransactionStatus.completed}}
        ),
        call(
            {'owner': normal_user.username, 'code': atm_extraction.code},
            {'$set': {'entries.2.status': TransactionStatus.completed}}
        ),
        call(
            {'owner': normal_user.username, 'code': atm_extraction.code},
            {'$set': {'status': TransactionStatus.completed}}
        )
    ]


@patch('src.operations.transactions.database.transactions')
def test_get_transactions(mock_collection, atm_extraction, normal_user):
    mock_collection.find.return_value.sort.return_value = [atm_extraction.dict(exclude_none=True)]

    res = get_transactions(normal_user)

    assert len(res) == 1
    assert res[0] == atm_extraction
    mock_collection.find.assert_called_once_with({'owner': normal_user.username})


@patch('src.operations.transactions.database.transactions')
def test_get_transactions_by_status(mock_collection, normal_user):
    mock_collection.find.return_value.sort.return_value = []

    res = get_transactions(normal_user, TransactionStatus.cancelled)

    assert len(res) == 0
    mock_collection.find.assert_called_once_with({'owner': normal_user.username, 'status': TransactionStatus.cancelled})


@patch('src.operations.transactions.database.accounts')
@patch('src.operations.transactions.database.transactions')
def test_cancel_transaction_partial(mock_collection, mock_accounts, atm_extraction, account_bank, normal_user,
                                    currency):
    # Set entries to different status to cover all cases
    atm_extraction.entries[0].status = TransactionStatus.completed
    atm_extraction.entries[1].status = TransactionStatus.pending
    atm_extraction.entries[2].status = TransactionStatus.cancelled
    mock_collection.find_one.return_value = atm_extraction.dict(exclude_none=True)

    res = cancel_transaction(atm_extraction.code, normal_user)

    # Correct transaction object attributes as expected
    atm_extraction.status = TransactionStatus.cancelled
    for entry in atm_extraction.entries:
        entry.status = TransactionStatus.cancelled

    # Assert only "complete" entry was reverted, but status was set for 2
    assert res == atm_extraction
    assert mock_accounts.update_one.mock_calls == [
        call(
            {'owner': normal_user.username, 'code': account_bank.code},
            {'$inc': {'assets.$[asset].quantity': -atm_extraction.entries[0].balance.quantity}},
            array_filters=[{'asset.instrument.code': currency.code}]
        )
    ]
    assert mock_collection.update_one.mock_calls == [
        call(
            {'owner': normal_user.username, 'code': atm_extraction.code},
            {'$set': {'entries.0.status': TransactionStatus.cancelled}}
        ),
        call(
            {'owner': normal_user.username, 'code': atm_extraction.code},
            {'$set': {'entries.1.status': TransactionStatus.cancelled}}
        ),
        call(
            {'owner': normal_user.username, 'code': atm_extraction.code},
            {'$set': {'status': TransactionStatus.cancelled}}
        )
    ]
