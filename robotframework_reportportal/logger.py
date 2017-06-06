"""Report Portal logging API for test libraries with support for attachments.

Usage of this logger is similar to the standard robot.api.logger with addition
of an extra kwarg "attachment" to all logging functions.

Example
-------

import subprocess
from robotframework_reportportal import logger

class MyLibrary(object):

    def log_free_memory(self):
        logger.debug("Collecting free memory statistics!")
        logger.debug(
            "Memory consumption report",
            attachment={
                "name": "free_memory.txt",
                "data": subprocess.check_output("free -h".split()),
                "mime": "application/octet-stream",
            },
        )
"""

from robot.api import logger
from .model import LogMessage


def write(msg, level="INFO", html=False, attachment=None):
    """Writes the message to the log file using the given level.

    Valid log levels are ``TRACE``, ``DEBUG``, ``INFO`` (default since RF
    2.9.1), ``WARN``, and ``ERROR`` (new in RF 2.9). Additionally it is
    possible to use ``HTML`` pseudo log level that logs the message as HTML
    using the ``INFO`` level.

    Attachment should contain a dict with "name", "data" and "mime" values
    defined. See module example.

    Instead of using this method, it is generally better to use the level
    specific methods such as ``info`` and ``debug`` that have separate
    ``html`` argument to control the message format.
    """
    log_message = LogMessage(msg)
    log_message.level = level
    log_message.attachment = attachment
    logger.write(log_message, level, html)


def trace(msg, html=False, attachment=None):
    """Writes the message to the log file using the ``TRACE`` level."""
    write(msg, "TRACE", html, attachment)


def debug(msg, html=False, attachment=None):
    """Writes the message to the log file using the ``DEBUG`` level."""
    write(msg, "DEBUG", html, attachment)


def info(msg, html=False, also_console=False, attachment=None):
    """Writes the message to the log file using the ``INFO`` level.

    If ``also_console`` argument is set to ``True``, the message is
    written both to the log file and to the console.
    """
    write(msg, "INFO", html, attachment)
    if also_console:
        console(msg)


def warn(msg, html=False, attachment=None):
    """Writes the message to the log file using the ``WARN`` level."""
    write(msg, "WARN", html, attachment)


def error(msg, html=False, attachment=None):
    """Writes the message to the log file using the ``ERROR`` level."""
    write(msg, "ERROR", html, attachment)


def console(msg, newline=True, stream="stdout"):
    """Writes the message to the console.

    If the ``newline`` argument is ``True``, a newline character is
    automatically added to the message.

    By default the message is written to the standard output stream.
    Using the standard error stream is possibly by giving the ``stream``
    argument value ``'stderr'``.
    """
    logger.console(msg, newline, stream)
