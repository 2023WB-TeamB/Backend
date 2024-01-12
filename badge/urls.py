from django.urls import path
from . import views

urlpatterns = [
    path('badge/<str:github_id>/<str:repo_name>/', views.BadgeView.as_view()),  # get - 문서 내역 조회
]
