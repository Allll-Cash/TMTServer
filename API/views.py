from random import randrange

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from API.models import Task, Folder, Subscription as SubModel, Code
from rest_framework.authtoken.models import Token

from TMTServer.settings import EMAIL_HOST_USER


class API(APIView):
    def set_user(self, request):
        if 'token' not in request.GET.keys():
            return
        token = request.GET['token']
        user = Token.objects.get(key=token).user
        request.user = user


@permission_classes((permissions.AllowAny,))
class Subscription(API):

    def post(self, request, *args, **kwargs):
        self.set_user(request)
        if 'info' in request.POST.keys():
            folder = Folder.objects.get(id=request.POST['id'])
            subs = SubModel.objects.filter(folder=folder)
            return JsonResponse({
                'users': [sub.user.email for sub in subs]
            })
        user = User.objects.get(email=request.POST['email'])
        folder = Folder.objects.get(id=request.POST['id'])
        SubModel.objects.get_or_create(user=user, folder=folder)
        return JsonResponse({'success': True})

    def delete(self, request, *args, **kwargs):
        self.set_user(request)
        folder = Folder.objects.get(id=request.POST['id'])
        user = User.objects.get(email=request.POST)




@permission_classes((permissions.AllowAny,))
class Delete(API):
    def post(self, request, *args, **kwargs):
        Task.objects.get(id=request.POST['id']).delete()
        return JsonResponse({'success': True})


@permission_classes((permissions.AllowAny,))
class Mark(API):
    def post(self, request, *args, **kwargs):
        task = Task.objects.get(id=request.POST['id'])
        task.done = 1 - task.done
        task.save()
        return JsonResponse({'success': True})


@permission_classes((permissions.AllowAny,))
class TasksView(API):
    def get(self, request, *args, **kwargs):
        self.set_user(request)
        if not request.user.is_authenticated:
            return JsonResponse({'tasks': []})
        if request.user.is_superuser:
            queryset = Task.objects.all()
        else:
            queryset = [task for folder in Folder.objects.filter(owner=request.user) for task in folder.tasks] + \
                   [task for sub in SubModel.objects.filter(user=request.user) for task in sub.folder.tasks]
        return JsonResponse({
            'tasks': [
                {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'done': task.done,
                    'folder': {
                        'id': task.folder.id,
                        'name': task.folder.name,
                        'owner': task.folder.owner.email,
                        'icon': task.folder.icon
                    }
                } for task in queryset
            ]
        })

    def post(self, request, *args, **kwargs):
        self.set_user(request)
        if 'id' in request.POST.keys():
            task = Task.objects.get(id=request.POST['id'])
        else:
            task = Task()
        task.title = request.POST['title']
        task.description = request.POST['description']
        task.folder = Folder.objects.get(id=request.POST['folder'])
        task.creator = request.user
        task.save()
        return JsonResponse({"success": True})


@permission_classes((permissions.AllowAny,))
class FoldersView(API):
    def get(self, request, *args, **kwargs):
        self.set_user(request)
        if not request.user.is_authenticated:
            return JsonResponse({'folders': []})
        if request.user.is_superuser:
            queryset = Folder.objects.all()
        else:
            queryset = [folder for folder in Folder.objects.filter(owner=request.user)] + \
                       [sub.folder for sub in SubModel.objects.filter(user=request.user)]
        return JsonResponse({
            'folders': [
                {
                    'id': folder.id,
                    'name': folder.name,
                    'owner': folder.owner.email,
                    'icon': folder.icon
                } for folder in queryset
            ]
        })

    def post(self, request, *args, **kwargs):
        self.set_user(request)
        if 'action' in request.POST.keys():
            Folder.objects.get(id=request.POST['id']).delete()
            return JsonResponse({'success': True})
        Folder.objects.create(name=request.POST['name'], icon=request.POST['icon'], owner=request.user)
        return JsonResponse({'success': True})


@permission_classes((permissions.AllowAny,))
class AuthTokenView(APIView):
    def get(self, request, *args, **kwargs):
        email = request.GET['email']
        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            user = User.objects.create_user(email, email, 'password')
            Folder.objects.create(owner=user, name='Учеба', icon='book.fill')
            Folder.objects.create(owner=user, name='Работа', icon='desktopcomputer')
            Folder.objects.create(owner=user, name='Спорт', icon='figure.walk')
            Folder.objects.create(owner=user, name='Дом', icon='house.fill')
            Folder.objects.create(owner=user, name='Здоровье', icon='heart.fill')
        Code.objects.filter(user=user).delete()
        token = Code.objects.create(user=user, code=randrange(10000, 100000))
        send_mail(
            'Вход в TMT',
            f'Для входа в приложение введите следующий код: {token.code}',
            EMAIL_HOST_USER,
            [email]
        )
        return JsonResponse({
            'success': 'True'
        })

    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        code = request.POST['code']
        user = User.objects.get(email=email)
        try:
            token = Code.objects.get(user=user, code=code)
        except ObjectDoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Неверный код'
            })
        token.delete()
        Token.objects.filter(user=user).delete()
        return JsonResponse({
            'success': True,
            'token': Token.objects.create(user=User.objects.get(email=email)).key
        })
