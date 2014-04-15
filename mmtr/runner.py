#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fnmatch
import re
import time
from pymongo import MongoClient
from mmtr import _configuration


class Runner(object):

    JOB_EVENT = 0
    JOB_TASK = 1
    STATUS_NEW = 0
    STATUS_PROCESSING = 1
    STATUS_COMPLETE = 2
    STATUS_FAILED = 3

    def __init__(self, config=None):
        self.config = config or _configuration
        self.collection = None
        self.tasks = []
        self.running = True

    def connect(self):
        ''' Connect to the database server with the parameters set in
        self.config
        '''
        con = MongoClient(self.config.host, self.config.port)
        database = con[self.config.database]
        self.collection = database[self.config.collection]

    def run(self):
        ''' Start running and polling for events to handle '''
        if not self.tasks:
            print "No tasks added. Exiting."
            return 1
        self.connect()
        query = self._build_query()
        while self.running:
            task = self.get_task(query)
            if task:
                to_run = filter(lambda k: re.match(k['pattern'],
                                task['event']), self.tasks)
                for i in to_run:
                    self.process_task(i['callback'], task)
                time.sleep(10)
            else:
                time.sleep(15)

    def get_task(self, query):
        ''' Get the next task from the database (if any) '''
        update = {'$set': {'status': self.STATUS_PROCESSING}}
        res = self.collection.find_and_modify(query=query,
                                              update=update,
                                              new=True)
        return res

    def process_task(self, runner, task):
        ''' Run each task that matches the event pattern '''
        try:
            results = runner(task)
        except Exception as err:
            data = {'$set': {
                'status': self.STATUS_FAILED,
                'error': str(err)
            }}
            self.collection.update({'_id': task['_id']}, data)
            return
        data = {'$set': {
            'status': self.STATUS_COMPLETE,
            'results': results
        }}

    def _build_query(self):
        ''' Build an event query from the added tasks '''
        query = []
        for i in self.tasks:
            query.append({'event': i['pattern']})
        return {'$or': query, 'status': self.STATUS_NEW}

    def add_task(self, callback, event, job_type=None):
        ''' Add a task callback to the event watching queue '''
        if not callable(callback):
            raise TypeError("{} is not callable".format(callback))

        if job_type is None:
            job_type = self.JOB_TASK
        if job_type not in [self.JOB_TASK, self.JOB_EVENT]:
            msg = "job_type must be one of 0, 1 not {}".format(job_type)
            raise KeyError(msg)

        pattern = fnmatch.translate(event)
        match = re.compile(pattern, re.IGNORECASE)

        task = {
            "callback": callback,
            "event": event,
            "pattern": match,
            "job_type": job_type
        }
        self.tasks.append(task)
