from factory import Faker
from factory.django import DjangoModelFactory

from ontrack.lookup.models import Setting


class SettingFactory(DjangoModelFactory):

    key = Faker("name")
    value = Faker("email")

    class Meta:
        model = Setting
        django_get_or_create = [
            "key",
            "value",
        ]
