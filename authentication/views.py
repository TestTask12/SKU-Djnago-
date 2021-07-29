from django.shortcuts import render
from rest_framework import generics, status, views, permissions
from .serializers import RegisterSerializer, LoginSerializer, EmailVerificationSerializer, ResetPasswordSerializer
from rest_framework.response import Response
from rest_framework.parsers import FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import AllowAny, IsAuthenticated,IsAuthenticatedOrReadOnly
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.shortcuts import redirect
from django.http import HttpResponsePermanentRedirect
import os
from .serializers import *


User = get_user_model()
JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

class RegisterView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user).access_token
        current_site = get_current_site(request).domain
        relativeLink = reverse('email-verify')
        absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
        email_body = 'Hi '+user.username + \
            ' Use the link below to verify your email \n' + absurl
        data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Verify your email'}

        Util.send_email(data)

        return Response(user_data, status=status.HTTP_201_CREATED)

class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST) 


class LoginAPIView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    parser_class = (FormParser, )

    # def post(self, request):
    #     print("request",request)
    #     print("request.data",request.data)
    #     serializer = self.serializer_class(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        print("request.data::>>>",request.data)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            email = request.data.get("email", None)
            password = request.data.get("password", None)
            try:
                User.objects.get(email=email)
            except:
                return Response({"error": "Your username/email is not correct. Please try again or register your details"})
            user = authenticate(email=email, password=password)
            print("user",user)
            if user:
                print("in",user)
                payload = JWT_PAYLOAD_HANDLER(user)
                print("After this ::>>>")
                jwt_token = JWT_ENCODE_HANDLER(payload)
                
                response = {
                    'success': 'True',
                    'status code': status.HTTP_200_OK,
                    'message': 'User logged in successfully',
                    'token': jwt_token,
                }
                status_code = status.HTTP_200_OK
                return Response(response, status=status_code)

class ResetPassword(views.APIView):
    permission_classes = (AllowAny,)
    def post(self,request):
        serializer = ResetPasswordSerializer(data=request.data)
        alldatas ={}
        if serializer.is_valid(raise_exception=True):
            mname =serializer.save()
        return Response(alldatas, status=status.HTTP_200_OK)