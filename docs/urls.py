from django.urls import path
from . import views
from .views import *

urlpatterns =[
    path('docs/', views.DocsList.as_view()), # get - 문서 내역 조회
    path("docs/create/", docs_create, name="docs_create"),
]
