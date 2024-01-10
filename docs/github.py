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
CODE_ASSISTANT_ID = env('CODE_ASSISTANT_ID')


ignore_file = [
    ".gitignore", ".idea", ".vscode", "__init__.py", "migrations", "manage.py", "asgi.py",
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


def get_github_code_prompt(url, framework):

    data_prmp = []

    if url.startswith("https://"):
        url = url.replace("https://", "")

    repo_url_list = url.split("/")
    owner = repo_url_list[1]
    repo = repo_url_list[2].split(".")[0]
    path = ''
    root_file = get_file_content(owner, repo, path)


    ###########################################################################################################################
    ###########################################################################################################################
    ###########################################################################################################################

    def display_directory_structure(file_structure):

        result_structure = []
        for element in file_structure:
            # 무시할 파일이면 건너뛰기
            if element['name'] in ignore_file:
                continue

            current_element = {'name': element['name'], 'type': element['type'], 'path': element['path']}

            isImage = False
            for file_extension in image_file:
                if element['name'].find(file_extension) != -1:
                    isImage = True
                    continue

            if isImage:
                continue

            # 디렉토리인 경우 내부 구조 출력
            if element['type'] == "dir":
                nested_structure = get_file_content(owner, repo, element['path'])
                if nested_structure:
                    # 재귀적으로 디렉토리 구조를 child에 저장
                    current_element['child'] = display_directory_structure(nested_structure)

            elif element['type'] == "file":
                if framework == "Django" and (element['path'].endswith("views.py") or
                                              element['path'].endswith("models.py") or
                                              element['path'].endswith("settings.py") or
                                              element['path'].endswith("README.md") or
                                              element['path'].endswith("serializers.py")):
                    file_content = get_file_content(owner, repo, element['path'])
                    if 'content' in file_content:
                        decoded_content = base64.b64decode(file_content['content']).decode('utf-8')
                        current_element['content'] = decoded_content
                        data_prmp.append(current_element)

                elif framework == "React" and element['path'].startswith("src/") and (
                        element['path'].endswith(".ts") or
                        element['path'].endswith(".tsx") or
                        element['path'].endswith(".js") or
                        element['path'].endswith("package.json") or
                        element['path'].endswith(".jsx")):
                    file_content = get_file_content(owner, repo, element['path'])
                    if 'content' in file_content:
                        decoded_content = base64.b64decode(file_content['content']).decode('utf-8')
                        current_element['content'] = decoded_content
                        data_prmp.append(current_element)

                elif framework == "Spring Boot" and (element['path'].startswith("src/main/java") or
                                                     element['path'].endswith("build.gradle")):
                    file_content = get_file_content(owner, repo, element['path'])
                    if 'content' in file_content:
                        decoded_content = base64.b64decode(file_content['content']).decode('utf-8')
                        current_element['content'] = decoded_content
                        data_prmp.append(current_element)

            result_structure.append(current_element)
        return result_structure

    ###########################################################################################################################
    ###########################################################################################################################
    ###########################################################################################################################

    if root_file:
        formatted_structure1 = display_directory_structure(root_file)

    res_ary = []
    for data in data_prmp:
        msg = f"path: {data['path']}\ncontent: {data['content']}"
        # commit_assistant_client.beta.threads.messages.create(
        #     thread_id,
        #     role="user",
        #     content=msg
        # )

    return res_ary


def get_assistant_response(prompt_ary):
    code_assistant_client = OpenAI(api_key=GPT_SECRET_KEY)
    code_thread = code_assistant_client.beta.threads.create()
    thread_id = code_thread.id

    for prompt in prompt_ary:
        code_assistant_client.beta.threads.messages.create(
            thread_id,
            role="user",
            content=prompt
        )

    run = code_assistant_client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=CODE_ASSISTANT_ID
    )

    while run.status != "completed":
        run = code_assistant_client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )

    messages = code_assistant_client.beta.threads.messages.list(
        thread_id=thread_id
    )

    res_message = ""

    for message in messages:
        if message.role == 'assistant':
            res_message = message.content

    return res_message[0].text.value
