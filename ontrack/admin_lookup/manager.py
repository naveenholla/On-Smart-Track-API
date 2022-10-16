from ontrack.utils.base.manager import PullManagerAbstarct

from .queryset import SettingQuerySet


class SettingPullManager(PullManagerAbstarct):
    def get_queryset(self):
        return SettingQuerySet(self.model, using=self._db)

    def save_setting(self, key, value):
        return self.get_queryset().update_or_create(
            key=key, defaults={"key": key, "value": value}
        )

    def get_setting(self, key):
        setting = self.get_queryset().filter(key=key).first()

        if setting is None:
            return None

        return setting.value
