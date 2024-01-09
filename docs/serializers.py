from rest_framework import serializers
from .models import Docs
class Serializer(serializers.ModelSerializer):
    class Meta:
        model = Docs
        fields = '__all__'