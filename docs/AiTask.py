import time

from gtd.celery import *
from gtd.settings import *
from .github import *
import logging


@app.task(name='framework_finder_task')
def framework_finder_task(repository_url, root_file):
    framework = framework_finder(repository_url, root_file)
    return framework


@app.task(name='get_assistant_response_task')
def get_assistant_response_task(prompt_ary, language):
    response, stack, res_title, thread_id = get_assistant_response(prompt_ary, language)

    if response == "failed":
        return response

    data = {
        "response": response,
        "stack": stack,
        "res_title": res_title,
        "thread_id": thread_id
    }

    return data
