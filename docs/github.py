import requests
import base64
import environ
from openai import OpenAI

env = environ.Env(DEBUG=(bool, True))
GITHUB_TOKEN = env('GITHUB_TOKEN')
GITHUB_BEARER_HEADERS = {'Authorization': f'Bearer {GITHUB_TOKEN}'}
GITHUB_TOKEN_HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}
GPT_SECRET_KEY = env('GPT_SECRET_KEY')
FRAMEWORK_ASSISTANT_ID = env('FRAMEWORK_ASSISTANT_ID')


ignore_file = [
    ".gitignore", ".idea", ".vscode", "README.md", "__init__.py", "migrations", "manage.py", "asgi.py",
    "wsgi.py", "tests.py", "admin.py", "apps.py", "gradle", "gradlew", "gradlew.bat", "settings.gradle"
]

image_file = [".svg", ".png", ".jpg", ".gif", ".sql", ".ini", ".in", ".md", "cfg"]


def url_validator(url):
    try:
        result = requests.get(url)
        return result.status_code == 200
    except:
        return False


def get_file_content(owner, repo, path):
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
    response = requests.get(url, headers=GITHUB_TOKEN_HEADERS)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"에러: {response.status_code}")


def display_only_directory_structure(file_structure, owner, repo, indent=""):
    result = ""
    for element in file_structure:
        if element['name'] in ignore_file:
            continue

        result += f"{indent}-{element['name']} ({element['type']})\n"

        if element['type'] == "dir":
            nested_structure = get_file_content(owner, repo, element['path'])
            if nested_structure:
                result += display_only_directory_structure(nested_structure, owner=owner, repo=repo, indent=indent + "\t")
    return result


def framework_finder(url):
    if url.startswith("https://"):
        url = url.replace("https://", "")

    repo_url_list = url.split("/")
    owner = repo_url_list[1]
    repo = repo_url_list[2].split(".")[0]
    path = ''
    root_file = get_file_content(owner, repo, path)

    structure = display_only_directory_structure(root_file, owner=owner, repo=repo)

    framework_assistant_client = OpenAI(api_key=GPT_SECRET_KEY)
    framework_thread = framework_assistant_client.beta.threads.create()
    thread_id = framework_thread.id

    framework_assistant_client.beta.threads.messages.create(
        thread_id,
        role="user",
        content=structure
    )

    run = framework_assistant_client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=FRAMEWORK_ASSISTANT_ID,
    )

    while run.status != "completed":
        run = framework_assistant_client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id,
        )

    messages = framework_assistant_client.beta.threads.messages.list(
        thread_id=thread_id,
    )

    res_message = ""
    for message in messages:
        if message.role == 'assistant':
            res_message = message.content

    return res_message[0].text.value
