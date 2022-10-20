from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ontrack.utils.base.enum import UserSettingKey
from ontrack.utils.base.model import BaseModel


class User(AbstractUser):
    """
    Default custom user model for On Smart Project API.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})


class UserProfile(BaseModel):
    user = models.OneToOneField(
        User, related_name="user_profile", on_delete=models.CASCADE
    )
    mobile = models.CharField(max_length=100, null=True, blank=True)
    address1 = models.CharField(max_length=200, null=True, blank=True)
    address2 = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.username


class Setting(BaseModel):
    user = models.ForeignKey(User, related_name="settings", on_delete=models.CASCADE)
    key = models.CharField(max_length=50, choices=UserSettingKey.choices, unique=True)
    value = models.CharField(max_length=200)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.key


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)
#         Settings.objects.create(
#             user=instance,
#             key=UserSettingKey.DEFAULT_THEME,
#             value="dark")
