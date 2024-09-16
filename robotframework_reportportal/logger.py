#  Copyright 2022 EPAM Systems
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""ReportPortal logging API for test libraries with support for attachments.

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
                "mime": "text/plain",
            },
        )
"""
from typing import Optional, Dict

from robot.api import logger

from robotframework_reportportal.model import LogMessage


def write(msg: str, level: str = 'INFO', html: bool = False, attachment: Optional[Dict[str, str]] = None,
          launch_log: bool = False) -> None:
    """Write the message to the log file using the given level.

    Valid log levels are ``TRACE``, ``DEBUG``, ``INFO`` (default since RF 2.9.1), ``WARN``,
    and ``ERROR`` (new in RF 2.9). Additionally, it is possible to use ``HTML`` pseudo log level that logs the message
    as HTML using the ``INFO`` level.

    Attachment should contain a dict with "name", "data" and "mime" values defined. See module example.

    Instead of using this method, it is generally better to use the level specific methods such as ``info`` and
    ``debug`` that have separate

    :param msg:        argument to control the message format.
    :param level:      log level
    :param html:       format or not format the message as html.
    :param attachment: a binary content to attach to the log entry
    :param launch_log: put the log entry on Launch level
    """
    log_message = LogMessage(msg)
    log_message.level = level
    log_message.attachment = attachment
    log_message.launch_log = launch_log
    logger.write(log_message, level, html)


def trace(msg: str, html: bool = False, attachment: Optional[Dict[str, str]] = None, launch_log: bool = False) -> None:
    """Write the message to the log file using the ``TRACE`` level."""
    write(msg, "TRACE", html, attachment, launch_log)


def debug(msg: str, html: bool = False, attachment: Optional[Dict[str, str]] = None, launch_log: bool = False) -> None:
    """Write the message to the log file using the ``DEBUG`` level."""
    write(msg, "DEBUG", html, attachment, launch_log)


def info(msg: str, html: bool = False, also_console: bool = False, attachment: Optional[Dict[str, str]] = None,
         launch_log: bool = False):
    """Write the message to the log file using the ``INFO`` level.

    If ``also_console`` argument is set to ``True``, the message is written both to the log file and to the console.
    """
    write(msg, "INFO", html, attachment, launch_log)
    if also_console:
        console(msg)


def warn(msg: str, html: bool = False, attachment: Optional[Dict[str, str]] = None, launch_log: bool = False) -> None:
    """Write the message to the log file using the ``WARN`` level."""
    write(msg, 'WARN', html, attachment, launch_log)


def error(msg: str, html: bool = False, attachment: Optional[Dict[str, str]] = None, launch_log: bool = False) -> None:
    """Write the message to the log file using the ``ERROR`` level."""
    write(msg, 'ERROR', html, attachment, launch_log)


def console(msg: str, newline: bool = True, stream: str = 'stdout') -> None:
    """Write the message to the console.

    If the ``newline`` argument is ``True``, a newline character is automatically added to the message.

    By default, the message is written to the standard output stream.
    Using the standard error stream is possibly by giving the ``stream`` argument value ``'stderr'``.
    """
    logger.console(msg, newline, stream)
