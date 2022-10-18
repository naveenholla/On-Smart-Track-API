import inspect
import logging
import traceback

from .context import ContextFilter


class ApplicationLogger:
    def __init__(self):
        self.logger = logging.getLogger("ontrack")
        self.logger.addFilter(ContextFilter())

    def log_info(self, message: str):
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
        """

        stack = inspect.stack()[1]
        self.logger.info(
            f"[{stack.filename}.{stack.function}({stack.lineno})]: {message}"
        )

    def log_debug(self, message: str):
        """
        Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
        """

        stack = inspect.stack()[1]
        self.logger.debug(
            f"[{stack.filename}.{stack.function}({stack.lineno})]: {message}"
        )

    def log_warning(self, message: str):
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
        """
        stack = inspect.stack()[1]
        self.logger.warning(
            f"[{stack.filename}.{stack.function}({stack.lineno})]: {message}"
        )

    def log_error(self, message: str):
        """
        Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=1)
        """
        stack = inspect.stack()[1]
        self.logger.error(
            f"[{stack.filename}.{stack.function}({stack.lineno})]: {message}"
        )

    def log_critical(self, message: str):
        """
        Log 'msg % args' with severity 'CRITICAL'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.critical("Houston, we have a %s", "major disaster", exc_info=1)
        """
        traceback_output = traceback.format_exc()
        self.logger.warning(traceback_output)
        stack = inspect.stack()[1]
        self.logger.critical(
            f"[{stack.filename}.{stack.function}({stack.lineno})]: {message}"
        )
