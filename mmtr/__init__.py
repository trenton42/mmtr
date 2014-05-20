#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Trenton Broughton'
__email__ = 'trenton@ikso.us'
__version__ = '0.2.0'

from mmtr import config


def configure(host=None, port=None, user=None,
              password=None, database=None, collection=None):
    _configuration.update(host=host,
                          port=port,
                          user=user,
                          password=password,
                          database=database,
                          collection=collection)

_configuration = config.Config()
