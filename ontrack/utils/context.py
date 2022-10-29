import logging
import uuid
from collections import deque
from contextlib import contextmanager


class ApplicationContextHandler:
    def __init__(self):
        self.attributes = deque([{}])

    def add(self, **new_context_vars):
        old_context = self.attributes[0]
        new_context = {**old_context, **new_context_vars}
        self.attributes.appendleft(new_context)

    def get(self, key):
        return self.attributes[0].get(key)

    def remove(self):
        self.attributes.popleft()

    def __str__(self):
        return str(self.attributes)


application_context_handler = ApplicationContextHandler()


@contextmanager
def application_context(**kwargs):
    application_context_handler.add(**kwargs)

    yield

    application_context_handler.remove()


def get_correlation_id():
    try:
        from celery._state import get_current_task

        task = get_current_task()
        if task and task.request:
            return task.request.id
        return uuid.uuid4().hex
    except Exception:
        return uuid.uuid4().hex


def get_context_value_by_key(key):
    return application_context_handler.get(key)


class ContextFilter(logging.Filter):
    def __init__(self):
        super().__init__()

    def filter(self, record):
        record.correlationid = get_context_value_by_key("correlationid")
        record.userid = get_context_value_by_key("userid")

        return True
