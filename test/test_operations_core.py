import pytest
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from unittest.mock import patch

from src.operations.core import add_institution
from .fixtures import admin_user_in, admin_user_input, bank_input, institution_in


@patch('src.operations.core.database.institutions')
def test_add_institution_failure(collection_mock, institution_in):
    collection_mock.insert_one.side_effect = DuplicateKeyError('Bank already exists')
    with pytest.raises(HTTPException):
        add_institution(institution_in)


@patch('src.operations.core.database.institutions')
def test_add_institution_success(collection_mock, institution_in):
    institution = add_institution(institution_in)

    collection_mock.insert_one.assert_called_once_with({
        'type': institution_in.type,
        'code': institution_in.code,
        'name': institution_in.name
    })
    assert institution == institution_in
