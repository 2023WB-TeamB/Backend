import time

from gtd.celery import *
from gtd.settings import *

@app.task(name='delayed_task')
def delayed_task():
    time.sleep(30)
    return 'delayed_task'