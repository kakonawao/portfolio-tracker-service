from pydantic import BaseModel

from .instruments import Instrument


class BalanceIn(BaseModel):
    instrument: str
    quantity: float


class Balance(BalanceIn):
    instrument: Instrument
