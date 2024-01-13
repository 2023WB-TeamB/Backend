from django.urls import path
from . import views

urlpatterns = [
    path('badge/<str:github_user_organization>/<str:repo_name>/<str:github_user>', views.BadgeView.as_view()),  # get - 문서 내역 조회
]
