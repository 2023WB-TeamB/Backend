from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from users.utils import user_token_to_data
from .models import Docs, User
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .github import *
import uuid
import requests
import json
import environ

# swagger 관련
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema, no_body


@swagger_auto_schema(request_body=no_body)
class DocsList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):  # 문서 조회
        authorization_header = request.META.get('HTTP_AUTHORIZATION')
        if authorization_header and authorization_header.startswith('Bearer '):
            token = authorization_header.split(' ')[1]
            user_id = user_token_to_data(token)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not User.objects.filter(id=user_id).exists():  # user_id가 User 테이블에 존재하지 않는 경우
            return Response({
                "status": 404,
                "message": "user_id가 존재하지 않습니다.",
            }, status=status.HTTP_404_NOT_FOUND)

        docs = Docs.objects.filter(is_deleted=False, user_id=user_id)  # is_deleted가 False인 객체만 조회
        if not docs:  # 문서가 존재하지 않는 경우
            return Response({
                "status": 404,
                "message": "해당 user_id에 해당하는 문서가 존재하지 않습니다.",
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = DocsSerializer(docs, many=True)
        docs_data = []
        for item in serializer.data:
            docs_data.append({
                "id": item['id'],
                "title": item['title']
            })
        response_data = {
            "status": 200,
            "message": '문서 조회 성공',
            "data": {
                "docs": docs_data
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)

class DocsCreateView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=SwaggerDocsPostSerializer)
    def post(self, request, *args, **kwargs):
        repository_url = request.data.get('repository_url')
        language = request.data.get('language')
        color = request.data.get('color')

        if not User.objects.filter(id=user_id).exists():  # user_id가 User 테이블에 존재하지 않는 경우
            return Response({
                "status": 404,
                "message": "user_id가 존재하지 않습니다.",
            }, status=status.HTTP_404_NOT_FOUND)

        docs = Docs.objects.filter(is_deleted=False, user_id=user_id)  # is_deleted가 False인 객체만 조회

        if repository_url is None or language is None or language not in ['KOR', 'ENG'] or color is None:
            return Response({"message": "잘못된 요청입니다. 입력 형식을 확인해 주세요.", "status": 400},
                            status=status.HTTP_400_BAD_REQUEST)

        request.data['user_id'] = User.objects.filter(id=1).first().id
        request.data['title'] = "OPGC (Open Source Project's Github Contributions)"
        request.data['content'] = ""
        request.data['user_id'] = User.objects.filter(id=user_id).first().id
        request.data['title'] = "OPGC (Open Source Project's Github Contributions)"
        request.data['content'] = """## 프로젝트 소개
OPGC 프로젝트는 Github 프로필을 분석하여 사용자의 기여를 추적하고 랭킹을 매기는 서비스입니다."""

        serializer = DocsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class DocsShareView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=SwaggerDocsSharePostSerializer)
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            docs_id = request.data.get('docs_id')
            if docs_id is None:
                return Response({"message": "문서 ID를 입력해 주세요.", "status": 400}, status=status.HTTP_400_BAD_REQUEST)
            try:
                doc = Docs.objects.get(pk=docs_id)
            except Docs.DoesNotExist:
                return Response({"message": "존재하지 않는 문서 ID입니다.", "status": 404}, status=status.HTTP_404_NOT_FOUND)
            if doc.url is not None:
                return Response({"message": "이미 URL이 생성된 문서입니다.", "status": 409, "existing_url": doc.url},
                                status=status.HTTP_409_CONFLICT)
            # UID를 사용하여 고유한 URL 생성
            base_url = 'http://127.0.0.1:8000/api/v1/docs/share/'
            unique_url = base_url + str(uuid.uuid4())
            doc.url = unique_url
            doc.save()
        serializer = DocsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return serializer.response(data=serializer.data)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def docs_share(request):
    if request.method == 'POST':
        docs_id = request.data.get('docs_id')

        if docs_id is None:
            return Response({"message": "문서 ID를 입력해 주세요.", "status": 400}, status=status.HTTP_400_BAD_REQUEST)

        try:
            doc = Docs.objects.get(pk=docs_id)
        except Docs.DoesNotExist:
            return Response({"message": "존재하지 않는 문서 ID입니다.", "status": 404}, status=status.HTTP_404_NOT_FOUND)

        if doc.url is not None:
            return Response({"message": "이미 URL이 생성된 문서입니다.", "status": 409, "existing_url": doc.url}, status=status.HTTP_409_CONFLICT)

        # UUID를 사용하여 고유한 URL 생성
        base_url = 'http://127.0.0.1:8000/api/v1/docs/share/'
        unique_url = base_url + str(uuid.uuid4())
        doc.url = unique_url
        doc.save()

        return Response({"message": "문서 공유 URL 생성 성공", "status": 201, "data": {"url": doc.url}}, status=status.HTTP_201_CREATED)


        doc.url = unique_url
            return Response({"message": "문서 공유 URL 생성 성공", "status": 201, "data": {"url": doc.url}},
                            status=status.HTTP_201_CREATED)


class DocsContributorView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=SwaggerDocsContributorPostSerializer)
    def post(self, request, *args, **kwargs):
        repo_url = request.data.get('repository_url')

        if repo_url is None:
            return Response({'message': '레포지토리 URL을 입력해 주세요.', 'status': 400}, status=status.HTTP_400_BAD_REQUEST)

        env = environ.Env(DEBUG=(bool, True))
        GITHUB_TOKEN = env('GITHUB_TOKEN')
        headers = {'Authorization': 'token ' + GITHUB_TOKEN}
        repo_name = repo_url.split("github.com/")[1]
        repository_url = f"https://api.github.com/repos/{repo_name}/contributors"

        response = requests.get(repository_url, headers=headers)

        if response.status_code == 200:
            contributors = json.loads(response.text)
            total_contributions = sum([contributor['contributions'] for contributor in contributors])
            result = []

            for contributor in contributors:
                contribution_percent = '{:.2f}%'.format(
                    (contributor['contributions'] / total_contributions) * 100)
                result.append({
                    'contributor': contributor['login'],
                    'contributions': contributor['contributions'],
                    'contribution_percent': contribution_percent
                })

            return Response({'message': '컨트리뷰터 생성 성공', 'status': 201, 'data': result}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': '레포지토리를 찾을 수 없습니다.', 'status': 404}, status=status.HTTP_404_NOT_FOUND)
