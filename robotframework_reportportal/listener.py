"""This module includes Robot Framework listener interfaces..

Copyright (c) 2021 http://reportportal.io .
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


import logging
import os
from mimetypes import guess_type

from reportportal_client.helpers import gen_attributes

from .model import Keyword, Test, Suite, LogMessage
from .service import RobotService
from .variables import Variables

items = []
ROBOT_LISTENER_API_VERSION = 2
VARIABLES = Variables()


def start_launch(launch, ts=None):
    """Start a new launch at the Report Portal.

    :param launch: Suite object of the high-level Robot suite.
    :param ts:     Timestamp(used by the ResultVisitor)
    """
    if not VARIABLES.launch_id:
        launch.doc = VARIABLES.launch_doc
        logging.debug("ReportPortal - Start Launch: {0}".format(
            launch.attributes))
        RobotService.start_launch(
            launch_name=VARIABLES.launch_name,
            attributes=gen_attributes(VARIABLES.launch_attributes),
            description=launch.doc,
            mode=VARIABLES.mode,
            ts=ts,
            skip_analytics=VARIABLES.skip_analytics
        )
    else:
        RobotService.rp.launch_id = VARIABLES.launch_id


def start_suite(name, attributes, ts=None):
    """Start a new test suite at the Report Portal.

    :param name:   Test suite name
    :param launch: Dictionary passed by the Robot Framework
    :param ts:     Timestamp(used by the ResultVisitor)
    """
    suite = Suite(attributes=attributes)
    if suite.robot_id == "s1":
        RobotService.init_service(
            VARIABLES.endpoint, VARIABLES.project, VARIABLES.uuid,
            VARIABLES.log_batch_size, VARIABLES.pool_size)
        start_launch(suite, ts)
        if not suite.suites:
            attributes['id'] = "s1-s1"
            start_suite(name, attributes, ts)

    else:
        logging.debug("ReportPortal - Start Suite: {0}".format(attributes))
        parent_id = items[-1][0] if items else None
        item_id = RobotService.start_suite(
            name=name,
            suite=suite,
            parent_item_id=parent_id,
            ts=ts)
        items.append((item_id, parent_id))


def end_suite(_, attributes, ts=None):
    """Finish started test suite at the Report Portal.

    :param attributes: Dictionary passed by the Robot Framework
    :param ts:         Timestamp(used by the ResultVisitor)
    """
    suite = Suite(attributes=attributes)
    if suite.robot_id == "s1":
        logging.debug(msg="ReportPortal - End Launch: {0}".format(attributes))
        RobotService.finish_launch(launch=suite, ts=ts)
        RobotService.terminate_service()
    else:
        logging.debug("ReportPortal - End Suite: {0}".format(attributes))
        item_id = items.pop()[0]
        RobotService.finish_suite(
            item_id=item_id,
            suite=suite,
            ts=ts)


def start_test(name, attributes, ts=None):
    """Start a new test case at the Report Portal.

    :param name:       Test case name
    :param attributes: Dictionary passed by the Robot Framework
    :param ts:         Timestamp(used by the ResultVisitor)
    """
    test = Test(name=name, attributes=attributes)
    logging.debug("ReportPortal - Start Test: {0}".format(attributes))
    parent_item_id = items[-1][0]
    item_id = RobotService.start_test(
        test=test,
        parent_item_id=parent_item_id,
        attributes=gen_attributes(VARIABLES.test_attributes + test.tags),
        ts=ts
    )
    items.append((item_id, parent_item_id))


def end_test(name, attributes, ts=None):
    """Finish started test case at the Report Portal.

    :param attributes: Dictionary passed by the Robot Framework
    :param ts:         Timestamp(used by the ResultVisitor)
    """
    test = Test(name=name, attributes=attributes)
    if not test.critical and test.status == 'FAIL':
        test.status = 'SKIP'
    item_id = items.pop()[0]
    logging.debug('ReportPortal - End Test: {0}'.format(attributes))
    RobotService.finish_test(
        item_id=item_id,
        test=test,
        ts=ts)


def start_keyword(name, attributes, ts=None):
    """Start a new keyword(test step) at the Report Portal.

    :param name:       Keyword name
    :param attributes: Dictionary passed by the Robot Framework
    :param ts:         Timestamp(used by the ResultVisitor)
    """
    parent_type = 'SUITE' if not items else 'TEST'
    parent_item_id = items[-1][0] if items else None
    kwd = Keyword(name=name, parent_type=parent_type, attributes=attributes)
    logging.debug("ReportPortal - Start Keyword: {0}".format(attributes))
    item_id = RobotService.start_keyword(
        keyword=kwd,
        parent_item_id=parent_item_id,
        has_stats=False,
        ts=ts)
    items.append((item_id, parent_item_id))


def end_keyword(name, attributes, ts=None):
    """Finish started keyword at the Report Portal.

    :param attributes: Dictionary passed by the Robot Framework
    :param ts:         Timestamp(used by the ResultVisitor)
    """
    kwd = Keyword(name=name, attributes=attributes)
    item_id, _ = items.pop()
    logging.debug("ReportPortal - End Keyword: {0}".format(attributes))
    RobotService.finish_keyword(
        item_id=item_id,
        keyword=kwd,
        ts=ts)


def _build_msg_struct(message):
    """Check if the given message comes from our custom logger or not.

    :param message: Message passed by the Robot Framework
    """
    if isinstance(message["message"], LogMessage):
        msg = message["message"]
    else:
        msg = LogMessage(message["message"])
        msg.level = message["level"]
    msg.item_id = items[-1][0]
    return msg


def log_message(message):
    """Send log message to the Report Portal.

    :param message: Message passed by the Robot Framework
    """
    msg = _build_msg_struct(message)
    logging.debug("ReportPortal - Log Message: {0}".format(message))
    RobotService.log(message=msg)


def log_message_with_image(msg, image):
    """Send log message to the Report Portal.

    :param msg:   Message passed by the Robot Framework
    :param image: Path to image
    """
    m = _build_msg_struct(msg)
    with open(image, "rb") as fh:
        m.attachment = {
            'name': os.path.basename(image),
            'data': fh.read(),
            'mime': guess_type(image)[0] or "application/octet-stream"
        }
    logging.debug("ReportPortal - Log Message with Image: {0} {1}"
                  .format(m, image))
    RobotService.log(message=m)
