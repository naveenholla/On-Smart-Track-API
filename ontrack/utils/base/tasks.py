from asgiref.sync import async_to_sync
from celery_progress.backend import ProgressRecorder
from channels.layers import get_channel_layer

from ontrack.utils.logger import ApplicationLogger


class TaskProgressRecorder:
    def __init__(self, task):
        self.task = task
        self.task_id = "task_%s" % task.request.id
        self.recorder = ProgressRecorder(task)
        self.channel_layer = get_channel_layer()
        self.task_type = "celery_task_update"

    def send_message(self, type_, message):
        async_to_sync(self.channel_layer.group_send)(
            self.task_id,
            {"type": self.task_type, "message": {"type": type_, "message": message}},
        )

    def send_progress(self, total, index):
        async_to_sync(self.channel_layer.group_send)(
            self.task_id,
            {
                "type": self.task_type,
                "message": {"type": "progress", "total": total, "index": index},
            },
        )


class TaskProgressStatus:
    def __init__(self, recorder: TaskProgressRecorder = None):
        self.logger = ApplicationLogger()
        self.recorder = recorder

    def log_debug(self, message):
        self.logger.log_debug(message)
        self.recorder.send_message("debug", message)

    def log_message(self, message):
        self.logger.log_info(message)
        self.recorder.send_message("message", message)

    def log_warning(self, message):
        self.logger.log_warning(message)
        self.recorder.send_message("warning", message)

    def log_error(self, message):
        self.logger.log_critical(message)
        self.recorder.send_message("error", message)
        print(message)

    def log_critical(self, message):
        self.logger.log_critical(message)
        self.recorder.send_message("critical", message)
        print(message)

    def log_start(self, message):
        self.logger.log_info(message)
        self.recorder.send_message("start", message)
        print(message)

    def log_completed(self, message):
        self.logger.log_info(message)
        self.recorder.send_message("completed", message)

    def log_progress(self, index, total):
        self.recorder.send_progress(total, index)

    def log_records_stats(self, stats):
        if "message" in stats:
            message = stats["message"]
        elif "created" in stats:
            created = stats["created"]
            updated = stats["updated"]
            message = f"created({created}), updated({updated})"
        else:
            message = "No stats."
        self.recorder.send_message("stats", message)
