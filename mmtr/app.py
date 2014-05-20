#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wrapt
import functools
import signal
from mmtr import runner

_current_app = runner.Runner()


def task(wrapped=None, event=None):
    if wrapped is None:
        return functools.partial(task, event=event)

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        body = args[0]
        response = wrapped(body, **kwargs)
        return response

    out = wrapper(wrapped)
    _current_app.add_task(out, event)
    return out


def _stop(*args):
    _current_app.running = False


signal.signal(signal.SIGINT, _stop)
signal.signal(signal.SIGTERM, _stop)
run = _current_app.run
