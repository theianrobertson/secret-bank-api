from decimal import Decimal
from datetime import datetime
import logging
from sba import Balance, Transaction

def get_date_from_string(date_string):
    try:
        return datetime.strptime(date_string, '%b %d, %Y')
    except ValueError:
        try:
            return datetime.strptime(date_string, '%B %d, %Y')
        except ValueError:
            logging.error('Could not parse date {}'.format(date_string))
            return None

def get_amount_from_string(amt_string):
    return Decimal(amt_string.replace('$', '').replace(',', ''))

def get_capitalone_account(data):
    return data.split("Re: Account ending in ")[1].split()[0]

def capitalone_balance_alert(data):
    account = get_capitalone_account(data)
    balance_string = data.split("Your balance has reached ")[1].split('\n')[0]
    if balance_string[-1] == '.':
        balance_string = balance_string[:-1]
    balance = get_amount_from_string(balance_string)
    date_string = data.split("This is to let you know that as of ")[1].split('\n')[0]
    date_string = ','.join(date_string.split(',')[0:2])
    date = get_date_from_string(date_string)
    return Balance(account=account, date=date, balance=balance)

def capitalone_transaction_charged(data):
    lines = data.splitlines()
    txn_block_header = (
        "As requested, we're notifying you of a transaction that was charged "
        "to your Capital One Mastercard account.")
    txn_block = lines[lines.index(txn_block_header) + 2:lines.index(txn_block_header) + 5]
    return Transaction(
        id = None,
        account = get_capitalone_account(data),
        date = get_date_from_string(txn_block[0]),
        amount = get_amount_from_string(txn_block[2]),
        payee = txn_block[1],
        type = 'debit'
    )
