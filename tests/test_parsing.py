import os
from datetime import datetime
from decimal import Decimal
import pytest
from sba import parsing, Balance, Transaction

CURR_DIR = os.path.dirname(os.path.realpath(__file__))

@pytest.mark.parametrize('date_string, expected', [
    ('AUG 19, 2018', datetime(2018, 8, 19)),
    ('November 16, 2018', datetime(2018, 11, 16)),
    ('SEP 01, 2018', datetime(2018, 9, 1)),
])
def test_get_date_from_string(date_string, expected):
    assert parsing.get_date_from_string(date_string) == expected

def test_capitalone_balance_alert():
    with open(os.path.join(CURR_DIR, 'capitalone', 'balance_alert', 'test_bal.txt')) as f:
        data = f.read()
    expected = Balance(account='1234', date=datetime(2018,8,10), balance=Decimal('3414.55'))
    assert parsing.capitalone_balance_alert(data) == expected # dataclasses do equality 👌

@pytest.mark.parametrize('amt_string, expected', [
    ("$1,234.12", Decimal('1234.12')),
    ("$1234.12", Decimal('1234.12')),
    ("23.24", Decimal('23.24'))
])
def test_get_amount_from_string(amt_string, expected):
    assert parsing.get_amount_from_string(amt_string) == expected

def test_capitalone_transaction_charged():
    with open(os.path.join(CURR_DIR, 'capitalone', 'transaction_charged', 'test_txn.txt')) as f:
        data = f.read()
    expected = Transaction(
        id=None, account='1234', date=datetime(2018,11,19), amount=Decimal('80.00'),
        payee='SOME MERCHANT 1234', type='debit')
    assert parsing.capitalone_transaction_charged(data) == expected
