from django.db import models
from docs.models import Docs

class TechStack(models.Model):
    id = models.AutoField(primary_key=True)
    docs_id = models.ForeignKey(Docs, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_deleted = models.BooleanField(default=False, null=False)