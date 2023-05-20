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

import auth_wrapper.views
from . import views
from auth_wrapper import urls as auth_wrapper_urls

schema_view = get_schema_view(
    openapi.Info(
        title="SciActivityDoc API schema",
        default_version='v1',
    ),
    public=True,  # TODO: настроить доступ см https://drf-yasg.readthedocs.io/en/stable/settings.html#authorization
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # это все для сваггера. Подробнее см. https://github.com/axnsan12/drf-yasg/
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='json/yaml схема api'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema swagger-ui'),

    path('auth/', include(auth_wrapper_urls.urlpatterns)),

    path('user/', views.UserDetail.as_view(), name='Возвращает информацию о текущем пользователе'),
    path('researcher/', views.ResearcherList.as_view(),
         name='Возвращает список исследователей, отсортированных по ФИО. '
              'В конце списка будут присутствовать "архивные" пользователи.'),

    path(r'note/<int:note_id>/', views.NoteDetail.as_view(),
         name='GET - показ информации о заметке по ее айди, DELETE - удаление заметки'),
    path(r'note/', views.NoteList.as_view(),
         name='GET - список последних заметок, POST - создание заметки'),

    # path('research/<str:rsrch_id>/graph/<int:graph_id>/node/<int:node_id>/'),
    # path('research/<str:rsrch_id>/graph/<int:graph_id>/node/'),
    #
    # path('research/<str:rsrch_id>/graph/<int:graph_id>/'),
    # path('research/<str:rsrch_id>/graph/'),
    #
    # path('research/<str:rsrch_id>/'),
    # path('research/'),
]
