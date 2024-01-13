from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.template import loader


class BadgeView(APIView):
    def get(self, request, github_user, repo_name, *args, **kwargs):
        print(github_user, repo_name)

        theme = request.GET.get('theme', 'basic')
        template = loader.get_template('tag/profile.html')
        context = {'github_user': github_user, 'repo_name': repo_name, 'percent': 80}
        print(context)
        response = HttpResponse(content=template.render(context, request))
        response['Content-Type'] = 'image/svg+xml'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
