#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Config(object):

    def __init__(self, database=None, collection=None, host=None,
                 port=None, user=None, password=None):
        ''' Create a new configuration object '''
        self.host = host or "localhost"
        self.port = port or 27017
        self.user = user
        self.password = password
        self.database = database or "mmtrevents"
        self.collection = collection or "Event"

    def update(self, **kwargs):
        ''' Update already set configuration, ignoring kwargs that are
        None or are not configuration values we are interested in.
        '''
        for i in ('host', 'port', 'user', 'password', 'database', 'collection'):
            if i not in kwargs or kwargs[i] is None:
                continue
            setattr(self, i, kwargs[i])
