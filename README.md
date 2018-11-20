# 🤫 Secret Bank API 🤫

I read [this post](http://gduverger.com/secret-api-banks) and thought I could put something together
instead of mucking about with Plaid or some other third part that could keep my credentials.

This project uses Google APIs to grab emails and write things to a sheets backend.  It's very much
a work in progress.  Please feel free to poke around!

## Installation

1. You'll need Python 3.7+
2. Clone this repo
3. `pip install -r requirements.txt`, probably into a virtualenv or conda env.
4. Enable the Google sheets and gmail APIs.  Check out [this reference](https://developers.google.com/sheets/api/quickstart/python)
   for an example of how to do it for the sheets API.  You'll want both on the same project.
5. Save the resulting `credentials.json` file where you're running this stuff.  The code will create
   a `token.json` file in the same directory when authorizing.
6. Create a `config.yml` file in the directory where you're running.  The yaml file looks like as
   follows, where the SOME_LONG_ID is from the transaction backend sheet URL like
   `https://docs.google.com/spreadsheets/d/SOME_LONG_ID/edit#gid=0`:
   ```yaml
   transaction_backend_sheet_id: SOME_LONG_ID
   ```
7. The transaction backend sheet needs a few things:
   - A cell with a single field with function `=COUNTA(transactions!A1:A)` in it, named as
     `count_rows_in_transactions`
   - A cell with a single field with function `=COUNTA(balances!A1:A)` in it, named as
     `count_rows_in_balances`
   - A sheet called `transactions` where your transactions will go.  With headers in the first row:
     - id
     - account
     - account_description
     - date
     - amount
     - payee
     - type
     - category
     - month
   - A sheet called `balances`, where your balances will go.  Headers in the first row:
     - account
     - account_description
     - date
     - balance

## Using the library

```python
from sba import Google, Transaction

#Initialize the object that connects to Google
google = Google()

#Grab all emails and save locally
google.catch_em_all()

#Write a transaction to sheets backend
tran = Transaction(
    id='some_transaction_id',
    account='123456',
    date=datetime(2018, 1, 6),
    amount=Decimal('12.14'),
    payee='A shadowy figure',
    type='debit')

google.write_records(tran, 'transactions') #You can also pass a list of transactions
```
