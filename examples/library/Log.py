"""Logging library for Robot Framework."""

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

import os

from robotframework_reportportal import logger


def screenshot_log(level, message, screenshot_file):
    """
    Attach a screenshot file into a log entry on ReportPortal.

    :param level: log entry level
    :param message: screenshot description
    :param screenshot_file: path to image file
    """
    with open(screenshot_file, "rb") as image_file:
        file_data = image_file.read()
    item_log(level, message, {"name": screenshot_file.split(os.path.sep)[-1],
                              "data": file_data,
                              "mime": "image/png"})


def item_log(level, message, attachment=None):
    """
    Post a log entry on which will be attached to the current processing item.

    :param level: log entry level
    :param message: message to post
    :param attachment: path to attachment file
    """
    logger.write(message, level, attachment=attachment)


def launch_log(level, message, attachment=None):
    """
    Post a log entry which will be attached to the launch.

    :param level: log entry level
    :param message: message to post
    :param attachment: path to attachment file
    """
    logger.write(message, level, attachment=attachment, launch_log=True)
