from django.db import models
from user.models import User


class Team(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, unique=True, verbose_name="名称")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, verbose_name="从属")
    user = models.ManyToManyField(User, related_name="user", verbose_name="成员")

    class Meta:
        verbose_name = "分组"
        verbose_name_plural = "分组"

    def __str__(self):
        if self.parent != "":
            return
        else:
            return self.name
