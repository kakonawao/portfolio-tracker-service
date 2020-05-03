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
