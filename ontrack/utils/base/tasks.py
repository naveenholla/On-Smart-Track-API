from asgiref.sync import async_to_sync
from celery_progress.backend import ProgressRecorder
from channels.layers import get_channel_layer

from ontrack.lookup.models import Task, TaskLog
from ontrack.utils.datetime import DateTimeHelper as dt
from ontrack.utils.logger import ApplicationLogger


class TaskProgressRecorder:
    def __init__(self, task, websocket_enabled=False):
        self.task = task
        self.task_id = "task_%s" % task.request.id
        self.recorder = ProgressRecorder(task)
        self.channel_layer = get_channel_layer()
        self.task_type = "celery_task_update"
        self.websocket_enabled = websocket_enabled

        self.db_task = Task(
            task_id=task.request.id, task_name=self.task.name, status="In-Progress"
        )
        self.db_task.save()

    def set_task_status(self, status):
        self.db_task.status = status
        self.db_task.save()

    def send_message(self, type_, title, message):
        tasklog = TaskLog(
            task=self.db_task, title=title, message=message, message_type=type_
        )
        tasklog.save()

        if self.websocket_enabled:
            try:
                async_to_sync(self.channel_layer.group_send)(
                    self.task_id,
                    {
                        "type": self.task_type,
                        "message": {
                            "type": type_,
                            "title": title,
                            "message": message,
                            "date": dt.current_dt_display_str(),
                        },
                    },
                )
            except Exception:
                pass

    def send_progress(self, title, total, index):
        self.db_task.total_count = total
        self.db_task.processed_count = index
        self.db_task.save()

        tasklog = TaskLog(
            task=self.db_task,
            title=title,
            message=f"Processed - {index}/{total}",
            message_type="progress",
        )
        tasklog.save()

        if self.websocket_enabled:
            try:
                async_to_sync(self.channel_layer.group_send)(
                    self.task_id,
                    {
                        "type": self.task_type,
                        "message": {
                            "type": "primary",
                            "title": title,
                            "total": total,
                            "index": index,
                            "date": dt.current_dt_display_str(),
                        },
                    },
                )
            except Exception:
                pass


class TaskProgressStatus:
    def __init__(self, recorder: TaskProgressRecorder = None):
        self.logger = ApplicationLogger()
        self.recorder = recorder

    def log_debug(self, message, title=None):
        if not title:
            title = "Debug Message"
        if self.recorder:
            self.recorder.send_message("info", title, message)

    def log_message(self, message, title=None):
        if not title:
            title = "Information"

        if self.recorder:
            self.recorder.send_message("info", title, message)

    def log_warning(self, message, title=None, is_completed=False):
        self.logger.log_warning(message)

        if not title:
            title = "Warning"

        if self.recorder:
            self.recorder.send_message("warning", title, message)

            if is_completed:
                self.recorder.set_task_status("Completed")

    def log_error(self, message, title=None):
        self.logger.log_critical(message)

        if not title:
            title = "Error"

        if self.recorder:
            self.recorder.send_message("danger", title, message)
            self.recorder.set_task_status("Failed")

    def log_critical(self, message, title=None):
        self.logger.log_critical(message)

        if not title:
            title = "Critical Error"

        if self.recorder:
            self.recorder.send_message("danger", title, message)
            self.recorder.set_task_status("Failed")

    def log_start(self, message, title=None):
        self.logger.log_info(message)

        if not title:
            title = "Started"

        if self.recorder:
            self.recorder.send_message("secondary", title, message)

    def log_completed(self, message, title=None):
        self.logger.log_info(message)

        if not title:
            title = "Completed"

        if self.recorder:
            self.recorder.send_message("success", title, message)
            self.recorder.set_task_status("Completed")

    def log_progress(self, index, total, title=None):
        if not title:
            title = "Progress"

        if self.recorder:
            self.recorder.send_progress(title, total, index)

    def log_records_stats(self, stats, title=None, is_completed=False):
        if "message" in stats:
            message = stats["message"]
        elif "created" in stats:
            created = stats["created"]
            updated = stats["updated"]
            message = f"created({created}), updated({updated})"
        elif "deleted" in stats:
            deleted = stats["deleted"]
            message = f"deleted({deleted})"
        else:
            message = "No stats."

        self.logger.log_info(message)

        if not title:
            title = "Stats"

        if self.recorder:
            self.recorder.send_message("success", title, message)

            if is_completed:
                self.recorder.set_task_status("Completed")
