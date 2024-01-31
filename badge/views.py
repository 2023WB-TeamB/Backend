from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.template import loader

from .models import Badge
from .theme import *

import environ
import requests
import json
from datetime import datetime
# swagger 관련
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

# 지원하는 기술 스택 이미지 목록
# Flutter, React Native, Angular, Next, Nuxt, React, Svelte, Vue, Unity, Django, Flask, FastAPI, Node, Spring, SpringBoot
# parameter 입력시 소문자로 입력해야 합니다.
class BadgeView(APIView):
    @swagger_auto_schema(tags=["Badge"], operation_summary="뱃지 조회 API")
    def get(self, request, github_user_organization, repo_name, github_user, *args, **kwargs):

        env = environ.Env(DEBUG=(bool, True))
        GITHUB_TOKEN = env('GITHUB_TOKEN')
        headers = {'Authorization': 'token ' + GITHUB_TOKEN}

        repository_url = "https://github.com/" + github_user_organization + "/" + repo_name

        theme = request.GET.get("theme", "terminal2")

        if theme == "terminal1":
            response = terminal1(request, github_user_organization, repo_name, github_user, repository_url, headers)
        elif theme == "terminal2":
            start_date = request.GET.get("start", None)
            end_date = request.GET.get("end", None)

            # 날짜 Validation
            try:
                # 입력된 문자열을 날짜로 변환합니다.
                start_date_obj = datetime.strptime(start_date, '%Y%m%d')
                end_date_obj = datetime.strptime(end_date, '%Y%m%d')
                transformed_start_date_str = datetime.strftime(start_date_obj, '%Y-%m-%d')
                transformed_end_date_str = datetime.strftime(end_date_obj, '%Y-%m-%d')
                request.data['start'] = transformed_start_date_str
                request.data['end'] = transformed_end_date_str
            except:
                return Response({'message': '날짜 형식이 잘못되었습니다.', 'status': 400}, status=status.HTTP_400_BAD_REQUEST)
            response = terminal2(request, github_user_organization, repo_name, github_user, "light", headers)
        elif theme == "terminal3":
            start_date = request.GET.get("start", None)
            end_date = request.GET.get("end", None)

            try:
                start_date_obj = datetime.strptime(start_date, '%Y%m%d')
                end_date_obj = datetime.strptime(end_date, '%Y%m%d')
                transformed_start_date_str = datetime.strftime(start_date_obj, '%Y-%m-%d')
                transformed_end_date_str = datetime.strftime(end_date_obj, '%Y-%m-%d')
                request.data['start'] = transformed_start_date_str
                request.data['end'] = transformed_end_date_str
            except:
                return Response({'message': '날짜 형식이 잘못되었습니다.', 'status': 400}, status=status.HTTP_400_BAD_REQUEST)
            response = terminal2(request, github_user_organization, repo_name, github_user, "dark", headers)
        elif theme == "card1":
            start_date = request.GET.get("start", None)
            end_date = request.GET.get("end", None)

            try:
                start_date_obj = datetime.strptime(start_date, '%Y%m%d')
                end_date_obj = datetime.strptime(end_date, '%Y%m%d')
                transformed_start_date_str = datetime.strftime(start_date_obj, '%Y-%m-%d')
                transformed_end_date_str = datetime.strftime(end_date_obj, '%Y-%m-%d')
                request.data['start'] = transformed_start_date_str
                request.data['end'] = transformed_end_date_str
            except:
                return Response({'message': '날짜 형식이 잘못되었습니다.', 'status': 400}, status=status.HTTP_400_BAD_REQUEST)

            response = card1(request, github_user_organization, repo_name, github_user, headers)
            pass
        else:
            return Response({'message': '유효한 테마를 입력해 주세요.', 'status': 404}, status=status.HTTP_404_NOT_FOUND)

        response['Content-Type'] = 'image/svg+xml'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
