from ontrack.utils.base.manager import BackendManagerAbstarct

from .queryset import SettingQuerySet, TaskQuerySet


class SettingBackendManager(BackendManagerAbstarct):
    def get_queryset(self):
        return SettingQuerySet(self.model, using=self._db)

    def save_setting(self, key, value, key_type):
        return self.get_queryset().update_or_create(
            key=key, defaults={"key": key, "value": value, "key_type": key_type}
        )

    def get_setting(self, key):
        setting = self.get_queryset().filter(key=key).first()

        if setting is None:
            return None

        return setting.value


class TaskBackendManager(BackendManagerAbstarct):
    def get_queryset(self):
        return TaskQuerySet(self.model, using=self._db)
