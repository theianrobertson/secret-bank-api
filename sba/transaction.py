from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass
class Transaction:
    id: str
    account: str
    account_description: str
    date: datetime
    amount: Decimal
    payee: str
    type: str
    category: str = ''

    @property
    def month(self):
        return self.date.strftime('%Y-%m')

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
