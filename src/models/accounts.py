from enum import Enum

from pydantic import BaseModel
from pydantic.fields import List

from .institutions import Institution, InstitutionType
from .balances import Balance


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


class Account(BaseModel):
    type: AccountType
    code: str
    description: str


class AccountIn(Account):
    holder: str = None


class OwnedAccount(Account):
    owner: str
    assets: List[Balance] = []


class CashAccount(OwnedAccount):
    type = AccountType.cash


class FinancialAccount(OwnedAccount):
    holder: Institution
