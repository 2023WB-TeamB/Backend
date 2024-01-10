from .models import User
from rest_framework import serializers
from .models import *

# swagger
from drf_yasg import openapi


class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            nickname=validated_data['nickname'],
        )
        return user

    class Meta:
        model = User
        fields = ['nickname', 'email', 'password']


class SignSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # 모두 직렬화하겠음
        fields = '__all__'


# swagger 관련
class SwaggerRegisterPostSerializer(serializers.Serializer):
    email = serializers.CharField()
    nickname = serializers.CharField()
    password = serializers.CharField()


class SwaggerLoginPostSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

