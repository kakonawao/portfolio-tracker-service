from fastapi import Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError

from ..config import database
from ..models.auth import User
from ..models.assets import AccountIn, AccountType
from .auth import resolve_user


def add_account(account: AccountIn, user: User = Depends(resolve_user)):
    try:
        data = account.dict(exclude_none=True)
        data['owner'] = user.username

        if not account.type.holder_type:
            data.pop('holder', None)

        else:
            if not data.get('holder'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Account holder is required for {account.type} account.'
                )

            holder_data = database.institutions.find_one(
                {
                    'type': account.type.holder_type,
                    'code': data['holder']
                }
            )
            if not holder_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Institution of type {account.type.holder_type} with code {account.holder} does not exist.'
                )
            data['holder'] = holder_data

        database.accounts.insert_one(data)

    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Account with code {account.code} already exists.'
        )

    return data


def get_accounts(user: User = Depends(resolve_user)):
    return [a for a in database.accounts.find({'owner': user.username})]
