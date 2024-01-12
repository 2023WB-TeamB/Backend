from django.db import models
from docs.models import Docs

# Create your models here.
class Badge(models.Model):
    id = models.AutoField(primary_key=True)
    docs_id = models.ForeignKey(Docs, on_delete=models.CASCADE, null=True)
    github_id = models.CharField(max_length=255)
    commit_cnt = models.IntegerField()
    pull_request_cnt = models.IntegerField()
    contribution = models.IntegerField()
    repository_url = models.URLField(max_length=1000, null=True)

    def __str__(self):
        return self.docs_id
