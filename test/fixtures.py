import copy

import pytest

from src.models.auth import UserIn
from src.models.core import Institution, InstitutionType, Instrument, InstrumentIn, InstrumentType
from src.models.assets import Account, AccountIn, AccountType


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
def broker_input():
    return {
        'type': InstitutionType.broker,
        'name': 'Morgan Stanley',
        'code': 'MS'
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
def broker(broker_input):
    return Institution(**broker_input)

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


# Assets

@pytest.fixture
def account_cash_input():
    return {
        'type': AccountType.cash,
        'holder': 'potato',
        'code': 'WALLET',
        'description': 'My wallet'
    }

@pytest.fixture
def account_cash_data(account_cash_input, normal_user_input):
    data = copy.copy(account_cash_input)
    data['owner'] = normal_user_input['username']
    data['holder'] = None
    return data

@pytest.fixture
def account_cash_in(account_cash_input):
    return AccountIn(**account_cash_input)

@pytest.fixture
def account_cash(account_cash_data):
    return Account(**account_cash_data)

@pytest.fixture
def account_bank_input():
    return {
        'type': AccountType.current,
        'holder': 'BOI',
        'code': 'BOICA',
        'description': 'My BOI current account'
    }

@pytest.fixture
def account_bank_data(account_bank_input, normal_user_input, bank_input):
    data = copy.copy(account_bank_input)
    data['owner'] = normal_user_input['username']
    data['holder'] = bank_input
    return data

@pytest.fixture
def account_bank_in(account_bank_input):
    return AccountIn(**account_bank_input)

@pytest.fixture
def account_bank(account_bank_data):
    return Account(**account_bank_data)

@pytest.fixture
def account_broker_input():
    return {
        'type': AccountType.investment,
        'holder': 'MS',
        'code': 'MSIP01',
        'description': 'Morgan Stanley investment plan'
    }

@pytest.fixture
def account_broker_data(account_broker_input, normal_user_input, broker_input):
    data = copy.copy(account_broker_input)
    data['owner'] = normal_user_input['username']
    data['holder'] = broker_input
    return data

@pytest.fixture
def account_broker_in(account_broker_input):
    return AccountIn(**account_broker_input)

@pytest.fixture
def account_broker(account_broker_data):
    return Account(**account_broker_data)
