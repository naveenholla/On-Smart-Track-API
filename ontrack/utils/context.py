import logging
import time
import uuid
from collections import deque
from contextlib import contextmanager

from django.core.cache import cache


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
    correlationid = get_correlation_id()
    application_context_handler.add(correlationid=correlationid)
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


LOCK_EXPIRE = 60 * 10  # Lock expires in 10 minutes


@contextmanager
def memcache_lock(lock_id, oid):
    timeout_at = time.monotonic() + LOCK_EXPIRE - 3
    # cache.add fails if the key already exists
    status = cache.add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
    finally:
        # memcache delete is very slow, but we have to use it to take
        # advantage of using add() for atomic locking
        if time.monotonic() < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else
            # also don't release the lock if we didn't acquire it
            cache.delete(lock_id)
