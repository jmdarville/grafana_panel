#!/usr/bin/env python3
from setuptools import find_packages, setup

setup(
    name='grafana-panels',
    version='0.0.1',
	description='Update Grafana panel thresholds from a google spreadsheet',
	author='jdarville',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'gspread',
        'oauth2client'
    ],
)
