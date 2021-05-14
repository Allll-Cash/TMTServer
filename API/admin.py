from django.contrib import admin

# Register your models here.
from API.models import Task, Folder

admin.site.register(Task)
admin.site.register(Folder)
