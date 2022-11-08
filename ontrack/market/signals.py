from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from ..market_data.models import Equity, Indice


@receiver(pre_save, sender=Equity)
def equity_pre_save(sender, instance, *args, **kwargs):
    if instance.slug is None:
        instance.slug = slugify(instance.symbol)


@receiver(pre_save, sender=Indice)
def indice_pre_save(sender, instance, *args, **kwargs):
    if instance.slug is None:
        instance.slug = slugify(instance.symbol)
