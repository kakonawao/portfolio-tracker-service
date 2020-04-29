import pytest
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from unittest.mock import patch

from src.operations.core import add_institution, get_institutions
from .fixtures import admin_user_in, admin_user_input, bank_input, institution


@patch('src.operations.core.database.institutions')
def test_add_institution_failure(collection_mock, institution):
    collection_mock.insert_one.side_effect = DuplicateKeyError('Bank already exists')
    with pytest.raises(HTTPException):
        add_institution(institution)


@patch('src.operations.core.database.institutions')
def test_add_institution_success(collection_mock, institution):
    res = add_institution(institution)

    collection_mock.insert_one.assert_called_once_with({
        'type': institution.type,
        'code': institution.code,
        'name': institution.name
    })
    assert res == institution


@patch('src.operations.core.database.institutions')
def test_get_institutions(collection_mock, bank_input, institution):
    collection_mock.find.return_value = [
        bank_input,
    ]

    res = get_institutions()

    assert len(res) == 1
    assert res[0] == institution
