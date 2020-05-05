from enum import Enum

from pydantic import BaseModel
from pydantic.fields import List

from .accounts import Account
from .balances import Balance, BalanceIn


class TransactionStatus(str, Enum):
    pending = 'pending'
    completed = 'completed'
    cancelled = 'cancelled'


class TransactionEntryIn(BaseModel):
    account: str
    balance: BalanceIn


class TransactionEntry(TransactionEntryIn):
    account: Account
    balance: Balance
    status: TransactionStatus


class TransactionIn(BaseModel):
    description: str
    total: BalanceIn
    entries: List[TransactionEntryIn]


class Transaction(TransactionIn):
    owner: str
    code: str
    status: TransactionStatus
    total: Balance
    entries: List[TransactionEntry]
