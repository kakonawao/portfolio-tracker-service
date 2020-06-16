import pymongo
from fastapi import Depends
from pymongo.errors import DuplicateKeyError

from ..config import database
from ..exceptions import ValidationError, NotFoundError, handled
from ..models.auth import User
from ..models.accounts import AccountIn, AccountType
from .auth import resolve_user


def _resolve_account_data(account, user):
    data = account.dict(exclude_none=True)
    data['owner'] = user.username
    data['assets'] = []

    if not account.type.holder_type:
        data.pop('holder', None)

    else:
        if not data.get('holder'):
            raise ValidationError(f'Account holder is required for {account.type} account')

        holder_data = database.institutions.find_one(
            {
                'type': account.type.holder_type,
                'code': data['holder']
            }
        )
        if not holder_data:
            raise ValidationError(f'Institution of type {account.type.holder_type} with code '
                                  f'{account.holder} does not exist')
        data['holder'] = holder_data

    return data


@handled
def add_account(account: AccountIn, user: User = Depends(resolve_user)):
    try:
        data = _resolve_account_data(account, user)
        database.accounts.insert_one(data)

    except DuplicateKeyError:
        raise ValidationError(f'Account with code {account.code} already exists.')

    return data


@handled
def get_accounts(user: User = Depends(resolve_user), t: AccountType = None):
    filters = {'owner': user.username}
    if t:
        filters['type'] = t

    return [a for a in database.accounts.find(filters).sort(
        [
            ('code', pymongo.ASCENDING)
        ]
    )]


@handled
def modify_account(code: str, account: AccountIn, user: User = Depends(resolve_user)):
    data = _resolve_account_data(account, user)
    res = database.accounts.replace_one({'owner': user.username, 'code': code}, data)

    if not res.modified_count:
        raise NotFoundError(f'Account with code {code} does not exist.')

    return data


@handled
def delete_account(code: str, user: User = Depends(resolve_user)):
    database.accounts.delete_one({'owner': user.username, 'code': code})
