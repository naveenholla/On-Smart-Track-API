from django.db import models


class UserManager(models.Manager):
    def myfunction(self):
        return super().all()
