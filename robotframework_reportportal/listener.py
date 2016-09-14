from .variables import Variables
from .model import Keyword, Test, Suite, LogMessage
from .service import RobotService

ROBOT_LISTENER_API_VERSION = 2


def start_suite(name, attributes):
    suite = Suite(attributes=attributes)
    if attributes["id"] == "s1":
        Variables.check_variables()
        RobotService.init_service(Variables.endpoint, Variables.project,
                                  Variables.uuid)
        suite.doc = Variables.launch_doc
        RobotService.start_launch(launch_name=Variables.launch_name,
                                  launch=suite)
    else:
        RobotService.start_suite(
            name=name, suite=suite)


def end_suite(name, attributes):
    suite = Suite(attributes=attributes)
    if attributes["id"] == "s1":
        RobotService.finish_launch(launch=suite)
    else:
        RobotService.finish_suite(suite=suite)


def start_test(name, attributes):
    test = Test(name=name, attributes=attributes)
    RobotService.start_test(test=test)


def end_test(name, attributes):
    test = Test(name=name, attributes=attributes)
    RobotService.finish_test(test=test)


def start_keyword(name, attributes):
    kwd = Keyword(attributes=attributes)
    RobotService.start_keyword(keyword=kwd)


def end_keyword(name, attributes):
    kwd = Keyword(attributes=attributes)
    RobotService.finish_keyword(keyword=kwd)


def log_message(message):
    msg = LogMessage(message)
    RobotService.log(message=msg)


def message(message):
    pass


def library_import(name, attributes):
    pass


def resource_import(name, attributes):
    pass


def variables_import(name, attributes):
    pass


def output_file(path):
    pass


def log_file(path):
    pass


def report_file(path):
    pass


def xunit_file(path):
    pass


def debug_file(path):
    pass


def close():
    pass
