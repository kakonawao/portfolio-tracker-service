from enum import Enum

from pydantic import BaseModel

from .institutions import Institution


class InstrumentType(str, Enum):
    currency = 'currency'
    index = 'index'
    security = 'security'


class InstrumentBase(BaseModel):
    type: InstrumentType
    description: str
    symbol: str


class InstrumentIn(InstrumentBase):
    exchange: str = None


class Instrument(InstrumentBase):
    code: str


class Security(Instrument):
    type = InstrumentType.security
    exchange: Institution
