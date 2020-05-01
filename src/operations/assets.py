from fastapi import Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError

from ..config import database
from ..models.auth import User
from ..models.assets import AccountIn, AccountType
from .auth import resolve_user


def add_account(account: AccountIn, user: User = Depends(resolve_user)):
    try:
        data = _resolve_account_data(account, user)
        database.accounts.insert_one(data)

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'{ve}'
        )

    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Account with code {account.code} already exists.'
        )

    return data


def get_accounts(user: User = Depends(resolve_user)):
    return [a for a in database.accounts.find({'owner': user.username})]


def modify_account(code: str, account: AccountIn, user: User = Depends(resolve_user)):
    try:
        data = _resolve_account_data(account, user)
        database.accounts.update_one({'owner': user.username, 'code': code}, {'$set': data})

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'{ve}'
        )

    return data


def delete_account(code: str, user: User = Depends(resolve_user)):
    database.accounts.delete_one({'owner': user.username, 'code': code})


def _resolve_account_data(account, user):
    data = account.dict(exclude_none=True)
    data['owner'] = user.username

    if not account.type.holder_type:
        data.pop('holder', None)

    else:
        if not data.get('holder'):
            raise ValueError(f'Account holder is required for {account.type} account.')

        holder_data = database.institutions.find_one(
            {
                'type': account.type.holder_type,
                'code': data['holder']
            }
        )
        if not holder_data:
            raise ValueError(f'Institution of type {account.type.holder_type} with code '
                             f'{account.holder} does not exist.')
        data['holder'] = holder_data

    return data

