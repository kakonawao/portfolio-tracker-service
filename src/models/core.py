from enum import Enum

from pydantic import BaseModel


class InstitutionType(str, Enum):
    bank = 'bank'
    broker = 'broker'
    exchange = 'exchange'


class Institution(BaseModel):
    type: InstitutionType
    name: str
    code: str


class InstrumentType(str, Enum):
    currency = 'currency'
    index = 'index'
    security = 'security'


class Instrument(BaseModel):
    type: InstrumentType
    description: str
    symbol: str

    @property
    def code(self):
        return self.symbol


class InstrumentIn(Instrument):
    exchange: str = None

    @property
    def code(self):
        return f'{self.exchange}:{self.symbol}' if self.type == self.type.security else f'{self.symbol}'


class Security(Instrument):
    type = InstrumentType.security
    exchange: Institution

    @property
    def code(self):
        return f'{self.exchange.code}:{self.symbol}'
