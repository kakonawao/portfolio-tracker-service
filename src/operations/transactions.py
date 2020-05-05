from datetime import datetime

from fastapi import Depends, HTTPException, status

from ..config import database
from ..models.auth import User
from ..models.accounts import Account
from ..models.transactions import TransactionIn, TransactionStatus
from .auth import resolve_user


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


def _resolve_entry_data(entry, user):
    account = database.accounts.find_one({'owner': user.username, 'code': entry.account})
    if not account:
        raise ValueError(f'Account with code {entry.account} not found.')

    instrument = database.instruments.find_one({'code': entry.balance.instrument})
    if not instrument:
        raise ValueError(f'Instrument with code {entry.balance.instrument} not found.')

    data = entry.dict(exclude_none=True)
    data['status'] = TransactionStatus.pending
    data['account'] = Account(**account).dict(exclude_none=True)
    data['balance']['instrument'] = instrument
    return data
