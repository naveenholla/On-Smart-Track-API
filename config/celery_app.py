import os

# from opentelemetry.instrumentation.celery import CeleryInstrumentor
from celery import Celery

# from celery.signals import worker_process_init

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

# @worker_process_init.connect(weak=False)
# def init_celery_tracing(*args, **kwargs):
#     CeleryInstrumentor().instrument()

app = Celery("ontrack")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
