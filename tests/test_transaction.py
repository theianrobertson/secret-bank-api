from datetime import datetime
from decimal import Decimal

from sba import Transaction

TRAN = Transaction(
    id='1',
    account='2',
    account_description='acct',
    date=datetime(2018, 1, 6),
    amount=Decimal('12.14'),
    payee='joe',
    type='debit')

def test_month():
    assert TRAN.month == '2018-01'

def test_to_sheets_values():
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
