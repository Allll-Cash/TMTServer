"""TMTServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from API.views import AuthTokenView, TasksView, FoldersView, Mark, Delete, Subscription

router = routers.DefaultRouter()

urlpatterns = [
    path('auth/', AuthTokenView.as_view()),
    path('api-auth/', include('rest_framework.urls')),
    path('tasks/', TasksView.as_view()),
    path('folders/', FoldersView.as_view()),
    path('mark/', Mark.as_view()),
    path('delete/', Delete.as_view()),
    path('subs/', Subscription.as_view()),
    path('', include(router.urls)),
    path('admin/', admin.site.urls)
]
