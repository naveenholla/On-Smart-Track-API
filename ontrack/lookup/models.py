from django.db import models

from ontrack.utils.base.enum import AdminSettingKey
from ontrack.utils.base.model import BaseModel

from .manager import SettingPullManager


# Create your models here.
class Currency(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    symbol = models.CharField(max_length=100, unique=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Setting(BaseModel):
    key = models.CharField(max_length=50, choices=AdminSettingKey.choices, unique=True)
    value = models.CharField(max_length=200)

    backend = SettingPullManager()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.key


# class FieldDataType(BaseModel):
#     name = models.CharField(max_length=50)

#     class Meta(BaseModel.Meta):
#         ordering = ["-created_at"]

#     def __str__(self):
#         return self.name


# class FieldTypeCategory(BaseModel):
#     name = models.CharField(max_length=50)

#     class Meta(BaseModel.Meta):
#         ordering = ["-created_at"]

#     def __str__(self):
#         return self.name


# class FieldType(BaseModel):
#     name = models.CharField(max_length=50)
#     field_type_category = models.ForeignKey(
#         FieldTypeCategory, related_name="field_types", on_delete=models.CASCADE
#     )
#     field_data_type = models.ForeignKey(
#         FieldDataType, related_name="field_data_type", on_delete=models.CASCADE
#     )
#     parent = models.ForeignKey(
#         "self",
#         related_name="parent_record",
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#     )
#     default_value = models.CharField(max_length=200, null=True, blank=True)
#     min_value = models.IntegerField(null=True, blank=True)
#     max_value = models.IntegerField(null=True, blank=True)
#     is_multi_select = models.BooleanField(default=False)
#     is_mandatory = models.BooleanField(default=False)
#     is_editable = models.BooleanField(default=True)
#     is_secure = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
#     ordinal = models.IntegerField()

#     class Meta(BaseModel.Meta):
#         ordering = ["-created_at"]

#     def __str__(self):
#         return self.name
