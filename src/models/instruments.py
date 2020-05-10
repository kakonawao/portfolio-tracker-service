from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from pydantic.fields import Dict

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


class Currency(Instrument):
    type = InstrumentType.currency


class Security(Instrument):
    type = InstrumentType.security
    exchange: Institution


class ValueIn(BaseModel):
    values: Dict[str, float]


class Value(ValueIn):
    instrument: Instrument
    date: datetime
