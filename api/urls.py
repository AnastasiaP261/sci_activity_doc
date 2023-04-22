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

from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="SciActivityDoc API schema",
        default_version='v1',
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="petrichuk.nastya@yandex.ru"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ],
)

urlpatterns = [
    # это все для сваггера (см. https://gadjimuradov.ru/post/swagger-dlya-django-rest-framework/)
    re_path(r'^swagger(?:\.json|\.yaml)$',
            # schema_view.without_ui создает экземпляр представления, используя только средства визуализации
            # JSON и YAML, опционально обернутые с помощью cache_page
            # (см. https://docs.djangoproject.com/en/dev/topics/cache/).
            schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
    path('swagger/',
         # создает экземпляр представления с помощью средства визуализации веб-интерфейса,
         # опционально обернутого с помощью cache_page.
         schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),

    path('auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('user/', views.UserGetView.as_view(), name='Возвращает информацию о текущем пользователе'),
    path('researchers/', views.ResearcherListView.as_view(),
         name='Возвращает список исследователей, отсортированных по ФИО. '
              'В конце списка будут присутствовать "архивные" пользователи.'),

]
