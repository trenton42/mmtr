#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='mmtr',
    version='0.1.0',
    description='Mongo based simple task runner',
    long_description=readme + '\n\n' + history,
    author='Trenton Broughton',
    author_email='trenton@ikso.us',
    url='https://github.com/trenton42/mmtr',
    packages=[
        'mmtr',
    ],
    package_dir={'mmtr': 'mmtr'},
    include_package_data=True,
    install_requires=[
        'pymongo',
        'wrapt'
    ],
    license="BSD",
    zip_safe=False,
    keywords='mmtr',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
)