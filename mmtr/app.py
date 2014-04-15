#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wrapt
import functools
from mmtr import runner

_current_app = runner.Runner()


def task(wrapped=None, event=None):
    if wrapped is None:
        return functools.partial(task, event=event)

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        body = args[0]
        response = wrapped(body)
        return response

    out = wrapper(wrapped)
    _current_app.add_task(out, event)
    return out

run = _current_app.run
