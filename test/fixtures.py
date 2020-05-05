import copy
from datetime import datetime

import pytest

from src.models.auth import UserIn
from src.models.institutions import Institution, InstitutionType
from src.models.instruments import Instrument, InstrumentIn, InstrumentType, Security
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
        'type': AccountType.current,
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
def transaction_input():
    return {
        'description': 'Initial money in my wallet',
        'total': {
            'instrument': 'EUR',
            'quantity': 3.14
        },
        'entries': [{
            'account': 'WALLET',
            'balance': {
                'instrument': 'EUR',
                'quantity': 3.14
            }
        }]
    }

@pytest.fixture
def transaction_in(transaction_input):
    return TransactionIn(**transaction_input)

@pytest.fixture
def transaction(transaction_input, currency, account_cash_input, normal_user_input):
    data = copy.copy(transaction_input)
    data['owner'] = normal_user_input['username']
    data['total']['instrument'] = currency.dict(exclude_none=True)
    data['status'] = TransactionStatus.pending
    data['entries'][0]['account'] = account_cash_input
    data['entries'][0]['status'] = TransactionStatus.pending
    data['entries'][0]['balance']['instrument'] = currency.dict(exclude_none=True)
    data['code'] = datetime(2020, 4, 20, 4, 20).isoformat()[:19]
    return Transaction(**data)
