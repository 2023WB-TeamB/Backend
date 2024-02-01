import requests
import base64
import environ
from openai import OpenAI

import time
from collections import deque

env = environ.Env(DEBUG=(bool, True))
GITHUB_TOKEN = env('GITHUB_TOKEN')
GITHUB_BEARER_HEADERS = {'Authorization': f'Bearer {GITHUB_TOKEN}'}
GITHUB_TOKEN_HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}
GPT_SECRET_KEY = env('GPT_SECRET_KEY')
FRAMEWORK_ASSISTANT_ID = env('FRAMEWORK_ASSISTANT_ID')
ENG_CODE_ASSISTANT_ID = env('ENG_CODE_ASSISTANT_ID')
KOR_CODE_ASSISTANT_ID = env('KOR_CODE_ASSISTANT_ID')
ENG_TITLE_ASSISTANT_ID = env('ENG_TITLE_ASSISTANT_ID')
KOR_TITLE_ASSISTANT_ID = env('KOR_TITLE_ASSISTANT_ID')

ignore_file = [
    ".gitignore", ".idea", ".vscode", "__init__.py", "migrations", "manage.py", "asgi.py",
    "wsgi.py", "tests.py", "admin.py", "apps.py", "gradle", "gradlew", "gradlew.bat", "settings.gradle"
]

image_file = [".svg", ".png", ".jpg", ".gif", ".sql", ".ini", ".in", ".md", "cfg", "d.ts", "d.js", "d.jsx", "d.tsx", ]


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
                result += display_only_directory_structure(nested_structure, owner=owner, repo=repo,
                                                           indent=indent + "\t")
    return result

def max_elements_subset_indices(arr):
    max_sum = 31000
    dp = [[0, []] for _ in range(max_sum+1)]
    for i in range(len(arr)):
        for j in range(max_sum, arr[i]-1, -1):
            if j-arr[i] >= 0 and dp[j][0] < dp[j-arr[i]][0] + 1:
                dp[j][0] = dp[j-arr[i]][0] + 1
                dp[j][1] = dp[j-arr[i]][1] + [i]

    return dp[max_sum][1]


