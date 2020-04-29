import pytest
from pydantic import ValidationError

from src.models.core import Institution, InstitutionType, Instrument, InstrumentIn, InstrumentType
from .fixtures import bank_input, currency_input, security_input, security_data, exchange, exchange_input


def test_invalid_institution():
    with pytest.raises(ValidationError):
        Institution()


def test_valid_institution(bank_input):
    institution = Institution(**bank_input)

    assert institution.type == InstitutionType.bank


def test_invalid_instrument():
    with pytest.raises(ValidationError):
        InstrumentIn()

    with pytest.raises(ValidationError):
        Instrument()


def test_valid_instrument_in(currency_input, security_input):
    currency_in = InstrumentIn(**currency_input)
    security_in = InstrumentIn(**security_input)

    assert currency_in.type == InstrumentType.currency
    assert security_in.type == InstrumentType.security


def test_valid_instrument(currency_input, security_data, exchange):
    currency = Instrument(**currency_input)
    security = Instrument(**security_data)

    assert currency.type == InstrumentType.currency
    assert security.type == InstrumentType.security
    assert security.exchange == exchange
