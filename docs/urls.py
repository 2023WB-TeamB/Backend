from django.urls import path

from .views import *

urlpatterns = [
    path("create/", docs_create, name="docs_create"),
    path("docs/share/", docs_share, name="docs_share"),
]
