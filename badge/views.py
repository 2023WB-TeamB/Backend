from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.template import loader

from .models import Badge


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

        repository_url = "https://github.com/" + github_user + "/" + repo_name
        # 뱃지에 등록된 데이터가 있는 경우
        if Badge.objects.filter(github_id=github_user, repository_url=repository_url).exists():
            badge = Badge.objects.get(github_id=github_user, repository_url=repository_url)
            # template = loader.get_template('tag/profile.html')
            # context = {
            #     'github_user': badge.github_id, 'repo_name': repo_name,
            #     'percent': badge.contribution, 'commits': badge.commit_cnt,
            #     'pull_requests': badge.pull_request_cnt
            # }
            # # TODO: 아래 코드 -> 즉 html(svg) 반환 코드는 모든 상황에서 진행됄 예정이기 때문에 나중에 한번에 처리 (분리 완료)
            # response = HttpResponse(content=template.render(context, request))
            # response['Content-Type'] = 'image/svg+xml'
            # response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            # return response

        # DataBase에 Badge Data가 없는 경우
        else:
            # TODO: Github Repository 유효성 검사
            # TODO: 유효한 경우 Repository Contributor에 user가 있는지 검사
            # TODO: GitHub Logic을 통해 데이터 받아오기
            # -------------------------------------------------------------------------
            # 임시 데이터 (GitHub Logic 구현 후 변경 필요)
            commit_cnt = 230
            pull_request_cnt = 74
            contribution = 80
            # -------------------------------------------------------------------------
            # 가중치 계산 및 토탈 점수 산출 (아직 계산식 미정)
            # 현재 contribution == total_percent 로 사용하고 있어
            # context도 percent = contribution으로 되어 있어 나중에 수정 필요
            percent = contribution

            # DataBase에 저장
            badge = Badge(github_id=github_user, commit_cnt=commit_cnt,
                          pull_request_cnt=pull_request_cnt, contribution=contribution,
                          repository_url=repository_url)
            badge.save()

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
