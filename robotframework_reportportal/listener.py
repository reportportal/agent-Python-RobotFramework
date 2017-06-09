import logging

from .variables import Variables
from .model import Keyword, Test, Suite, LogMessage
from .service import RobotService

ROBOT_LISTENER_API_VERSION = 2


class ParentTypes(object):

    items = []

    @staticmethod
    def push(item):
        ParentTypes.items.append(item)

    @staticmethod
    def pop():
        return ParentTypes.items.pop()

    @staticmethod
    def peek():
        return ParentTypes.items[-1]

    @staticmethod
    def is_empty():
        return ParentTypes.items == []


def start_suite(name, attributes):
    suite = Suite(attributes=attributes)
    ParentTypes.push("SUITE")
    if attributes["id"] == "s1":
        Variables.check_variables()
        RobotService.init_service(Variables.endpoint, Variables.project,
                                  Variables.uuid, Variables.log_batch_size)
        suite.doc = Variables.launch_doc
        logging.debug("ReportPortal - Start Launch: {0}".format(attributes))
        RobotService.start_launch(launch_name=Variables.launch_name,
                                  launch=suite)
    else:
        logging.debug("ReportPortal - Start Suite: {0}".format(attributes))
        RobotService.start_suite(name=name, suite=suite)


def end_suite(name, attributes):
    suite = Suite(attributes=attributes)
    ParentTypes.pop()
    if attributes["id"] == "s1":
        logging.debug(msg="ReportPortal - End Launch: {0}".format(attributes))
        RobotService.finish_launch(launch=suite)
        RobotService.terminate_service()
    else:
        logging.debug("ReportPortal - End Suite: {0}".format(attributes))
        RobotService.finish_suite(suite=suite)


def start_test(name, attributes):
    test = Test(name=name, attributes=attributes)
    ParentTypes.push("TEST")
    logging.debug("ReportPortal - Start Test: {0}".format(attributes))
    RobotService.start_test(test=test)


def end_test(name, attributes):
    test = Test(name=name, attributes=attributes)
    ParentTypes.pop()
    logging.debug("ReportPortal - End Test: {0}".format(attributes))
    RobotService.finish_test(test=test)


def start_keyword(name, attributes):
    parent_type = "SUITE" if ParentTypes.is_empty() else ParentTypes.peek()
    kwd = Keyword(name=name, parent_type=parent_type, attributes=attributes)
    logging.debug("ReportPortal - Start Keyword: {0}".format(attributes))
    RobotService.start_keyword(keyword=kwd)


def end_keyword(name, attributes):
    kwd = Keyword(name=name, attributes=attributes)
    logging.debug("ReportPortal - End Keyword: {0}".format(attributes))
    RobotService.finish_keyword(keyword=kwd)


def log_message(message):
    # Check if message comes from our custom logger or not
    if isinstance(message["message"], LogMessage):
        msg = message["message"]
    else:
        msg = LogMessage(message["message"])
        msg.level = message["level"]

    logging.debug("ReportPortal - Log Message: {0}".format(message))
    RobotService.log(message=msg)


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


def debug_file(path):
    logging.debug("ReportPortal - Debug File: {0}".format(path))
