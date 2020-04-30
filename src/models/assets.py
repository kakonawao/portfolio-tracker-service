from enum import Enum

from pydantic import BaseModel
from pydantic.fields import Union

from .core import Institution, InstitutionType


class AccountType(str, Enum):
    cash = 'cash'
    current = 'current'
    savings = 'savings'
    investment = 'investment'

    @property
    def holder_type(self):
        if self.value in (self.current, self.savings):
            return InstitutionType.bank
        elif self.value in (self.investment):
            return InstitutionType.broker

        return None


class AccountIn(BaseModel):
    type: AccountType
    holder: str = None
    code: str
    description: str


class Account(AccountIn):
    owner: str
    holder: Union[None, Institution]
