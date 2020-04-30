from enum import Enum

from pydantic import BaseModel
from pydantic.fields import Union

from .core import Institution


class AccountType(str, Enum):
    cash = 'cash'
    current = 'current'
    savings = 'savings'
    investment = 'investment'


class AccountIn(BaseModel):
    type: AccountType
    holder: str = None
    code: str
    description: str


class Account(AccountIn):
    owner: str
    holder: Union[None, Institution]
