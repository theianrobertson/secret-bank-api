# 🤫 Secret Bank API 🤫

I read [this post](http://gduverger.com/secret-api-banks) and thought I could put something together
instead of mucking about with Plaid or some other third part that could keep my credentials.

Uses Google APIs to ping a personal Google API account.  You need `credentials.json`, and this will
walk through setting up `token.json` one time.

## Installation

Just handle it k

## Use

```python
import sba

gmail = sba.GMail()
gmail.catch_em_all()
```
