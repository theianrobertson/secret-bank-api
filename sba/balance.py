from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass
from sba import config

@dataclass
class Balance:
    account: str
    date: datetime
    balance: Decimal

    @property
    def account_description(self):
        return config.account_lookup()[self.account]

    @property
    def to_sheets_values(self):
        return [
            self.account,
            self.account_description,
            self.date.strftime('%Y-%m-%d'),
            self.balance.to_eng_string()
        ]

def balance_from_sheets_values(values):
    """De-parse from sheets values.

    Parameters
    ----------
    values : list

    Returns
    -------
    Balance
    """
    return Balance(
        account=values[0],
        date=datetime.strptime(values[2], '%Y-%m-%d'),
        balance=Decimal(values[3])
    )
