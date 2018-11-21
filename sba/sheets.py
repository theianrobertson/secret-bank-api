import logging

from sba.config import MAX_COLUMNS
from sba.transaction import Transaction, transaction_from_sheets_values
from sba.balance import Balance, balance_from_sheets_values

class SheetsMixin:
    """A mixing to provide functionality for interacting with the Sheets API."""

    def write_records(self, records, sheet):
        """Write record(s) to the transaction backend

        Parameters
        ----------
        records: sba.Balance/Transaction or list of them
            An instance of the balance/transaction data class, or a list of them.
        sheet: str, {transactions, balances}
            Which type of records these are.
        """
        if not isinstance(records, list):
            records = [records]
        row_to_write = self.first_empty_row(sheet)
        range_name = f"{sheet}!A{row_to_write}:{MAX_COLUMNS[sheet]}"
        value_range_body = {
            'range': range_name,
            'majorDimension': 'ROWS',
            'values': [record.to_sheets_values for record in records]
        }
        result = self.sheets_service.spreadsheets().values().update(
            spreadsheetId=self._transaction_backend_sheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=value_range_body).execute()

    def first_empty_row(self, sheet):
        """Get the first empty row, using the named range for that sheet.

        Parameters
        ----------
        sheet : str, {balances, transactions}

        Returns
        -------
        int
            The first non-filled row in the sheet, based on a named range.
        """
        range_name = f'count_rows_in_{sheet}'
        result = self.sheets_service.spreadsheets().values().get(
            spreadsheetId=self._transaction_backend_sheet_id,
            range=range_name).execute()
        return int(result['values'][0][0]) + 1

    def get_records(self, sheet):
        """Reads rows from a sheet, returning a list of objects

        Parameters
        ----------
        sheet : str, {balances, transactions}

        Returns
        -------
        list
        """
        last_filled_row = self.first_empty_row(sheet) - 1
        range_name = f"{sheet}!A2:{MAX_COLUMNS[sheet]}{last_filled_row}"
        result = self.sheets_service.spreadsheets().values().get(
            spreadsheetId=self._transaction_backend_sheet_id,
            range=range_name).execute()
        if sheet == 'transactions':
            return [transaction_from_sheets_values(values) for values in result['values']]
        else:
            return [balance_from_sheets_values(values) for values in result['values']]
