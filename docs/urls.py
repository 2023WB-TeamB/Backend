from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('docs', views.DocsAPI.as_view()),
    path('docs/version', views.DocsVersionList.as_view()),
    path('docs/<int:pk>', views.DocsDetail.as_view()),
    path("docs/share", DocsShareView.as_view()),
    path('docs/contributor',DocsContributorView.as_view()),
    path('docs/search', DocsSearchView.as_view()),
    path('docs/img', UploadImageView.as_view()),
]