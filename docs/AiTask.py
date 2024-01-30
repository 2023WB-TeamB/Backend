import time

from gtd.celery import *
from gtd.settings import *
import logging

@app.task(name='framework_finder_task')
def framework_finder_task(repository_url, root_file):
    from .github import framework_finder
    framework = framework_finder(repository_url, root_file)
    return framework


@app.task(name='get_content_task')
def get_content_task(code_thread_id, language):
    from .github import get_content
    res_content = get_content(code_thread_id, language)
    return res_content


@app.task(name='get_title_task')
def get_title_task(content, language):
    from .github import get_title
    res_title = get_title(content, language)
    return res_title


@app.task(name='get_outline_task')
def get_outline_task(content, language):
    from .github import get_outline
    res_outline = get_outline(content, language)
    return res_outline


@app.task(name='get_tech_stack_task')
def get_tech_stack_task(code_thread_id, root_file):
    from .github import get_tech_stack
    res_tech_stack = get_tech_stack(code_thread_id, root_file)
    return res_tech_stack


@app.task(name='get_main_function_task')
def get_main_function_task(code_thread_id, root_file):
    from .github import get_main_function
    res_main_function = get_main_function(code_thread_id, root_file)
    return res_main_function


@app.task(name='get_core_algorithm_task')
def get_core_algorithm_task(code_thread_id, root_file):
    from .github import get_core_algorithm
    res_core_algorithm = get_core_algorithm(code_thread_id, root_file)
    return res_core_algorithm


def get_assistant_response_task(prompt_ary, language):
    from .github import get_assistant_response
    response, stack, res_title, thread_id = get_assistant_response(prompt_ary, language)

    if response == "failed":
        return response

    if res_title is None:
        res_title = "제목"

    data = {
        "response": response,
        "stack": stack,
        "res_title": res_title,
        "thread_id": thread_id
    }

    return data