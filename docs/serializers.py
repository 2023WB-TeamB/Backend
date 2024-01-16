from .models import Docs, Keywords
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status

class KeywordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keywords
        fields = ['name']

class DocsSearchSerializer(serializers.ModelSerializer):
    keywords = KeywordsSerializer(read_only=True, many=True)

    class Meta:
        model = Docs
        fields = ['title', 'updated_at', 'keywords']

class DocsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Docs
        fields = '__all__'

    def response(self, data):
        response_data = {
            'message': '문서 생성 성공',
            'status': 201,
            'data': {
                'docs_id': data['id'],
                'title': data['title'],
                'content': data['content'],
                'language': data['language'],
                'tech_stack': ["Django", "React"],
                'created_at': data['created_at'],
            }
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    def docs_detail(self, data):
        docs_data = []
        for item in data:
            docs_data.append({
                "id": item['id'],
                "title": item['title'],
                "content": item['content'],
                "repository_url": item['repository_url'],
                "url": item['url'],
                "language": item['language'],
                "created_at": item['created_at'],
                "updated_at": item['updated_at'],
                "color": item['color']
            })
        response_data = {
            "status": 200,
            "message": '문서 상세 조회 성공',
            "data": {
                "docs": docs_data
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)

class SwaggerDocsPostSerializer(serializers.Serializer):
    repository_url = serializers.CharField()
    language = serializers.CharField()
    color = serializers.CharField()


class SwaggerDocsSharePostSerializer(serializers.Serializer):
    docs_id = serializers.IntegerField()


class SwaggerDocsContributorPostSerializer(serializers.Serializer):
    repository_url = serializers.CharField()

