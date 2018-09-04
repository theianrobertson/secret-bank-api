from unittest import mock
import pytest
from datetime import datetime
from decimal import Decimal

import sba.transaction

MOCK_CONFIG_CATEGORIES = {
    "salary": [{"type": "dep", "payee": "^SOMEONE WHAT PAYS ME$"}],
    "restaurants": ["^A&W", "^BOSTON PIZZA", "^BURGER KING"],
    "other": ["^BOSTON"]}
TRAN = sba.transaction.Transaction(
    id='1',
    account='2',
    date=datetime(2018, 1, 6),
    amount=Decimal('12.14'),
    payee='joe',
    type='debit')

def test_month():
    assert TRAN.month == '2018-01'

@mock.patch('sba.config.account_lookup', return_value={'2': 'acct'})
def test_to_sheets_values(mocker):
    assert TRAN.to_sheets_values == [
        '1',
        '2',
        'acct',
        '2018-01-06',
        '12.14',
        'joe',
        'debit',
        '',
        '2018-01'
    ]

@pytest.mark.parametrize('categorizer,match', [
    ('^jo', True),
    ('^jo$', False),
    ({'payee': '^jo', 'amount': "12.14"}, True),
    ({'payee': '^jo', 'amount': "12.1"}, False),
    ({'payee': '^jo', 'amount': "12.1", "account": "20"}, False),
    ({'payee': '^jo', 'amount': "12.143"}, False),
    ({'type': 'debit', 'amount': "12.1"}, False),
    ({'type': 'debit', 'amount': "12.14"}, True),
    ({'id': '1', 'account': "2"}, True),
    ({'id': '1', 'account': "3"}, False),
])
def test_categorizer_from_config_entry(categorizer, match):
    assert sba.transaction.categorizer_from_config_entry(categorizer)(TRAN) is match

def test_filter_dict():
    some_dict = {
        "id": "hi",
        "account": "acct",
        "date": "date",
        "amount": "amount",
        "payee": "payee",
        "type": "other",
        "other_thing": "hi"}
    filtered = sba.transaction.filter_dict(some_dict)
    assert set(['id', 'account', 'date', 'amount', 'payee', 'type']) == set(filtered.keys())

@pytest.mark.parametrize('transaction,expected',[
    (sba.transaction.Transaction(id='1', account='2', date=datetime(2018, 1, 6), amount=Decimal('12.14'), payee='joe', type='debit'), ''),
    (sba.transaction.Transaction(id='1', account='2', date=datetime(2018, 1, 6), amount=Decimal('12.14'), payee='A&W #1234', type='debit'), 'restaurants'),
    (sba.transaction.Transaction(id='1', account='2', date=datetime(2018, 1, 6), amount=Decimal('12.14'), payee='BOSTON PIZZA', type='debit'), ''),
    (sba.transaction.Transaction(id='1', account='2', date=datetime(2018, 1, 6), amount=Decimal('12.14'), payee='SOMEONE WHAT PAYS ME', type='dep'), 'salary'),
    (sba.transaction.Transaction(id='1', account='2', date=datetime(2018, 1, 6), amount=Decimal('12.14'), payee='SOMEONE WHAT PAYS ME', type='credit'), ''),
])
@mock.patch('sba.config.categories', return_value=MOCK_CONFIG_CATEGORIES)
def test_get_category(mocker, transaction, expected):
    assert sba.transaction.get_category(transaction) == expected
