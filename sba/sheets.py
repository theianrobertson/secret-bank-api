import logging

class SheetsMixin:
    """A mixing to provide functionality for interacting with the Sheets API."""

    def write_transactions(self, transactions):
        """Write transaction(s) to the transaction backend

        Parameters
        ----------
        transactions: sba.Transaction or list of sba.Transaction
            An instance of the transaction data class, or a list of them.
        """
        if not isinstance(transactions, list):
            transactions = [transactions]
        row_to_write = self.first_empty_transaction_row()
        range_name = f'transactions!A{row_to_write}:I'
        value_range_body = {
            'range': range_name,
            'majorDimension': 'ROWS',
            'values': [transaction.to_sheets_values for transaction in transactions]
        }
        result = self.sheets_service.spreadsheets().values().update(
            spreadsheetId=self._transaction_backend_sheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=value_range_body).execute()

    def first_empty_transaction_row(self):
        """Get the first empty transaction row

        Returns
        -------
        int
            The first non-filled transaction row, based on a named range.
        """
        range_name = 'count_rows_in_transactions'
        result = self.sheets_service.spreadsheets().values().get(
            spreadsheetId=self._transaction_backend_sheet_id,
            range=range_name).execute()
        return int(result['values'][0][0]) + 1
