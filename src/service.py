import pymongo
from fastapi import FastAPI
from pydantic.fields import List, Union

from .config import database
from .models.auth import User
from .models.institutions import Institution
from .models.instruments import Instrument, Security
from .models.accounts import FinancialAccount, CashAccount
from .models.transactions import Transaction
from .operations.auth import add_user, authenticate, get_current_user
from .operations.institutions import add_institution, get_institutions, modify_institution, delete_institution
from .operations.instruments import add_instrument, get_instruments, modify_instrument, delete_instrument
from .operations.accounts import add_account, get_accounts, modify_account, delete_account
from .operations.transactions import add_transaction, get_transactions, complete_transaction


# Service

service = FastAPI()


# Start/end event hooks

@service.on_event("startup")
async def startup_event():
    database.users.create_index(
        [
            ('username', pymongo.ASCENDING)
         ],
        unique=True
    )

    database.institutions.create_index(
        [
            ('code', pymongo.ASCENDING)
        ],
        unique=True
    )

    database.instruments.create_index(
        [
            ('code', pymongo.ASCENDING)
        ],
        unique=True
    )

    database.accounts.create_index(
        [
            ('owner', pymongo.ASCENDING),
            ('code', pymongo.ASCENDING)
        ],
        unique=True
    )

    database.transactions.create_index(
        [
            ('owner', pymongo.ASCENDING),
            ('code', pymongo.ASCENDING)
        ],
        unique=True
    )


# Hook up resources to operations

service.post('/users', response_model=User)(add_user)
service.post('/sessions')(authenticate)
service.get('/sessions/current', response_model=User)(get_current_user)

service.post('/institutions', response_model=Institution)(add_institution)
service.get('/institutions', response_model=List[Institution])(get_institutions)
service.put('/institutions/{code}', response_model=Institution)(modify_institution)
service.delete('/institutions/{code}')(delete_institution)

service.post('/instruments', response_model=Union[Security, Instrument])(add_instrument)
service.get('/instruments', response_model=List[Union[Security, Instrument]])(get_instruments)
service.put('/instruments/{code}', response_model=Union[Security, Instrument])(modify_instrument)
service.delete('/instruments/{code}')(delete_instrument)

service.post('/accounts', response_model=Union[FinancialAccount, CashAccount])(add_account)
service.get('/accounts', response_model=List[Union[FinancialAccount, CashAccount]])(get_accounts)
service.put('/accounts/{code}', response_model=Union[FinancialAccount, CashAccount])(modify_account)
service.delete('/accounts/{code}')(delete_account)

service.post('/transactions', response_model=Transaction)(add_transaction)
service.get('/transactions', response_model=List[Transaction])(get_transactions)
service.put('/transactions/{code}/complete', response_model=Transaction)(complete_transaction)
