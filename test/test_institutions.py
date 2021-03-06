import pytest
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from unittest.mock import patch

from src.models.institutions import InstitutionType
from src.operations.institutions import add_institution, get_institutions, modify_institution, delete_institution
from .fixtures import bank, bank_input, broker, broker_input, normal_user, normal_user_input


@patch('src.operations.institutions.database.institutions')
def test_add_institution_failure(collection_mock, bank):
    collection_mock.insert_one.side_effect = DuplicateKeyError('Bank already exists')
    with pytest.raises(HTTPException) as excinfo:
        add_institution(bank)

    assert excinfo.value.status_code == 400


@patch('src.operations.institutions.database.institutions')
def test_add_institution_success(collection_mock, bank):
    res = add_institution(bank)

    assert res == bank
    collection_mock.insert_one.assert_called_once_with(bank.dict(exclude_none=True))


@patch('src.operations.institutions.database.institutions')
def test_get_institutions(collection_mock, bank, broker):
    collection_mock.find.return_value.sort.return_value = [
        bank.dict(exclude_none=True),
        broker.dict(exclude_none=True)
    ]

    res = get_institutions()

    assert len(res) == 2
    assert res[0] == bank
    assert res[1] == broker
    collection_mock.find.assert_called_once_with({})


@patch('src.operations.institutions.database.institutions')
def test_get_institutions_by_type(collection_mock, bank, normal_user):
    collection_mock.find.return_value.sort.return_value = [
        bank.dict(exclude_none=True),
    ]

    res = get_institutions(normal_user, InstitutionType.bank)

    assert len(res) == 1
    assert res[0] == bank
    collection_mock.find.assert_called_once_with({'type': InstitutionType.bank})


@patch('src.operations.institutions.database.institutions')
def test_modify_institution(collection_mock, bank):
    bank.name = 'Boys Over Internet'
    res = modify_institution(bank.code, bank)

    assert res == bank
    collection_mock.replace_one.assert_called_once_with({'code': bank.code}, bank.dict(exclude_none=True))


@patch('src.operations.institutions.database.institutions')
def test_modify_institution_not_found(collection_mock, bank):
    bank.name = 'Boys Over Internet'
    collection_mock.replace_one.return_value.modified_count = 0

    with pytest.raises(HTTPException) as excinfo:
        modify_institution(bank.code, bank)

    assert excinfo.value.status_code == 404


@patch('src.operations.institutions.database.institutions')
def test_delete_institution(collection_mock, bank):
    delete_institution(bank.code)

    collection_mock.delete_one.assert_called_once_with({'code': bank.code})
