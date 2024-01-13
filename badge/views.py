from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.template import loader

from .models import Badge

import environ
import requests
import json

class BadgeView(APIView):
    def get(self, request, github_user_organization, repo_name, github_user, *args, **kwargs):

        # TODO: github_user, repo_name 으로 문서화된 레포지토리가 있는지 확인
        # TODO: ! Docs ID 검색 후 badge filter까지 하면 로직이 하나 늘어나는거기 때문에 바로 badge filter로 검색
        # TODO: - 문서화된 레포지토리가 있으면(변경됨)
        # TODO: - - Docs Id와 연결된 badge db에서 repo_name과 github_user로 조회(변경됨)
        # TODO: - - badge db에서 repo_name과 github_user로 조회
        # TODO: - - data를 받아온 후 template에 넣어서 return

        # TODO: - 문서화된 레포지토리가 없으면
        # TODO: - - badge db에서 repo_name과 github_user로 조회
        # TODO: - - 정보가 있으면
        # TODO: - - - data를 받아온 후 template에 넣어서 return

        # TODO: - - 정보가 없으면
        # TODO: - - - Repository, github_user 분석 후 유효한 데이터 인 경우에 badge db에 저장
        # TODO: - - - data를 받아온 후 template에 넣어서 return (위쪽과 동일 로직 -> 함수로 빼기)

        # TODO: ! 닉네임을 변경한 경우? 어떻게 처리할지 고민할 것
        # TODO: ! 만약 이미 뱃지를 사용하던 유저가 문서화를 진행할 경우? -> 문서화 진행 시 뱃지 생성 -> 뱃지 업데이트

        env = environ.Env(DEBUG=(bool, True))
        GITHUB_TOKEN = env('GITHUB_TOKEN')
        headers = {'Authorization': 'token ' + GITHUB_TOKEN}

        repository_url = "https://github.com/" + github_user_organization + "/" + repo_name
        # 뱃지에 등록된 데이터가 있는 경우
        if Badge.objects.filter(github_id=github_user, repository_url=repository_url).exists():
            badge = Badge.objects.get(github_id=github_user, repository_url=repository_url)

        # DataBase에 Badge Data가 없는 경우
        else:

            # TODO: Github Repository 유효성 검사
            try:
                result = requests.get(f"https://api.github.com/repos/{github_user_organization}/{repo_name}/contributors", headers=headers)
            except:
                return Response({'message': '유효한 레포지토리 URL을 입력해 주세요.', 'status': 404}, status=status.HTTP_404_NOT_FOUND)

            if result.status_code != 200:
                return Response({'message': '유효한 레포지토리 URL을 입력해 주세요.', 'status': 404}, status=status.HTTP_404_NOT_FOUND)

            # TODO: 유효한 경우 Repository Contributor에 user가 있는지 검사
            contributors = json.loads(result.text)
            if not any(contributor['login'] == github_user for contributor in contributors):
                return Response({'message': f'{github_user}님은 {repo_name}에 Contributor로 등록되지 않았습니다.', 'status': 400}, status=status.HTTP_400_BAD_REQUEST)

            # TODO: GitHub Logic을 통해 데이터 받아오기
            pr_response = requests.get(f"https://api.github.com/repos/{github_user_organization}/{repo_name}/pulls?state=all", headers=headers)

            if pr_response.status_code != 200:
                return Response({'message': 'GitHub API Server Error.', 'status': 500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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

            # print(request_contributor_info)
            # -------------------------------------------------------------------------
            # 임시 데이터 (GitHub Logic 구현 후 변경 필요)
            # commit_cnt = 10
            # pull_request_cnt = 74
            # contribution = 80
            # -------------------------------------------------------------------------
            # 가중치 계산 및 토탈 점수 산출 (아직 계산식 미정)
            # 현재 contribution == total_percent 로 사용하고 있어
            # context도 percent = contribution으로 되어 있어 나중에 수정 필요
            # percent = contribution

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
        # theme = request.GET.get('theme', 'basic')
        template = loader.get_template('tag/profile.html')
        context = {
            'github_user': badge.github_id, 'repo_name': repo_name,
            'percent': badge.contribution, 'commits': badge.commit_cnt,
            'pull_requests': badge.pull_request_cnt
        }
        response = HttpResponse(content=template.render(context, request))
        response['Content-Type'] = 'image/svg+xml'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
