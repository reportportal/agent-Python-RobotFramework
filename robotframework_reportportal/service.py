import logging
import traceback
from time import time
from reportportal_client import ReportPortalServiceAsync
from .variables import Variables


def async_error_handler(exc_info):
    exc, msg, tb = exc_info
    traceback.print_exception(exc, msg, tb)


def timestamp():
    return str(int(time() * 1000))


class RobotService(object):
    rp = None
    launch_id = None

    status_mapping = {
        "PASS": "PASSED",
        "FAIL": "FAILED",
        "SKIP": "SKIPPED"
    }

    log_level_mapping = {
        "INFO": "INFO",
        "FAIL": "ERROR",
        "TRACE": "TRACE",
        "DEBUG": "DEBUG"
    }

    stack = []
    logs = []

    @staticmethod
    def init_service(endpoint, project, uuid, log_batch_size):
        if RobotService.rp is None:
            logging.debug(
                msg="ReportPortal - Init service: "
                    "endpoint={0}, project={1}, uuid={2}".format(endpoint,
                                                                 project,
                                                                 uuid))
            RobotService.rp = ReportPortalServiceAsync(endpoint=endpoint,
                                                       project=project,
                                                       token=uuid,
                                                       error_handler=async_error_handler,
                                                       log_batch_size=log_batch_size)
        else:
            raise Exception("RobotFrameworkService is already initialized")

    @staticmethod
    def terminate_service():
        if RobotService.rp is not None:
            RobotService.rp.terminate()

    @staticmethod
    def start_launch(launch_name, mode=None, launch=None):
        sl_pt = {
            "name": launch_name,
            "start_time": timestamp(),
            "description": launch.doc,
            "mode": mode,
            "tags": Variables.launch_tags
        }
        logging.debug("ReportPortal - Start launch: "
                      "request_body=%s", sl_pt)
        req_data = RobotService.rp.start_launch(**sl_pt)
        logging.debug("ReportPortal - Launch started: "
                      "response_body=%s", req_data)

    @staticmethod
    def finish_launch(launch=None):
        fl_rq = {
            "end_time": timestamp(),
            "status": RobotService.status_mapping[launch.status]
        }
        logging.debug("ReportPortal - Finish launch: "
                      "request_body=%s", fl_rq)
        RobotService.rp.finish_launch(**fl_rq)

    @staticmethod
    def start_suite(name=None, suite=None):
        start_rq = {
            "name": name,
            "description": suite.doc,
            "tags": None,
            "start_time": timestamp(),
            "item_type": "SUITE"
        }
        logging.debug(
            "ReportPortal - Start suite: "
            "request_body=%s", start_rq)
        RobotService.rp.start_test_item(**start_rq)

    @staticmethod
    def finish_suite(issue=None, suite=None):
        fta_rq = {
            "end_time": timestamp(),
            "status": RobotService.status_mapping[suite.status],
            "issue": issue
        }
        logging.debug(
            "ReportPortal - Finish suite:"
            " request_body=%s", fta_rq)
        RobotService.rp.finish_test_item(**fta_rq)

    @staticmethod
    def start_test(test=None):
        start_rq = {
            "name": test.name,
            "description": test.doc,
            "tags": test.tags,
            "start_time": timestamp(),
            "item_type": "TEST"
        }
        logging.debug(
            "ReportPortal - Start test: "
            "request_body=%s", start_rq)
        RobotService.rp.start_test_item(**start_rq)

    @staticmethod
    def finish_test(issue=None, test=None):
        fta_rq = {
            "end_time": timestamp(),
            "status": RobotService.status_mapping[test.status],
            "issue": issue
        }
#        if Variables.report_level == "test":
#            RobotService._send_logs()
        logging.debug(
            "ReportPortal - Finish test:"
            " request_body=%s", fta_rq)
        RobotService.rp.finish_test_item(**fta_rq)

    @staticmethod
    def start_keyword(keyword=None):
        start_rq = {
            "name": keyword.get_kwd(),
            "description": keyword.doc,
            "tags": keyword.tags,
            "start_time": timestamp(),
            "item_type": "STEP"
        }
#        RobotService._modify_request(keyword, start_rq)
        logging.debug(
            "ReportPortal - Start keyword: "
            "request_body=%s", start_rq)
        RobotService.rp.start_test_item(**start_rq)

    @staticmethod
    def finish_keyword(issue=None, keyword=None):
        fta_rq = {
            "end_time": timestamp(),
            "status": RobotService.status_mapping[keyword.status],
            "issue": issue
        }
#        if Variables.report_level == "keyword":
#            RobotService._send_logs()
        logging.debug(
            "ReportPortal - Finish keyword:"
            " request_body=%s", fta_rq)
        RobotService.rp.finish_test_item(**fta_rq)

    @staticmethod
    def log(message, attachment=None):
        sl_rq = {
            "time": timestamp(),
            "message": message.message,
            "level": RobotService.log_level_mapping[message.level],
            "attachment": attachment,
        }
        RobotService.rp.log(**sl_rq)

#    @staticmethod
#    def _get_top_item_type_from_stack():
#        try:
#            return RobotService.stack[-1][1]
#        except IndexError:
#            return "SUITE"
#
#    @staticmethod
#    def _modify_request(keyword, start_rq):
#        parent_type = RobotService._get_top_item_type_from_stack()
#        if keyword.kwd_type == "Setup":
#            sta_rq.type = "BEFORE_{0}".format(parent_type)
#        elif keyword.kwd_type == "Teardown":
#            sta_rq.type = "AFTER_{0}".format(parent_type)
#        else:
#            sta_rq.type = "STEP"

#    @staticmethod
#    def _send_logs():
#        def post_log(sl_rq):
#            try:
#                logging.debug(msg="ReportPortal - Post log: "
#                                  "request_body={0}".format(sl_rq.data))
#                RobotService.rp.log(sl_rq)
#            except Exception:
#                pass
#
#        current_item_id = RobotService._get_top_id_from_stack()
#        map(post_log, filter(lambda x: x.item_id == current_item_id,
#                             RobotService.logs))
#        RobotService.logs = []
