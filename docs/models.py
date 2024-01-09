from django.db import models
from users.models import User


# Create your models here.
class Docs(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    repository_url = models.URLField(max_length=1000)
    url = models.URLField(max_length=1000, null=True)
    language = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title
