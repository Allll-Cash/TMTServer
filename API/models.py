from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Code(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.IntegerField()


class Folder(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField(null=True)
    icon = models.TextField(null=True)

    @property
    def tasks(self):
        return Task.objects.filter(folder=self)


class Task(models.Model):
    title = models.TextField(null=True)
    description = models.TextField(null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True)
    done = models.IntegerField(default=0)


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
