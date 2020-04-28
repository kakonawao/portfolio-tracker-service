import pytest

from src.models.auth import UserIn
from src.models.core import Institution, InstitutionType


@pytest.fixture
def normal_user_input():
    return {
        'username': 'potato',
        'password': 'tub3rsar3gr3at'
    }

@pytest.fixture
def admin_user_input(normal_user_input):
    normal_user_input['is_admin'] = True
    return normal_user_input

@pytest.fixture
def normal_user_in(normal_user_input):
    return UserIn(**normal_user_input)


@pytest.fixture
def admin_user_in(admin_user_input):
    return UserIn(**admin_user_input)


@pytest.fixture
def bank_input():
    return {
        'type': InstitutionType.bank,
        'name': 'Bank of Ireland',
        'code': 'BOI'
    }

@pytest.fixture
def institution_in(bank_input):
    return Institution(**bank_input)
