from asgiref.sync import async_to_sync
from celery_progress.backend import ProgressRecorder
from channels.layers import get_channel_layer

from ontrack.utils.datetime import DateTimeHelper as dt
from ontrack.utils.logger import ApplicationLogger


class TaskProgressRecorder:
    def __init__(self, task):
        self.task = task
        self.task_id = "task_%s" % task.request.id
        self.recorder = ProgressRecorder(task)
        self.channel_layer = get_channel_layer()
        self.task_type = "celery_task_update"

    def send_message(self, type_, title, message):
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

    def log_debug(self, message):
        self.logger.log_debug(message)
        self.recorder.send_message("info", "Debug Message", message)

    def log_message(self, message):
        self.logger.log_info(message)
        self.recorder.send_message("info", "Information", message)

    def log_warning(self, message):
        self.logger.log_warning(message)
        self.recorder.send_message("warning", "Warning", message)

    def log_error(self, message):
        self.logger.log_critical(message)
        self.recorder.send_message("danger", "Error", message)
        print(message)

    def log_critical(self, message):
        self.logger.log_critical(message)
        self.recorder.send_message("danger", "Critical Error", message)
        print(message)

    def log_start(self, message):
        self.logger.log_info(message)
        self.recorder.send_message("secondary", "Started", message)
        print(message)

    def log_completed(self, message):
        self.logger.log_info(message)
        self.recorder.send_message("success", "Completed", message)

    def log_progress(self, index, total):
        self.recorder.send_progress("Progress", index)

    def log_records_stats(self, stats):
        if "message" in stats:
            message = stats["message"]
        elif "created" in stats:
            created = stats["created"]
            updated = stats["updated"]
            message = f"created({created}), updated({updated})"
        else:
            message = "No stats."
        self.recorder.send_message("success", "Stats", message)
