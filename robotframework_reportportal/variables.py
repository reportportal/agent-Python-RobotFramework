from robot.libraries.BuiltIn import BuiltIn

from .exception import RobotServiceException


def get_variable(name, default=None):
    return BuiltIn().get_variable_value("${" + name + "}", default=default)


class Variables(object):
    uuid = None
    endpoint = None
    launch_name = None
    project = None
    launch_doc = None
    report_level = None
    report_logs = None

    REPORT_LEVELS = ["test", "keyword"]

    @staticmethod
    def check_variables():
        Variables.uuid = get_variable("RP_UUID", default=None)
        if Variables.uuid is None:
            raise RobotServiceException(
                "Didn't passed parameter RP_UUID for robot run\n"
                "You should pass -v RP_UUID:<uuid_value>")
        Variables.endpoint = get_variable("RP_ENDPOINT", default=None)
        if Variables.endpoint is None:
            raise RobotServiceException(
                "Didn't passed parameter RP_ENDPOINT for robot run\n"
                "You should pass -v RP_RP_ENDPOINT:<endpoint_value>")
        Variables.launch_name = get_variable("RP_LAUNCH", default=None)
        if Variables.launch_name is None:
            raise RobotServiceException(
                "Didn't passed parameter RP_LAUNCH for robot run\n"
                "You should pass -v RP_LAUNCH:<launch_name_value>")
        Variables.project = get_variable("RP_PROJECT", default=None)
        if Variables.project is None:
            raise RobotServiceException(
                "Didn't passed parameter RP_PROJECT for robot run\n"
                "You should pass -v RP_PROJECT:<project_name_value>")
        Variables.launch_doc = get_variable("RP_LAUNCH_DOC", default=None)
        Variables.report_level = get_variable("RP_REPORT_LEVEL",
                                              default="keyword")
        if Variables.report_level not in Variables.REPORT_LEVELS:
            Variables.report_level = "keyword"
        Variables.report_logs = get_variable("RP_REPORT_LOGS", default="yes")
