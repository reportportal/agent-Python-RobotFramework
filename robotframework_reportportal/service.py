from time import time
from reportportal_client import (ReportPortalService, FinishExecutionRQ,
                                 StartLaunchRQ, StartTestItemRQ,
                                 FinishTestItemRQ, SaveLogRQ)


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
    def init_service(endpoint, project, uuid):
        if RobotService.rp is None:
            RobotService.rp = ReportPortalService(endpoint=endpoint,
                                                  project=project,
                                                  token=uuid)
        else:
            raise Exception("RobotFrameworkService could not be initialized")

    @staticmethod
    def start_launch(launch_name=None, mode=None, launch=None):
        sl_rq = StartLaunchRQ(name=launch_name,
                              start_time=timestamp(),
                              description=launch.doc,
                              mode=mode,
                              tags=None)
        r = RobotService.rp.start_launch(sl_rq)
        RobotService.launch_id = r.id
        RobotService.stack.append((None, "SUITE"))

    @staticmethod
    def finish_launch(launch=None):
        fl_rq = FinishExecutionRQ(
            end_time=timestamp(),
            status=RobotService.status_mapping[launch.status])
        launch_id = RobotService.launch_id
        RobotService.rp.finish_launch(launch_id, fl_rq)
        RobotService.stack.pop()

    @staticmethod
    def start_suite(name=None, suite=None):
        sta_rq = StartTestItemRQ(name=name, description=suite.doc,
                                 tags=None,
                                 start_time=timestamp(),
                                 launch_id=RobotService.launch_id,
                                 type="SUITE")
        parent_item_id = RobotService._get_top_id_from_stack()
        r = RobotService.rp.start_test_item(
            parent_item_id=parent_item_id, start_test_item_rq=sta_rq)
        RobotService.stack.append((r.id, "SUITE"))

    @staticmethod
    def finish_suite(issue=None, suite=None):
        fta_rq = FinishTestItemRQ(end_time=timestamp(),
                                  status=RobotService.status_mapping[
                                      suite.status],
                                  issue=issue)
        suite_id = RobotService._get_top_id_from_stack()
        RobotService.rp.finish_test_item(
            item_id=suite_id,
            finish_test_item_rq=fta_rq)
        RobotService.stack.pop()

    @staticmethod
    def start_test(test=None):
        sta_rq = StartTestItemRQ(name=test.name, description=test.doc,
                                 tags=test.tags,
                                 start_time=timestamp(),
                                 launch_id=RobotService.launch_id,
                                 type="TEST")
        parent_suite_id = RobotService._get_top_id_from_stack()
        r = RobotService.rp.start_test_item(
            parent_item_id=parent_suite_id, start_test_item_rq=sta_rq)
        RobotService.stack.append((r.id, "TEST"))

    @staticmethod
    def finish_test(issue=None, test=None):
        fta_rq = FinishTestItemRQ(end_time=timestamp(),
                                  status=RobotService.status_mapping[
                                      test.status],
                                  issue=issue)
        test_id = RobotService._get_top_id_from_stack()
        RobotService.rp.finish_test_item(
            item_id=test_id,
            finish_test_item_rq=fta_rq)
        RobotService.stack.pop()

    @staticmethod
    def start_keyword(keyword=None):
        sta_rq = StartTestItemRQ(name=keyword.get_kwd(),
                                 description=keyword.doc, tags=keyword.tags,
                                 start_time=timestamp(),
                                 launch_id=RobotService.launch_id,
                                 type="STEP")
        parent_item_id = RobotService._get_top_id_from_stack()
        RobotService._modify_request(keyword, sta_rq)
        r = RobotService.rp.start_test_item(
            parent_item_id=parent_item_id,
            start_test_item_rq=sta_rq)
        RobotService.stack.append((r.id, "KEYWORD"))

    @staticmethod
    def finish_keyword(issue=None, keyword=None):
        fta_rq = FinishTestItemRQ(end_time=timestamp(),
                                  status=RobotService.status_mapping[
                                      keyword.status],
                                  issue=issue)
        RobotService._send_logs()
        RobotService.rp.finish_test_item(
            item_id=RobotService._get_top_id_from_stack(),
            finish_test_item_rq=fta_rq)
        RobotService.stack.pop()

    @staticmethod
    def log(message):
        sl_rq = SaveLogRQ(item_id=RobotService._get_top_id_from_stack(),
                          time=timestamp(), message=message.message,
                          level=RobotService.log_level_mapping[message.level])
        RobotService.logs.append(sl_rq)

    @staticmethod
    def _get_top_id_from_stack():
        try:
            return RobotService.stack[-1][0]
        except IndexError:
            return None

    @staticmethod
    def _get_top_item_type_from_stack():
        try:
            return RobotService.stack[-1][1]
        except IndexError:
            return "SUITE"

    @staticmethod
    def _modify_request(keyword, sta_rq):
        parent_type = RobotService._get_top_item_type_from_stack()
        if keyword.kwd_type == "Setup":
            sta_rq.type = "BEFORE_{0}".format(parent_type)
        elif keyword.kwd_type == "Teardown":
            sta_rq.type = "AFTER_{0}".format(parent_type)
        else:
            sta_rq.type = "STEP"

    @staticmethod
    def _send_logs():
        def post_log(sl_rq):
            try:
                RobotService.rp.log(sl_rq)
            except Exception:
                pass

        current_item_id = RobotService._get_top_id_from_stack()
        map(post_log, filter(lambda x: x.item_id == current_item_id,
                             RobotService.logs))
        RobotService.logs = []