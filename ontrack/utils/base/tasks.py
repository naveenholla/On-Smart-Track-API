from celery_progress.backend import ProgressRecorder

from ontrack.utils.logger import ApplicationLogger


class TaskProgressStatus:
    def __init__(self, recorder: ProgressRecorder = None):
        self.logger = ApplicationLogger()
        self.recorder = recorder

    def log_debug(self, message):
        self.logger.log_debug(message)

    def log_message(self, message):
        self.logger.log_info(message)

    def log_warning(self, message):
        self.logger.log_warning(message)

    def log_error(self, message):
        self.logger.log_critical(message)
        print(message)

    def log_critical(self, message):
        self.logger.log_critical(message)
        print(message)

    def log_start(self, message):
        self.logger.log_info(message)
        print(message)

    def log_completed(self, message):
        self.logger.log_info(message)
        print(message)

    def log_progress(self, index, total):
        print(f"{index} / {total} ({index/total*100}%)")

    def log_records_stats(self, stats):
        if "message" in stats:
            message = stats["message"]
        elif "created" in stats:
            created = stats["created"]
            updated = stats["updated"]
            message = f"created({created}), updated({updated})"
        else:
            message = "No stats."
        print(message)
