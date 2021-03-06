import copy
from datetime import datetime

import pytest

from src.models.auth import UserIn
from src.models.institutions import Institution, InstitutionType
from src.models.instruments import Instrument, InstrumentIn, InstrumentType, Security, ValueIn, Value
from src.models.accounts import AccountIn, AccountType, CashAccount, FinancialAccount
from src.models.transactions import Transaction, TransactionIn, TransactionStatus


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
def normal_user(normal_user_input):
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
def currency_in(currency_input):
    return InstrumentIn(**currency_input)


@pytest.fixture
def currency(currency_input):
    data = copy.copy(currency_input)
    data['code'] = currency_input['symbol']
    return Instrument(**data)


@pytest.fixture
def security_in(security_input):
    return InstrumentIn(**security_input)


@pytest.fixture
def security(security_input, exchange_input):
    data = copy.copy(security_input)
    data['exchange'] = exchange_input
    data['code'] = f'{exchange_input["code"]}:{data["symbol"]}'
    return Security(**data)


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
def account_cash_in(account_cash_input):
    return AccountIn(**account_cash_input)


@pytest.fixture
def account_cash(account_cash_input, normal_user_input):
    data = copy.copy(account_cash_input)
    data['owner'] = normal_user_input['username']
    data['holder'] = None
    data['assets'] = []
    return CashAccount(**data)


@pytest.fixture
def account_bank_input():
    return {
        'type': AccountType.bank,
        'holder': 'BOI',
        'code': 'BOICA',
        'description': 'My BOI current account'
    }


@pytest.fixture
def account_bank_in(account_bank_input):
    return AccountIn(**account_bank_input)


@pytest.fixture
def account_bank(account_bank_input, normal_user_input, bank_input):
    data = copy.copy(account_bank_input)
    data['owner'] = normal_user_input['username']
    data['holder'] = bank_input
    data['assets'] = []
    return FinancialAccount(**data)


@pytest.fixture
def account_broker_input():
    return {
        'type': AccountType.investment,
        'holder': 'MS',
        'code': 'MSIP01',
        'description': 'Morgan Stanley investment plan'
    }


@pytest.fixture
def account_broker_in(account_broker_input):
    return AccountIn(**account_broker_input)


@pytest.fixture
def account_broker(account_broker_input, normal_user_input, broker_input):
    data = copy.copy(account_broker_input)
    data['owner'] = normal_user_input['username']
    data['holder'] = broker_input
    data['assets'] = []
    return FinancialAccount(**data)


# Transactions

@pytest.fixture
def atm_extraction_input():
    return {
        'description': 'Extract money from ATM',
        'total': {
            'instrument': 'EUR',
            'quantity': 100
        },
        'entries': [
            {
                'account': 'BOICEUR',
                'balance': {
                    'instrument': 'EUR',
                    'quantity': -100
                }
            },
            {
                'account': 'WALLET',
                'balance': {
                    'instrument': 'EUR',
                    'quantity': 50
                }
            },
            {
                'account': 'DEGIRO',
                'balance': {
                    'instrument': 'EUR',
                    'quantity': 50
                }
            },
        ]
    }


@pytest.fixture
def atm_extraction_in(atm_extraction_input):
    return TransactionIn(**atm_extraction_input)


@pytest.fixture
def atm_extraction(atm_extraction_input, currency, account_bank_input, account_cash_input, account_broker_input,
                   normal_user_input):
    data = copy.copy(atm_extraction_input)
    data['owner'] = normal_user_input['username']
    data['total']['instrument'] = currency.dict(exclude_none=True)
    data['status'] = TransactionStatus.pending
    data['entries'][0]['account'] = account_bank_input
    data['entries'][0]['status'] = TransactionStatus.pending
    data['entries'][0]['balance']['instrument'] = data['total']['instrument']
    data['entries'][1]['account'] = account_cash_input
    data['entries'][1]['status'] = TransactionStatus.pending
    data['entries'][1]['balance']['instrument'] = data['total']['instrument']
    data['entries'][2]['account'] = account_broker_input
    data['entries'][2]['status'] = TransactionStatus.pending
    data['entries'][2]['balance']['instrument'] = data['total']['instrument']
    data['code'] = datetime(2020, 4, 20, 4, 20).isoformat()[:19]
    return Transaction(**data)


# Values
@pytest.fixture
def value_input():
    return {
        'values': {
            'USD': 1.1,
            'ARS': 70
        }
    }

@pytest.fixture
def value_in(value_input):
    return ValueIn(**value_input)


@pytest.fixture
def value(value_input, currency):
    data = copy.copy(value_input)
    data['instrument'] = currency.dict()
    data['date'] = datetime(2020, 4, 20)
    return Value(**data)
