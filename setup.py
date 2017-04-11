# -*- coding: utf-8 -*-
from setuptools import setup
setup(
    name='ProcAPI',
    packages=['procapi', 'tests'],
    test_suite='tests',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
