import pytest
from pydantic import ValidationError

from src.models.core import Institution, InstitutionType
from .fixtures import bank_input


def test_invalid_institution():
    with pytest.raises(ValidationError):
        Institution()


def test_valid_institution(bank_input):
    institution = Institution(**bank_input)

    assert institution.type == InstitutionType.bank
