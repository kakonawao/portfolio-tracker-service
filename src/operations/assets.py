from fastapi import Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError

from ..config import database
from ..models.auth import User
from ..models.assets import AccountIn, AccountType
from .auth import resolve_user


def add_account(account: AccountIn, user: User = Depends(resolve_user)):
    try:
        data = account.dict()
        data['owner'] = user.username

        if account.type == AccountType.cash:
            data['holder'] = None

        else:
            if not data['holder']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Account holder is required for {account.type} account.'
                )

            holder_data = database.institutions.find_one({'code': data['holder']})
            if not holder_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Institution with code {account.holder} does not exist.'
                )
            data['holder'] = holder_data

        database.accounts.insert_one(data)

    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Account with code {account.code} already exists.'
        )

    return data
