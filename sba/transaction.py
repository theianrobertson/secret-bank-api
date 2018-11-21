from collections import namedtuple
from functools import lru_cache
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import re
import logging

from ofxparse import OfxParser

from sba import config

LOG = logging.getLogger(__name__)

Categorizer = namedtuple('Categorizer', ['category', 'matcher'])

@lru_cache()
def load_categorizers():
    """Load transaction categorizers from config file
    """
    all_categorizers = []
    for category, list_items in config.categories().items():
        for list_item in list_items:
            LOG.debug('Parsing {}'.format(list_item))
            all_categorizers.append(Categorizer(category, categorizer_from_config_entry(list_item)))
    return all_categorizers

def categorizer_from_config_entry(config_entry):
    """Load a list into a categorizer

    Parameters
    ----------
    config_entry : str or dict
        An item from the config file where entries are either strings or dicts

    Returns
    -------
    function
        A function which returns true if a transaction matches that category.
    """
    if isinstance(config_entry, str):
        compiled = re.compile(config_entry)
        return lambda transaction: bool(re.match(compiled, transaction.payee))
    elif isinstance(config_entry, dict):
        matchers = []
        if 'payee' in config_entry:
            compiled = re.compile(config_entry.pop('payee'))
            matchers.append(lambda transaction: bool(re.match(compiled, transaction.payee)))
        if 'amount' in config_entry:
            decimal_amount = Decimal(config_entry.pop('amount'))
            matchers.append(lambda transaction: transaction.amount == decimal_amount)
        for key, value in config_entry.items():
            matchers.append(lambda transaction: getattr(transaction, key) == value)
        return lambda transaction: all(matcher(transaction) for matcher in matchers)
    else:
        raise ValueError('config_entry must be a string or dict')


@dataclass
class Transaction:
    id: str
    account: str
    date: datetime
    amount: Decimal
    payee: str
    type: str
    _category: str = ''

    @property
    def month(self):
        return self.date.strftime('%Y-%m')

    @property
    def account_description(self):
        return config.account_lookup()[self.account]

    @property
    def category(self):
        return self._category or get_category(self)

    @property
    def to_sheets_values(self):
        return [
            self.id,
            self.account,
            self.account_description,
            self.date.strftime('%Y-%m-%d'),
            self.amount.to_eng_string(),
            self.payee,
            self.type,
            self.category,
            self.month
        ]

def from_qfx(filename):
    """Load a QFX file into a list of transactions"""
    with open(filename) as file_open:
        ofx = OfxParser.parse(file_open)
    LOG.info('parsing account: {}'.format(ofx.account.number))
    LOG.info('start_date: {}'.format(ofx.account.statement.start_date))
    LOG.info('end_date: {}'.format(ofx.account.statement.end_date))
    LOG.info('transaction count: {}'.format(len(ofx.account.statement.transactions)))
    LOG.info('balance: {}'.format(ofx.account.statement.balance))
    LOG.info('available_balance: {}'.format(ofx.account.statement.available_balance))
    return [
        Transaction(**filter_dict(txn.__dict__), account=ofx.account.number)
        for txn in ofx.account.statement.transactions]

def filter_dict(tran_dict):
    keys = ["id", "date", "amount", "payee", "type"]
    return {key: tran_dict[key] for key in keys}

def get_category(transaction):
    categorizers = load_categorizers()
    matches = set([cat.category for cat in categorizers if cat.matcher(transaction)])
    LOG.info('Matched {} for transaction {}'.format(matches, transaction))
    if len(matches) == 1:
        return matches.pop()
    return ''

def transaction_from_sheets_values(values):
    """De-parse from sheets values.

    Parameters
    ----------
    values : list

    Returns
    -------
    Transaction
    """
    return Transaction(
        id=values[0],
        account=values[1],
        date=datetime.strptime(values[3], '%Y-%m-%d'),
        amount=Decimal(values[4]),
        payee=values[5],
        type=values[6],
        _category=values[7]
    )
