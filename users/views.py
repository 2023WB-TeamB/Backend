from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated

import jwt

from gtd.settings import *
from .serializers import *
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework import status
from rest_framework.response import Response

from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from rest_framework_simplejwt.tokens import UntypedToken

# swagger 관련
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema


# from drf_yasg import openapi

class RegisterAPIView(APIView):
    @swagger_auto_schema(request_body=SwaggerRegisterPostSerializer)
    # 회원가입
    def post(self, request):
        serializer = UserSerializer(data=request.data)

        # 만약 전달된 데이터가 유효하다면
        if serializer.is_valid():
            # UserSerializer에서 사용자 정보를 저장하고 저장된 사용자 정보를 가져옵니다.
            user = serializer.save()

            # 토큰을 얻기 위해 TokenObtainPairSerializer를 사용합니다.
            token = TokenObtainPairSerializer.get_token(user)

            # 토큰을 문자열로 변환합니다.
            refresh_token = str(token)
            access_token = str(token.access_token)

            # 콘솔에 토큰을 출력합니다.
            print(refresh_token)
            print(access_token)

            res = Response(
                {
                    # "user": serializer.data,
                    "message": "register successs",
                    # "token": {
                    #     "access": access_token,
                    #     "refresh": refresh_token,
                    # },
                },
                status=status.HTTP_200_OK,
            )

            res.set_cookie("access", access_token, httponly=True)
            res.set_cookie("refresh", refresh_token, httponly=True)

            return res
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # class UserViewset(viewsets.ModelViewSet):
    #     permission_classes = [IsAuthenticated]
    #     queryset = User.objects.all()
    #     serializer_class = SignSerializer
    #
    #     def update(self, request, *args, **kwargs):
    #         kwargs['partial'] = True
    #         return super().update(request, *args, **kwargs)


@swagger_auto_schema(request_body=SwaggerLoginPostSerializer)
class AuthAPIView(APIView):

    # 유저 정보 확인
    def get(self, request):
        try:
            # 유저 식별
            access = request.COOKIES['access']
            payload = jwt.decode(access, SECRET_KEY, algorithms=['HS256'])
            pk = payload.get('user_id')
            user = get_object_or_404(User, pk=pk)
            serializer = SignSerializer(instance=user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except jwt.exceptions.ExpiredSignatureError:
            # 토큰 만료 시 토큰 갱신
            data = {'refresh': request.COOKIES.get('refresh', None)}
            serializer = TokenRefreshSerializer(data=data)

            if serializer.is_valid(raise_exception=True):
                access = serializer.data.get('access', None)
                refresh = serializer.data.get('refresh', None)
                payload = jwt.decode(access, SECRET_KEY, algorithms=['HS256'])
                pk = payload.get('user_id')
                user = get_object_or_404(User, pk=pk)
                serializer = SignSerializer(instance=user)

                res = Response(serializer.data, status=status.HTTP_200_OK)
                res.set_cookie('access', access)
                res.set_cookie('refresh', refresh)
                return res

            raise jwt.exceptions.InvalidTokenError

        except jwt.exceptions.InvalidTokenError:
            # 사용 불가능한 토큰
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        flag = request.data.get('flag')
        key = request.data.get('key')

        if flag == 'set':
            value = request.data.get('value')
            cache.set(key, value)
        elif flag == 'get':
            res = cache.get(key)
            return Response({key : res}, status=status.HTTP_200_OK)

        return Response({'msg': 'success'}, status=status.HTTP_200_OK)

    # 로그인
    def post(self, request):
        user = authenticate(
            email=request.data.get("email"), password=request.data.get("password")
        )
        if user is not None:
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)

            # 리프레쉬 토큰을 Redis에 저장
            cache.set(user.id, refresh_token, timeout=int(token.lifetime.total_seconds()))

            res = Response(
                {
                    "message": "login success",
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    }
                },
                status=status.HTTP_200_OK,
            )
            res.set_cookie("access", access_token, httponly=True)
            res.set_cookie("refresh", refresh_token, httponly=True)
            return res
        else:
            return Response({'message': 'Invalid email or password.'}, status=status.HTTP_400_BAD_REQUEST)

    # 로그아웃
    def delete(self, request):
        access_token = request.COOKIES.get('access')
        refresh_token = request.COOKIES.get('refresh')
        user = User.objects.filter(email=request.data.get("email")).first()

        # access 토큰 검증
        try:
            UntypedToken(access_token)
        except jwt.exceptions.InvalidTokenError:
            return Response({'message': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

        # 쿠키에 저장된 토큰 삭제
        response = Response({
            "message": "Logout success"
        }, status=status.HTTP_202_ACCEPTED)
        response.delete_cookie("access")
        response.delete_cookie("refresh")

        # Redis에서 리프레쉬 토큰 삭제
        cache.delete(user.id)

        return response


