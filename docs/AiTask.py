import time

from gtd.celery import *
from gtd.settings import *
from .github import *


@app.task(name='delayed_task')
def delayed_task():
    time.sleep(30)
    return 'delayed_task'


@app.task(name='framework_finder_task')
def framework_finder_task(repository_url):
    framework = framework_finder(repository_url)
    return framework


@app.task(name='get_assistant_response_task')
def get_assistant_response_task(prompt_ary, language):
    response, stack, res_title = get_assistant_response(prompt_ary, language)

    if response == "failed":
        return response

    data = {
        "response": response,
        "stack": stack,
        "res_title": res_title
    }
    return data
