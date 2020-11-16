from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    def get_full_name(self):
        full_name = '%s %s' % (self.last_name, self.first_name)
        return full_name.strip()

    def __str__(self):
        return self.get_full_name()
    #
    # def save(self, *args, **kwargs):
    #     super(User, self).save(*args, **kwargs)
