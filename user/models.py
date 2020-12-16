from django.db import models
from django.contrib.auth.models import AbstractUser
from team.models import Team


class User(AbstractUser):
    ip_address = models.CharField(max_length=20, blank=True, verbose_name="上次登录ip")
    team = models.ManyToManyField(Team, related_name="team", blank=True, verbose_name="所属团队")

    def get_full_name(self):
        full_name = '%s%s' % (self.last_name, self.first_name)
        return full_name.strip()

    def __str__(self):
        return self.get_full_name()
    #
    # def save(self, *args, **kwargs):
    #     super(User, self).save(*args, **kwargs)
