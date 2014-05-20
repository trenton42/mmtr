#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import pika
import json
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
        self.channel = None

    def connect(self):
        ''' Connect to the database server with the parameters set in
        self.config
        '''
        credentials = pika.PlainCredentials(_configuration.user, _configuration.password)
        con = pika.ConnectionParameters(host=_configuration.host,
                                        credentials=credentials)
        connection = pika.BlockingConnection(con)
        self.channel = connection.channel()

        self.channel.exchange_declare(exchange='mmtr_runner',
                                      type='topic')

        result = self.channel.queue_declare(_configuration.queue)
        queue_name = result.method.queue

        for task in self.tasks:
            binding_key = task['event']
            self.channel.queue_bind(exchange='mmtr_runner',
                                    queue=queue_name,
                                    routing_key=binding_key)
        self.channel.basic_consume(self.task_callback,
                                   queue=queue_name,
                                   no_ack=False)
        print "Ready"
        self.channel.start_consuming()

    def run(self):
        ''' Start running and polling for events to handle '''
        if not self.tasks:
            print "No tasks added. Exiting."
            return 1
        self.connect()

    def task_callback(self, ch, method, properties, body):
        ''' Respond to a task from the queue '''
        to_run = filter(lambda k: re.match(k['pattern'],
                        method.routing_key), self.tasks)

        try:
            data = json.loads(body)
        except:
            return
        task = {'method': method, 'properties': properties}
        self.process_tasks(to_run, task, data)

    def process_tasks(self, runners, task, data):
        ''' Run each task that matches the event pattern '''
        all_results = []
        passed_data = data.pop('data', {})
        for i in runners:
            res = {
                'callback': i['callback'].__name__,
                'status': None,
                'result': None
            }
            runner = i['callback']
            try:
                results = runner(passed_data, **data)
            except Exception as err:
                res['status'] = self.STATUS_FAILED
                res['result'] = str(err)
            else:
                res['status'] = self.STATUS_COMPLETE
                res['result'] = results
            if res['result'] is not None:
                all_results.append(res)
        if task['properties'].reply_to:
            try:
                body = json.dumps(all_results)
            except:
                body = '[]'

            props = task['properties']
            self.channel.basic_publish(exchange='',
                                       routing_key=props.reply_to,
                                       properties=pika.BasicProperties(correlation_id=props.correlation_id),
                                       body=body)
            print task['method'].delivery_tag
        self.channel.basic_ack(delivery_tag=task['method'].delivery_tag)

    def _check_pattern(self, pattern):
        ''' Check that a pattern is a valid routing key '''
        if re.findall('[^a-zA-Z0-9.#*]', pattern):
            raise ValueError('Pattern must only contain a-zA-Z0-9.#*')
        tmp = pattern.split('.')
        matches = filter(lambda k: ('*' in k or '#' in k) and len(k) > 1, tmp)
        if matches:
            raise ValueError('# or * must only be used alone in a word')
        out = pattern.replace('.', '\.')
        out = out.replace('*', '[a-zA-Z0-9]+')
        out = out.replace('#', '[a-zA-Z0-9.]*')
        return re.compile('^' + out + '$')

    def add_task(self, callback, event, job_type=None):
        ''' Add a task callback to the event watching queue '''
        if not callable(callback):
            raise TypeError("{} is not callable".format(callback))

        if job_type is None:
            job_type = self.JOB_TASK
        if job_type not in [self.JOB_TASK, self.JOB_EVENT]:
            msg = "job_type must be one of 0, 1 not {}".format(job_type)
            raise KeyError(msg)

        match = self._check_pattern(event)

        task = {
            "callback": callback,
            "event": event,
            "pattern": match,
            "job_type": job_type
        }
        self.tasks.append(task)
