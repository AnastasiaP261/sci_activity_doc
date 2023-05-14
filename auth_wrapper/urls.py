"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from django.urls import re_path  # тот же path, только умеет в регулярки
from django.conf import urls
from django.views.generic import TemplateView
from rest_framework import routers, permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from knox import views as knox_views
from .views import LoginView, UserGetView

urlpatterns = [
    path('', UserGetView.as_view(), name='Возвращает информацию о текущем пользователе'),

    path(r'login/', LoginView.as_view(), name='knox login'),
    path(r'logout/', knox_views.LogoutView.as_view(), name='knox logout'),
    path(r'logoutall/', knox_views.LogoutAllView.as_view(), name='knox logoutall'),
]
