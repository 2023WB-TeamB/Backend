from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.template import loader
from rest_framework.response import Response
from rest_framework import status

from .models import Badge
from .tech_stack_images import *

import requests
import json


# TODO: parameter가 너무 많아 나중에 Tuple로 묶어서 넘겨주는 방식으로 변경
def terminal1(request, github_user_organization, repo_name, github_user, repository_url, headers):

    # 뱃지에 등록된 데이터가 있는 경우
    if Badge.objects.filter(github_id=github_user, repository_url=repository_url).exists():
        badge = Badge.objects.get(github_id=github_user, repository_url=repository_url)

    else:
        try:
            result = requests.get(f"https://api.github.com/repos/{github_user_organization}/{repo_name}/contributors",
                                  headers=headers)
        except:
            return Response({'message': '유효한 레포지토리 URL을 입력해 주세요.', 'status': 404}, status=status.HTTP_404_NOT_FOUND)

        if result.status_code != 200:
            return Response({'message': '유효한 레포지토리 URL을 입력해 주세요.', 'status': 404}, status=status.HTTP_404_NOT_FOUND)

        contributors = json.loads(result.text)
        if not any(contributor['login'] == github_user for contributor in contributors):
            return Response({'message': f'{github_user}님은 {repo_name}에 Contributor로 등록되지 않았습니다.', 'status': 400},
                            status=status.HTTP_400_BAD_REQUEST)

        pr_response = requests.get(
            f"https://api.github.com/repos/{github_user_organization}/{repo_name}/pulls?state=all", headers=headers)

        if pr_response.status_code != 200:
            return Response({'message': 'GitHub API Server Error.', 'status': 500},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        #######################################################################################################

        pull_request_list = json.loads(pr_response.text)
        total_contributions = sum([contributor['contributions'] for contributor in contributors])
        result = []

        for contributor in contributors:
            user_prs = [pr for pr in pull_request_list if pr['user']['login'] == contributor['login']]
            contribution_percent = '{:.2f}%'.format((contributor['contributions'] / total_contributions) * 100)
            res_data = {
                'contributor': contributor['login'],
                'commit_count': contributor['contributions'],
                'contribution_percent': contribution_percent,
                'pr_count': len(user_prs),
            }
            # DataBase에 저장
            badge = Badge(github_id=res_data['contributor'],
                          commit_cnt=res_data['commit_count'],
                          pull_request_cnt=res_data['pr_count'],
                          contribution=res_data['contribution_percent'].strip("%"),
                          repository_url=repository_url)
            badge.save()
            result.append(res_data)

    # repository_url이 같은 badge데이터 가져오기
    contributor_user = Badge.objects.filter(github_id=github_user, repository_url=repository_url).get()
    contributors = Badge.objects.filter(repository_url=repository_url)
    percent = contributor_user.contribution / (100 * 1 / len(contributors))
    rank = "F"
    if percent >= 1.2:
        rank = "A"
    elif percent > 0.8:
        rank = "B"
    elif percent > 0.5:
        rank = "C"
    elif percent > 0.1:
        rank = "D"
    position = request.GET.get('position', "Devloper")

    template = loader.get_template('tag/terminal1.html')
    context = {
        'github_user': badge.github_id, 'repo_name': repo_name,
        'percent': badge.contribution, 'commits': badge.commit_cnt,
        'pull_requests': badge.pull_request_cnt, 'rank': rank,
        'position': position,
    }
    response = HttpResponse(content=template.render(context, request))
    return response


def card1(request, github_user_organization, repo_name, github_user, headers):
    try:
        result = requests.get(f"https://api.github.com/repos/{github_user_organization}/{repo_name}/contributors",
                              headers=headers)
    except:
        return Response({'message': '유효한 레포지토리 URL을 입력해 주세요.', 'status': 404}, status=status.HTTP_404_NOT_FOUND)

    if result.status_code != 200:
        return Response({'message': '유효한 레포지토리 URL을 입력해 주세요.', 'status': 404}, status=status.HTTP_404_NOT_FOUND)

    contributors = json.loads(result.text)
    if not any(contributor['login'] == github_user for contributor in contributors):
        return Response({'message': f'{github_user}님은 {repo_name}에 Contributor로 등록되지 않았습니다.', 'status': 400},
                        status=status.HTTP_400_BAD_REQUEST)

    contributor_list = []

    for contributor in contributors:
        data = {
            'contributor': contributor['login'],
            'avatar_url': contributor['avatar_url'],
        }
        contributor_list.append(data)

    template = loader.get_template('tag/card1.html')
    stack1 = request.GET.get('stack1', "")
    stack2 = request.GET.get('stack2', "")

    if get_tech_image(stack1) is False or get_tech_image(stack2) is False:
        return Response({'message': '유효한 기술 스택을 입력해 주세요.', 'status': 404}, status=status.HTTP_404_NOT_FOUND)

    contributor_len = len(contributor_list)
    context = {
        'organization': github_user_organization, 'repo_name': repo_name,
        'contributors': contributor_list, 'stack1': get_tech_image(stack1), 'stack2': get_tech_image(stack2),
        'first_contributor_avatar_url': contributor_list[0]['avatar_url'],
        'contributor_len': contributor_len,
        'start': request.data['start'], 'end': request.data['end'],
    }
    if len(contributor_list) > 1:
        context['second_contributor_avatar_url'] = contributor_list[1]['avatar_url']

    response = HttpResponse(content=template.render(context, request))
    return response


def terminal2(request, github_user_organization, repo_name, github_user, dark_light, headers):
    try:
        result = requests.get(f"https://api.github.com/repos/{github_user_organization}/{repo_name}/contributors",
                              headers=headers)
    except:
        return Response({'message': '유효한 레포지토리 URL을 입력해 주세요.', 'status': 404}, status=status.HTTP_404_NOT_FOUND)

    if result.status_code != 200:
        return Response({'message': '유효한 레포지토리 URL을 입력해 주세요.', 'status': 404}, status=status.HTTP_404_NOT_FOUND)

    contributors = json.loads(result.text)
    if not any(contributor['login'] == github_user for contributor in contributors):
        return Response({'message': f'{github_user}님은 {repo_name}에 Contributor로 등록되지 않았습니다.', 'status': 400},
                        status=status.HTTP_400_BAD_REQUEST)

    template = loader.get_template('tag/terminal2.html')
    stack1 = request.GET.get('stack1', "")
    stack2 = request.GET.get('stack2', "")

    context = {
        'organization': github_user_organization, 'repo_name': repo_name,
        'stack1': stack1, 'stack2': stack2, 'theme': dark_light,
        'start': request.data['start'], 'end': request.data['end'],
    }

    response = HttpResponse(content=template.render(context, request))
    return response