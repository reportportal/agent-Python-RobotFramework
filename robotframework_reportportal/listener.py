import logging
import os
from mimetypes import guess_type

from reportportal_client.helpers import gen_attributes

from .model import Keyword, Test, Suite, LogMessage
from .service import RobotService
from .variables import Variables

ROBOT_LISTENER_API_VERSION = 2

items = []


def start_launch(launch):
    """Start a new launch at the Report Portal."""
    if not Variables.launch_id:
        launch.doc = Variables.launch_doc
        logging.debug("ReportPortal - Start Launch: {0}".format(
            launch.attributes))
        RobotService.start_launch(
            launch_name=Variables.launch_name,
            attributes=gen_attributes(Variables.launch_attributes),
            description=launch.doc)
    else:
        RobotService.rp.launch_id = Variables.launch_id


def start_suite(name, attributes):
    suite = Suite(attributes=attributes)
    if suite.robot_id == "s1":
        Variables.check_variables()
        RobotService.init_service(Variables.endpoint, Variables.project,
                                  Variables.uuid)
        start_launch(suite)
        if not suite.suites:
            attributes['id'] = "s1-s1"
            start_suite(name, attributes)

    else:
        logging.debug("ReportPortal - Start Suite: {0}".format(attributes))
        parent_id = items[-1][0] if items else None
        item_id = RobotService.start_suite(
            name=name,
            suite=suite,
            parent_item_id=parent_id)
        items.append((item_id, parent_id))


def end_suite(_, attributes):
    suite = Suite(attributes=attributes)
    if suite.robot_id == "s1":
        logging.debug(msg="ReportPortal - End Launch: {0}".format(attributes))
        RobotService.finish_launch(launch=suite)
        RobotService.terminate_service()
    else:
        logging.debug("ReportPortal - End Suite: {0}".format(attributes))
        RobotService.finish_suite(item_id=items.pop()[0], suite=suite)


def start_test(name, attributes):
    test = Test(name=name, attributes=attributes)
    logging.debug("ReportPortal - Start Test: {0}".format(attributes))
    parent_item_id = items[-1][0]
    items.append((
        RobotService.start_test(
            test=test,
            parent_item_id=parent_item_id,
            attributes=gen_attributes(Variables.test_attributes + test.tags),
        ),
        parent_item_id))


def end_test(name, attributes):
    test = Test(name=name, attributes=attributes)
    item_id, _ = items.pop()
    logging.debug("ReportPortal - End Test: {0}".format(attributes))
    RobotService.finish_test(item_id=item_id, test=test)


def start_keyword(name, attributes):
    parent_type = 'SUITE' if not items else 'TEST'
    parent_item_id = items[-1][0] if items else None
    kwd = Keyword(name=name, parent_type=parent_type, attributes=attributes)
    logging.debug("ReportPortal - Start Keyword: {0}".format(attributes))
    items.append((
        RobotService.start_keyword(keyword=kwd, parent_item_id=parent_item_id,
                                   has_stats=False),
        parent_item_id))


def end_keyword(name, attributes):
    kwd = Keyword(name=name, attributes=attributes)
    item_id, _ = items.pop()
    logging.debug("ReportPortal - End Keyword: {0}".format(attributes))
    RobotService.finish_keyword(item_id=item_id, keyword=kwd)


def _build_msg_struct(message):
    # Check if message comes from our custom logger or not
    if isinstance(message["message"], LogMessage):
        msg = message["message"]
    else:
        msg = LogMessage(message["message"])
        msg.level = message["level"]

    msg.item_id = items[-1][0]
    return msg


def log_message(message):
    msg = _build_msg_struct(message)
    logging.debug("ReportPortal - Log Message: {0}".format(message))
    RobotService.log(message=msg)


def log_message_with_image(msg, image):
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


def message(message):
    logging.debug("ReportPortal - Message: {0}".format(message))


def library_import(name, attributes):
    logging.debug("ReportPortal - Library Import: {0}".format(attributes))


def resource_import(name, attributes):
    logging.debug("ReportPortal - Resource Import: {0}".format(attributes))


def variables_import(name, attributes):
    logging.debug("ReportPortal - Variables Import: {0}".format(attributes))


def output_file(path):
    logging.debug("ReportPortal - Output File: {0}".format(path))


def log_file(path):
    logging.debug("ReportPortal - Log File: {0}".format(path))


def report_file(path):
    logging.debug("ReportPortal - Report File: {0}".format(path))


def xunit_file(path):
    logging.debug("ReportPortal - XUnit File: {0}".format(path))


def info_file(path):
    logging.debug("ReportPortal - info File: {0}".format(path))
