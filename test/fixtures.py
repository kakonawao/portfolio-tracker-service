import copy

import pytest

from src.models.auth import UserIn
from src.models.core import Institution, InstitutionType, Instrument, InstrumentIn, InstrumentType


# Users

@pytest.fixture
def normal_user_input():
    return {
        'username': 'potato',
        'password': 'tub3rsar3gr3at'
    }

@pytest.fixture
def admin_user_input(normal_user_input):
    input = copy.copy(normal_user_input)
    input['is_admin'] = True
    return input

@pytest.fixture
def normal_user_in(normal_user_input):
    return UserIn(**normal_user_input)


@pytest.fixture
def admin_user_in(admin_user_input):
    return UserIn(**admin_user_input)


# Institutions

@pytest.fixture
def bank_input():
    return {
        'type': InstitutionType.bank,
        'name': 'Bank of Ireland',
        'code': 'BOI'
    }

@pytest.fixture
def exchange_input():
    return {
        'type': InstitutionType.exchange,
        'name': 'Nasdaq',
        'code': 'NDQ'
    }

@pytest.fixture
def bank(bank_input):
    return Institution(**bank_input)

@pytest.fixture
def exchange(exchange_input):
    return Institution(**exchange_input)


# Instruments

@pytest.fixture
def currency_input():
    return {
        'type': InstrumentType.currency,
        'description': 'Euro',
        'symbol': 'EUR'
    }

@pytest.fixture
def security_input():
    return {
        'type': InstrumentType.security,
        'description': 'Amazon',
        'symbol': 'AMZN',
        'exchange': 'NDQ'
    }

@pytest.fixture
def security_data(security_input, exchange_input):
    data = copy.copy(security_input)
    data['exchange'] = exchange_input
    return data

@pytest.fixture
def currency(currency_input):
    return InstrumentIn(**currency_input)


@pytest.fixture
def security_in(security_input):
    return InstrumentIn(**security_input)

@pytest.fixture
def security(security_data):
    return Instrument(**security_data)
