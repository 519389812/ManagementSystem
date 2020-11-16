from django.db import models
from user.models import User


class Team(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, unique=True, verbose_name="组名")
    user = models.ManyToManyField(User, related_name="user", default=None, blank=True, verbose_name="成员")

    class Meta:
        verbose_name = "分组"
        verbose_name_plural = "分组"

    def __str__(self):
        return self.name


class Department(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True, verbose_name="团队名")
    team = models.ManyToManyField(Team, related_name="team", default=None, blank=True, verbose_name="团队")

    class Meta:
        verbose_name = "团队"
        verbose_name_plural = "团队"

    def __str__(self):
        return self.name