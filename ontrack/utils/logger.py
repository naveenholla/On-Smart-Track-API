import inspect
import logging
import traceback

from .context import ContextFilter


class ApplicationLogger:
    def __init__(self):
        self.logger = logging.getLogger("ontrack")
        self.logger.addFilter(ContextFilter())

    def log_info(self, message: str):
        stack = inspect.stack()[1]
        self.logger.info(
            f"[{stack.filename}.{stack.function}({stack.lineno})]: {message}"
        )

    def log_debug(self, message: str):
        stack = inspect.stack()[1]
        self.logger.debug(
            f"[{stack.filename}.{stack.function}({stack.lineno})]: {message}"
        )

    def log_warning(self, message: str):
        stack = inspect.stack()[1]
        self.logger.warning(
            f"[{stack.filename}.{stack.function}({stack.lineno})]: {message}"
        )

    def log_error(self, message: str):
        stack = inspect.stack()[1]
        self.logger.error(
            f"[{stack.filename}.{stack.function}({stack.lineno})]: {message}"
        )

    def log_critical(self, message: str):
        traceback_output = traceback.format_exc()
        self.logger.warning(traceback_output)
        stack = inspect.stack()[1]
        self.logger.critical(
            f"[{stack.filename}.{stack.function}({stack.lineno})]: {message}"
        )
