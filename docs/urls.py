from django.urls import path
from . import views
from .views import *

urlpatterns =[
    # path('docs/', views.DocsList.as_view()), # get - 문서 내역 조회
    path('docs/', views.DocsList.as_view()), # get - 문서 내역 조회
    # path('docs/<int:pk>/', views.DocsDetail.as_view()), # get - 문서 상세 내역 조회
    path("docs/create/", docs_create, name="docs_create"),
    path("docs/share/", docs_share, name="docs_share"),
    path('docs/contributor/', docs_contributor, name='docs_contributor'),
]
