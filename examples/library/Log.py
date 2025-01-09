#  Copyright 2024 EPAM Systems
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Logging library for Robot Framework."""

from reportportal_client.helpers import guess_content_type_from_bytes

from robotframework_reportportal import logger


def item_log(level, message, attachment=None, html=False):
    """
    Post a log entry on which will be attached to the current processing item.

    :param level: log entry level
    :param message: message to post
    :param attachment: path to attachment file
    :param html: format or not format the message as html
    """
    logger.write(message, level, attachment=attachment, html=html)


def launch_log(level, message, attachment=None):
    """
    Post a log entry which will be attached to the launch.

    :param level: log entry level
    :param message: message to post
    :param attachment: path to attachment file
    """
    logger.write(message, level, attachment=attachment, launch_log=True)


def binary_log(level: str, message: str, file_name: str, attachment: bytes):
    """
    Post a log entry with binary attachment.

    :param level: log entry level
    :param message: message to post
    :param file_name: name of the attachment file
    :param attachment: binary data to attach
    """
    logger.write(
        message,
        level,
        attachment={
            "name": file_name,
            "data": attachment,
            "mime": guess_content_type_from_bytes(attachment),
        },
        launch_log=False,
    )
