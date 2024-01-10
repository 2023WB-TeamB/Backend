from django.http import Http404
from django.urls import is_valid_path
from rest_framework.views import APIView
from .models import Docs, User
from .serializers import DocsSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .github import *
import uuid


class DocsList(APIView):
    def get(self, request): # 문서 조회
        docs = Docs.objects.filter(is_deleted=False)  # is_deleted가 False인 객체만 조회
        serializer = DocsSerializer(docs, many=True)
        return Response(serializer.data)

class DocsDetail(APIView): # Docs의 detail을 보여주는 역할
    def get_object(self, pk):  # Docs 객체 가져오기
        try:
            return Docs.objects.get(pk=pk, is_deleted=False)  # is_deleted가 False인 객체만 조회
        except Docs.DoesNotExist:
            raise Http404
    def get(self, request, pk): # 문서 상세 조회
        doc = self.get_object(pk)
        serializer =  DocsSerializer(doc)
        return Response(serializer.data)

# from django.shortcuts import get_object_or_404, get_list_or_404


@api_view(['POST'])
def docs_create(request):

    if request.method == 'POST':
        repository_url = request.data.get('repository_url')
        language = request.data.get('language')

        if repository_url is None or language is None or language not in ['KOR', 'ENG']:
            return Response({"message": "잘못된 요청입니다. 입력 형식을 확인해 주세요.", "status": 400}, status=status.HTTP_400_BAD_REQUEST)

        if url_validator(repository_url) is False:
            return Response({"message": "유효하지 않은 URL입니다.", "status": 404}, status=status.HTTP_400_BAD_REQUEST)


        framework = framework_finder(repository_url)
        # Github, OpenAI API 이용해 Framework 추출
        # return Response({"message": framework, "status": 201, "data": {"docs_id": 1}}, status=status.HTTP_201_CREATED)

        ####################################################
        if repository_url.startswith("https://"):
            repository_url = repository_url.replace("https://", "")

        repo_url_list = repository_url.split("/")
        owner = repo_url_list[1]
        repo = repo_url_list[2].split(".")[0]
        path = ''
        root_file = get_file_content(owner, repo, path)

        # TODO: 찾아낸 Framework를 활용하여 GitHub 코드 추출
        if root_file:
            prompt_ary = get_github_code_prompt(repository_url, framework)
            response = get_assistant_response(prompt_ary)

        return Response({"message": response, "status": 201, "data": {"docs_id": 1}}, status=status.HTTP_201_CREATED)
        # TODO: 추출한 코드를 활용하여 문서 생성
        request.data['user_id'] = User.objects.filter(id=1).first().id
        request.data['title'] = "OPGC (Open Source Project's Github Contributions)"
        request.data['content'] = "OPGC (Open Source Project's Github Contributions)"
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
            return Response({"message": "이미 URL이 생성된 문서입니다.", "status": 409}, status=status.HTTP_409_CONFLICT)

        # UUID를 사용하여 고유한 URL 생성
        base_url = 'http://127.0.0.1:8000/api/v1/docs/share/'
        unique_url = base_url + str(uuid.uuid4())
        doc.url = unique_url
        doc.save()

        return Response({"message": "문서 공유 URL 생성 성공", "status": 201, "data": {"url": doc.url}}, status=status.HTTP_201_CREATED)
