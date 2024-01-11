from .models import Docs
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status


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

    def docs_share(self, data):
        docs_id = data.get('docs_id')
        doc = Docs.objects.get(pk=docs_id)

        response_data = {
            "message": "문서 공유 URL 생성 성공",
            "status": 201,
            "data": {
                "share_url": doc.url,
            }
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class SwaggerDocsPostSerializer(serializers.Serializer):
    repository_url = serializers.CharField()
    language = serializers.CharField()
    color = serializers.CharField()


class SwaggerDocsSharePostSerializer(serializers.Serializer):
    docs_id = serializers.IntegerField()


class SwaggerDocsContributorPostSerializer(serializers.Serializer):
    repository_url = serializers.CharField()