def framework_finder(url, root_file):
    if url.startswith("https://"):
        url = url.replace("https://", "")

    repo_url_list = url.split("/")
    owner = repo_url_list[1]
    repo = repo_url_list[2].split(".")[0]

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

    while run.status == "queued" or run.status == "in_progress":
        run = framework_assistant_client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id,
        )
        time.sleep(5)

    if run.status == "failed":
        return "failed"

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

            if element['type'] == "dir":
                nested_structure = get_file_content(owner, repo, element['path'])
                if nested_structure:
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

                elif (framework == "React" or framework == "React Native") and element['path'].startswith("src/pages/") and (
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

                elif framework == ("Fiber" or "Go gin" or "Golang" or "Go Kit" or "Echo") and (
                        element['path'].endswith("main.go") or
                        element['path'].startswith("models/") or
                        element['path'].endswith("model.go") or
                        element['path'].startswith("middleware/") or
                        element['path'].startswith("handlers/") or
                        element['path'].startswith("domain/") or
                        element['path'].startswith("controllers/")):
                    file_content = get_file_content(owner, repo, element['path'])
                    if 'content' in file_content:
                        decoded_content = base64.b64decode(file_content['content']).decode('utf-8')
                        current_element['content'] = decoded_content
                        data_prmp.append(current_element)

                elif framework == "Svelte" and (
                        element['path'].endswith(".svelte") or
                        element['path'].startswith("components/") or
                        element['path'].endswith("package.json") or
                        element['path'].endswith("rollup.config.js") or
                        element['path'].endswith("webpack.config.js") or
                        element['path'].endswith("App.svelte")):
                    file_content = get_file_content(owner, repo, element['path'])
                    if 'content' in file_content:
                        decoded_content = base64.b64decode(file_content['content']).decode('utf-8')
                        current_element['content'] = decoded_content
                        data_prmp.append(current_element)

                elif framework == "Ktor" and (element['path'].startswith("src/main/kotlin") or
                                              element['path'].endswith("build.gradle.kts")):
                    file_content = get_file_content(owner, repo, element['path'])
                    if 'content' in file_content:
                        decoded_content = base64.b64decode(file_content['content']).decode('utf-8')
                        current_element['content'] = decoded_content
                        data_prmp.append(current_element)

                elif framework == "Angular" and (
                        element['path'].startswith("api/") or
                        element['path'].endswith("index.html")):
                    file_content = get_file_content(owner, repo, element['path'])
                    if 'content' in file_content:
                        decoded_content = base64.b64decode(file_content['content']).decode('utf-8')
                        current_element['content'] = decoded_content
                        data_prmp.append(current_element)

                elif framework == ("Nodejs" or "Next.js") and (
                        element['path'].endswith(".js") or
                        element['path'].endswith("package.json")):
                    file_content = get_file_content(owner, repo, element['path'])
                    if 'content' in file_content:
                        decoded_content = base64.b64decode(file_content['content']).decode('utf-8')
                        current_element['content'] = decoded_content
                        data_prmp.append(current_element)

                elif framework == "Flask" and (
                        element['path'].startswith("app/") or
                        element['path'].startswith("model/") or
                        element['path'].endswith("models.py")):
                    file_content = get_file_content(owner, repo, element['path'])
                    if 'content' in file_content:
                        decoded_content = base64.b64decode(file_content['content']).decode('utf-8')
                        current_element['content'] = decoded_content
                        data_prmp.append(current_element)

                elif framework == ("Vue.js" or "Vue Vuex") and (
                        element['path'].endswith(".vue") or
                        element['path'].endswith(".ts") or
                        element['path'].endswith("package.json")):
                    file_content = get_file_content(owner, repo, element['path'])
                    if 'content' in file_content:
                        decoded_content = base64.b64decode(file_content['content']).decode('utf-8')
                        current_element['content'] = decoded_content
                        data_prmp.append(current_element)

            result_structure.append(current_element)

        return result_structure

    # Repository에 파일이 있을 경우에만 데이터를 가져오도록 함 (삭제 X)
    if root_file:
        display_directory_structure(root_file)

    res_ary = []
    for data in data_prmp:
        content = data['content']

        # content가 31000자를 넘는 경우 slice하여 처리
        # Issue -> path: ~~, content: ~~ 형식에 맞춰서 출력하려다 보니 합쳐지는 파일이 많으면 메세지가 너무 길어짐
        if len(content) > 31000:
            msg1 = f"path: {data['path']}\ncontent(1): {data['content'][:31000]}"
            msg2 = f"path: {data['path']}\ncontent(2): {data['content'][31000:]}"
            res_ary.append(msg1)
            res_ary.append(msg2)
        else:
            msg = f"path: {data['path']}\ncontent: {data['content']}"
            res_ary.append(msg)

    return res_ary


def get_title(content, language):
    code_assistant_client = OpenAI(api_key=GPT_SECRET_KEY)
    title_thread = code_assistant_client.beta.threads.create()
    title_thread_id = title_thread.id

    title_assistant_id = ENG_TITLE_ASSISTANT_ID
    if language == "KOR":
        title_assistant_id = KOR_TITLE_ASSISTANT_ID

    content_slice_list = slice_blog(content)

    for content_slice in content_slice_list:
        code_assistant_client.beta.threads.messages.create(
            title_thread_id,
            role="user",
            content=content_slice
        )

    run = code_assistant_client.beta.threads.runs.create(
        thread_id=title_thread_id,
        assistant_id=title_assistant_id
    )

    while run.status == "queued" or run.status == "in_progress":
        run = code_assistant_client.beta.threads.runs.retrieve(
            thread_id=title_thread_id,
            run_id=run.id
        )
        time.sleep(2)

    if run.status == "failed":
        return "failed", "failed", "failed"

    messages = code_assistant_client.beta.threads.messages.list(
        thread_id=title_thread_id
    )
    res_message = ""

    for message in messages:
        if message.role == 'assistant':
            res_message = message.content
            break

    res_title = res_message[0].text.value
    return res_title

def slice_blog(res_blog):
    slice_limit = 32000
    blog_parts = []

    # res_blog의 길이가 32000자 이하일 경우, 그대로 blog_parts에 추가
    if len(res_blog) <= slice_limit:
        blog_parts.append(res_blog)
    else:
        # res_blog의 길이가 32000자 이상일 경우, 32000자 단위로 분할하여 blog_parts에 추가
        for i in range(0, len(res_blog), slice_limit):
            blog_parts.append(res_blog[i:i+slice_limit])

    return blog_parts


def get_assistant_response(prompt_ary, language):
    code_assistant_client = OpenAI(api_key=GPT_SECRET_KEY)
    code_thread = code_assistant_client.beta.threads.create()
    content_thread_id = code_thread.id

    assistant_id = ENG_CODE_ASSISTANT_ID
    if language == "KOR":
        assistant_id = KOR_CODE_ASSISTANT_ID

    while True:
        arr = [len(p) for p in prompt_ary]
        arr_len = len(arr)

        if arr_len <= 1:
            break

        combine_index = max_elements_subset_indices(arr)

        if not prompt_ary:
            break

        combine_message = "\n\n".join(prompt_ary[i] for i in combine_index)

        combine_index_set = set(combine_index)
        prompt_ary = [prompt_ary[i] for i in range(arr_len) if i not in combine_index_set]
        code_assistant_client.beta.threads.messages.create(
            content_thread_id,
            role="user",
            content=combine_message
        )

    if len(arr) == 1:
        code_assistant_client.beta.threads.messages.create(
            content_thread_id,
            role="user",
            content=prompt_ary[0]
        )

    run = code_assistant_client.beta.threads.runs.create(
        thread_id=content_thread_id,
        assistant_id=assistant_id
    )

    while run.status == "queued" or run.status == "in_progress":
        run = code_assistant_client.beta.threads.runs.retrieve(
            thread_id=content_thread_id,
            run_id=run.id
        )
        time.sleep(2)

    if run.status == "failed":
        return "failed", "failed", "failed"

    messages = code_assistant_client.beta.threads.messages.list(
        thread_id=content_thread_id
    )

    res_message = ""

    for message in messages:
        if message.role == 'assistant':
            res_message = message.content

    res_blog = res_message[0].text.value
    res_tech_stack = []
    res_title = get_title(res_blog, language)

    return res_blog, res_tech_stack, res_title, content_thread_id


def get_github_latest_sha(url):
    if url.startswith("https://"):
        url = url.replace("https://", "")

    repo_url_list = url.split("/")
    owner = repo_url_list[1]
    repo = repo_url_list[2].split(".")[0]

    url = f'https://api.github.com/repos/{owner}/{repo}'
    response = requests.get(url, headers=GITHUB_TOKEN_HEADERS)

    if response.status_code == 200:
        default_branch = response.json()['default_branch']
    else:
        return "failed"

    url = f'https://api.github.com/repos/{owner}/{repo}/commits?sha={default_branch}'
    response = requests.get(url, headers=GITHUB_TOKEN_HEADERS)

    if response.status_code == 200:
        return response.json()[0]['sha']
    else:
        return "failed"


def assistant_run(language, thread):
    assistant_client = OpenAI(api_key=GPT_SECRET_KEY)
    thread_id = thread
    assistant_id = ENG_CODE_ASSISTANT_ID
    if language == "KOR":
        assistant_id = KOR_CODE_ASSISTANT_ID

    try:
        messages = assistant_client.beta.threads.messages.list(
            thread_id=thread_id
        )
    except Exception as e:
        return "not found thread"

    new_thread = assistant_client.beta.threads.create()

    for message in messages:
        if message.role == 'user':
            assistant_client.beta.threads.messages.create(
                new_thread.id,
                role="user",
                content=message.content[0].text.value
            )

    run = assistant_client.beta.threads.runs.create(
        thread_id=new_thread.id,
        assistant_id=assistant_id
    )

    while run.status == "queued" or run.status == "in_progress":
        run = assistant_client.beta.threads.runs.retrieve(
            thread_id=new_thread.id,
            run_id=run.id
        )
        time.sleep(1)

    if run.status == "failed":
        return "failed"

    messages = assistant_client.beta.threads.messages.list(
        thread_id=new_thread.id
    )

    res_message = ""

    for message in messages:
        if message.role == 'assistant':
            res_message = message.content

    result = res_message[0].text.value
    return result

def get_contributors(user, repo):
    url = f"https://api.github.com/repos/{user}/{repo}/contributors"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return [contributor['login'] for contributor in data]
