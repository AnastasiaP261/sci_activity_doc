from django.shortcuts import render
from django.contrib.auth import login
from rest_framework import permissions, generics
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView

from api.serializers import CustomUserSerializer
from auth_wrapper.models import User


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=None)


class UserGetView(generics.ListAPIView):
    """
    Текущий пользователь
    """
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'

    def get_queryset(self):
        return User.objects.filter(username=self.request.user.get_username())

    def get_object(self):
        return User.objects.get_by_natural_key(self.request.user.get_username())
