from datetime import datetime

from fastapi import Depends, HTTPException, status

from ..config import database
from ..models.auth import User
from ..models.balances import Balance
from ..models.accounts import Account
from ..models.transactions import Transaction, TransactionIn, TransactionEntryIn, TransactionStatus
from .auth import resolve_user


def _resolve_entry_data(entry: TransactionEntryIn, user: User):
    account_data = database.accounts.find_one({'owner': user.username, 'code': entry.account})
    if not account_data:
        raise ValueError(f'Account with code {entry.account} not found.')

    instrument_data = database.instruments.find_one({'code': entry.balance.instrument})
    if not instrument_data:
        raise ValueError(f'Instrument with code {entry.balance.instrument} not found.')

    data = entry.dict(exclude_none=True)
    data['status'] = TransactionStatus.pending
    data['account'] = Account(**account_data).dict(exclude_none=True)
    data['balance']['instrument'] = instrument_data
    return data


def _update_account_balance(user: User, account: Account, balance: Balance):
    account_filter = {'owner': user.username, 'code': account.code}

    account_doc = database.accounts.find_one({**account_filter, 'assets.instrument.code': balance.instrument.code})
    if account_doc:
        # Account contains asset, update it
        update_doc = {'$inc': {'assets.$[asset].quantity': balance.quantity}}
        array_filters = [{'asset.instrument.code': balance.instrument.code}]

    else:
        # Account does not contain asset, push it
        update_doc = {'$push': {'assets': balance.dict()}}
        array_filters = None

    database.accounts.update_one(
        account_filter,
        update_doc,
        array_filters=array_filters
    )


def _revert_account_balance(user: User, account: Account, balance: Balance):
    database.accounts.update_one(
        {'owner': user.username, 'code': account.code},
        {'$inc': {'assets.$[asset].quantity': -balance.quantity}},
        array_filters=[{'asset.instrument.code': balance.instrument.code}]
    )


def add_transaction(transaction: TransactionIn, user: User = Depends(resolve_user)):
    try:
        data = transaction.dict(exclude_none=True)
        data['owner'] = user.username
        data['status'] = TransactionStatus.pending
        data['code'] = datetime.utcnow().isoformat()[:19]
        data['entries'] = [_resolve_entry_data(entry, user) for entry in transaction.entries]
        data['total']['instrument'] = database.instruments.find_one({'code': transaction.total.instrument})
        database.transactions.insert_one(data)

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'{ve}'
        )

    return data


def get_transactions(user: User = Depends(resolve_user)):
    return [t for t in database.transactions.find({'owner': user.username})]


def _get_transaction_for_processing(filters: dict, target_status: TransactionStatus):
    doc = database.transactions.find_one(filters)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Transaction {filters["code"]} not found.'
        )

    if doc['status'] == target_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Transaction {filters["code"]} is already {target_status}.'
        )

    return Transaction(**doc)


def complete_transaction(code: str, user: User = Depends(resolve_user)):
    transaction_filters = {'owner': user.username, 'code': code}
    transaction = _get_transaction_for_processing(transaction_filters, TransactionStatus.completed)

    for entry_n, entry in enumerate(transaction.entries):
        if entry.status != TransactionStatus.completed:
            # TODO: make this block atomic (see https://github.com/kakonawao/portfolio-tracker-service/issues/44)
            _update_account_balance(user, entry.account, entry.balance)
            database.transactions.update_one(
                transaction_filters,
                {'$set': {f'entries.{entry_n}.status': TransactionStatus.completed}}
            )
            entry.status = TransactionStatus.completed

    database.transactions.update_one(
        transaction_filters,
        {'$set': {'status': TransactionStatus.completed}},
    )
    transaction.status = TransactionStatus.completed
    return transaction


def cancel_transaction(code: str, user: User = Depends(resolve_user)):
    transaction_filters = {'owner': user.username, 'code': code}
    transaction = _get_transaction_for_processing(transaction_filters, TransactionStatus.cancelled)

    for entry_n, entry in enumerate(transaction.entries):
        if entry.status != TransactionStatus.cancelled:
            # TODO: make this block atomic (see https://github.com/kakonawao/portfolio-tracker-service/issues/44)
            if entry.status == TransactionStatus.completed:
                # Entry already processed, need to revert it
                _revert_account_balance(user, entry.account, entry.balance)

            database.transactions.update_one(
                transaction_filters,
                {'$set': {f'entries.{entry_n}.status': TransactionStatus.cancelled}}
            )
            entry.status = TransactionStatus.cancelled

    database.transactions.update_one(
        transaction_filters,
        {'$set': {'status': TransactionStatus.cancelled}},
    )
    transaction.status = TransactionStatus.cancelled
    return transaction
