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


class InstrumentIn(BaseModel):
    type: InstrumentType
    description: str
    symbol: str
    exchange: str = None


class Instrument(InstrumentIn):
    exchange: Institution = None
