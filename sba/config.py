from functools import lru_cache

import yaml

DEFAULT_PATH = 'config.yml'
MAX_COLUMNS = {'transactions': 'I', 'balances': 'D'}

@lru_cache()
def load_config(config=DEFAULT_PATH):
    """Load from a config file

    Parameters
    ----------
    config : str
        File name of the config file.  Defaults to config.yml in the current working directory.
    """
    with open(config) as file_open:
        return yaml.load(file_open)

def account_lookup(config=DEFAULT_PATH):
    return load_config(config)['account_lookup']

def categories(config=DEFAULT_PATH):
    return load_config(config)['categories']

def transaction_backend_sheet_id(config=DEFAULT_PATH):
    return load_config(config)['transaction_backend_sheet_id']
