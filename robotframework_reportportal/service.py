import logging
import traceback
from time import time

from reportportal_client.external.google_analytics import send_event
from reportportal_client.helpers import (
    get_launch_sys_attrs,
    get_package_version
)
from reportportal_client.service import (
    _dict_to_payload,
    ReportPortalService
)

from .variables import Variables


def async_error_handler(exc_info):
    exc, msg, tb = exc_info
    traceback.print_exception(exc, msg, tb)


def timestamp():
    return str(int(time() * 1000))


class RobotService(object):
    agent_name = "robotframework-reportportal"
    agent_version = get_package_version(agent_name)
    rp = None

    status_mapping = {
        "PASS": "PASSED",
        "FAIL": "FAILED",
        "SKIP": "SKIPPED"
    }

    log_level_mapping = {
        "INFO": "INFO",
        "FAIL": "ERROR",
        "TRACE": "TRACE",
        "DEBUG": "DEBUG",
        "HTML": "INFO",
        "WARN": "WARN",
        "ERROR": "ERROR"
    }

    @staticmethod
    def _get_launch_attributes(cmd_attrs):
        """Generate launch attributes including both system and user ones.

        :param list cmd_attrs: List for attributes from the command line
        """
        attributes = cmd_attrs or []
        system_attributes = get_launch_sys_attrs()
        system_attributes['agent'] = (
            '{}-{}'.format(RobotService.agent_name,
                           RobotService.agent_version))
        return attributes + _dict_to_payload(system_attributes)

    @staticmethod
    def init_service(endpoint, project, uuid):
        if RobotService.rp is None:
            logging.debug(
                "ReportPortal - Init service: "
                "endpoint={0}, project={1}, uuid={2}"
                .format(endpoint, project, uuid))
            RobotService.rp = ReportPortalService(
                endpoint=endpoint,
                project=project,
                token=uuid)
        else:
            raise Exception("RobotFrameworkService is already initialized")

    @staticmethod
    def terminate_service():
        if RobotService.rp is not None:
            RobotService.rp.terminate()

    @staticmethod
    def start_launch(launch_name, attributes=None,
                     description=None, mode=None):
        """Call start_launch method of the common client.

        :param launch_name: Launch name
        :param attributes:  Launch attributes
        :param description: Launch description
        :param mode:        Launch mode
        :return:            launch UUID
        """
        sl_pt = {
            "attributes": RobotService._get_launch_attributes(attributes),
            "name": launch_name,
            "start_time": timestamp(),
            "description": description,
            "mode": mode
        }
        logging.debug("ReportPortal - Start launch: "
                      "request_body={0}".format(sl_pt))
        if not Variables.skip_analytics:
            send_event(RobotService.agent_name, RobotService.agent_version)
        return RobotService.rp.start_launch(**sl_pt)

    @staticmethod
    def finish_launch(launch=None):
        fl_rq = {
            "end_time": timestamp(),
            "status": RobotService.status_mapping[launch.status]
        }
        logging.debug("ReportPortal - Finish launch: "
                      "request_body={0}".format(fl_rq))
        RobotService.rp.finish_launch(**fl_rq)

    @staticmethod
    def start_suite(name=None, suite=None, parent_item_id=None, attributes=None):
        start_rq = {
            "name": name,
            "attributes": attributes,
            "description": suite.doc,
            "start_time": timestamp(),
            "item_type": "SUITE",
            "parent_item_id": parent_item_id
        }
        logging.debug(
            "ReportPortal - Start suite: "
            "request_body={0}".format(start_rq))
        return RobotService.rp.start_test_item(**start_rq)

    @staticmethod
    def finish_suite(item_id, issue=None, suite=None):
        fta_rq = {
            "end_time": timestamp(),
            "status": RobotService.status_mapping[suite.status],
            "issue": issue,
            "item_id": item_id
        }
        logging.debug(
            "ReportPortal - Finish suite:"
            " request_body={0}".format(fta_rq))
        RobotService.rp.finish_test_item(**fta_rq)

    @staticmethod
    def start_test(test=None, parent_item_id=None, attributes=None):
        # Item type should be sent as "STEP" until we upgrade to RPv6.
        # Details at: https://github.com/reportportal/agent-Python-RobotFramework/issues/56
        start_rq = {
            "name": test.name,
            "attributes": attributes,
            "description": test.doc,
            "start_time": timestamp(),
            "item_type": "STEP",
            "parent_item_id": parent_item_id
        }
        logging.debug(
            "ReportPortal - Start test: "
            "request_body={0}".format(start_rq))
        return RobotService.rp.start_test_item(**start_rq)

    @staticmethod
    def finish_test(item_id, issue=None, test=None):
        fta_rq = {
            "end_time": timestamp(),
            "status": RobotService.status_mapping[test.status],
            "issue": issue,
            "item_id": item_id
        }
        logging.debug(
            "ReportPortal - Finish test:"
            " request_body={0}".format(fta_rq))
        RobotService.rp.finish_test_item(**fta_rq)

    @staticmethod
    def start_keyword(keyword=None, parent_item_id=None, has_stats=True):
        start_rq = {
            "name": keyword.get_name(),
            "description": keyword.doc,
            "start_time": timestamp(),
            "item_type": keyword.get_type(),
            "parent_item_id": parent_item_id,
            "has_stats": has_stats
        }
        logging.debug(
            "ReportPortal - Start keyword: "
            "request_body={0}".format(start_rq))
        return RobotService.rp.start_test_item(**start_rq)

    @staticmethod
    def finish_keyword(item_id, issue=None, keyword=None):
        fta_rq = {
            "end_time": timestamp(),
            "status": RobotService.status_mapping[keyword.status],
            "issue": issue,
            "item_id": item_id
        }
        logging.debug(
            "ReportPortal - Finish keyword:"
            " request_body={0}".format(fta_rq))
        RobotService.rp.finish_test_item(**fta_rq)

    @staticmethod
    def log(message):
        sl_rq = {
            "time": timestamp(),
            "message": message.message,
            "level": RobotService.log_level_mapping[message.level],
            "attachment": message.attachment,
            "item_id": message.item_id
        }
        RobotService.rp.log(**sl_rq)
