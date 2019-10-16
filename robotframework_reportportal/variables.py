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
    log_batch_size = None
    launch_tags = None

    @staticmethod
    def check_variables():
        Variables.uuid = get_variable("RP_UUID", default=None)
        if Variables.uuid is None:
            raise RobotServiceException(
                "Missing parameter RP_UUID for robot run\n"
                "You should pass -v RP_UUID:<uuid_value>")
        Variables.endpoint = get_variable("RP_ENDPOINT", default=None)
        if Variables.endpoint is None:
            raise RobotServiceException(
                "Missing parameter RP_ENDPOINT for robot run\n"
                "You should pass -v RP_RP_ENDPOINT:<endpoint_value>")
        Variables.launch_name = get_variable("RP_LAUNCH", default=None)
        if Variables.launch_name is None:
            raise RobotServiceException(
                "Missing parameter RP_LAUNCH for robot run\n"
                "You should pass -v RP_LAUNCH:<launch_name_value>")
        Variables.project = get_variable("RP_PROJECT", default=None)
        if Variables.project is None:
            raise RobotServiceException(
                "Missing parameter RP_PROJECT for robot run\n"
                "You should pass -v RP_PROJECT:<project_name_value>")
        Variables.launch_doc = get_variable("RP_LAUNCH_DOC", default=None)
        Variables.launch_tags = get_variable("RP_LAUNCH_TAGS", default="").split(" ")
        Variables.log_batch_size = int(get_variable("RP_LOG_BATCH_SIZE", default="20"))
