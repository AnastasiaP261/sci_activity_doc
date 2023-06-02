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

from auth_wrapper import urls as auth_wrapper_urls
from . import views

urlpatterns = [
    path('auth/', include(auth_wrapper_urls.urlpatterns)),

    path('user/', views.UserDetail.as_view(), name='Возвращает информацию о текущем пользователе'),
    path('researcher/', views.ResearcherList.as_view(),
         name='Возвращает список исследователей, отсортированных по ФИО. '
              'В конце списка будут присутствовать "архивные" пользователи.'),
    path('user/suggestions/', views.UserSuggestions.as_view({'get': 'list'}),
         name='GET - возвращает подсказки для поиска пользователя по имени'),

    path(r'note/<int:note_id>/', views.NoteDetail.as_view(),
         name='GET - показ информации о заметке по ее айди, DELETE - удаление заметки'),
    path(r'note/', views.NoteCreate.as_view(),
         name='GET - список последних заметок, POST - создание заметки'),

    path('graph/<int:graph_id>/node/<int:node_id>/', views.NodeDetail.as_view(),
         name='GET - просмотр информации об узле графа'),
    path('graph/<int:graph_id>/', views.GraphDetail.as_view(),
         name='GET - показ информации о графе по его айди, DELETE - удаление графа, PATCH - обновление информации в графе'),
    # TODO обязательно запиши что отсюда нельзя поменять набор заметок

    path('graph/', views.CreateGraph.as_view(),
         name='POST - создание графа'),

    path('research/<str:rsrch_id>/', views.ResearchDetail.as_view(),
         name='GET - показ информации об исследовании, DELETE - удаление исследования, PATCH - обновление информации в исследовании'),
    path('research/', views.ResearchList.as_view(),
         name='GET - запрос всех исследований или исследований пользователя, POST - создание графа'),
]
