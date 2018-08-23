from setuptools import setup, find_packages
import os
import sys

exec(open("secret-bank-api/_version.py").read())

INSTALL_REQUIRES = [
    "google-api-python-client",
    "oauth2client",
    "pyyaml",
]

setup(
    name="secret-bank-api",
    version=__version__,
    description="Secret Bank API",
    long_description="Seeeecret Baaaank API",
    url="https://github.com/theianrobertson/secret-bank-api",
    license="MIT",
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    package_data={"": ["*.yaml"]},
    zip_safe=False,
)
