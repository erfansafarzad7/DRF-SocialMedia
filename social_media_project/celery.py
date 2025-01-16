from __future__ import absolute_import, unicode_literals
import os
import django
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media_project.settings')
django.setup()

app = Celery('social_media_project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from installed apps
app.autodiscover_tasks()

app.conf.update(
    worker_pool='solo'  # or prefork
)


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
