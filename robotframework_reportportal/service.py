"""This module includes Robot service for reporting results to Report Portal.

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

from reportportal_client.external.google_analytics import send_event
from reportportal_client.helpers import (
    get_launch_sys_attrs,
    get_package_version,
    timestamp
)
from reportportal_client.service import (
    _dict_to_payload,
    ReportPortalService
)


class RobotService(object):
    """Class represents service that sends Robot items to Report Portal."""

    agent_name = "robotframework-reportportal"
    agent_version = get_package_version(agent_name)
    rp = None

    status_mapping = {
        "PASS": "PASSED",
        "FAIL": "FAILED",
        "NOT RUN": "SKIPPED",
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
    def init_service(endpoint, project, uuid, log_batch_size, pool_size):
        """Initialize common reportportal client.

        :param endpoint:       Report Portal API endpoint
        :param project:        Report Portal project
        :param uuid:           API token
        :param log_batch_size: Number of logs to be sent within one batch
        :param pool_size:      HTTPAdapter max pool size
        """
        if RobotService.rp is None:
            logging.debug(
                "ReportPortal - Init service: "
                "endpoint={0}, project={1}, uuid={2}"
                .format(endpoint, project, uuid))
            RobotService.rp = ReportPortalService(
                endpoint=endpoint,
                project=project,
                token=uuid,
                log_batch_size=log_batch_size,
                max_pool_size=pool_size)
        else:
            raise Exception("RobotFrameworkService is already initialized")

    @staticmethod
    def terminate_service():
        """Terminate common reportportal client."""
        if RobotService.rp is not None:
            RobotService.rp.terminate()

    @staticmethod
    def start_launch(launch_name, attributes=None, description=None,
                     mode=None, ts=None, skip_analytics=False):
        """Call start_launch method of the common client.

        :param launch_name:    Launch name
        :param attributes:     Launch attributes
        :param description:    Launch description
        :param mode:           Launch mode
        :param ts:             Start time
        :param skip_analytics: Skip reporting of agent name and version to GA?
        :return:               launch UUID
        """
        sl_pt = {
            "attributes": RobotService._get_launch_attributes(attributes),
            "name": launch_name,
            "start_time": ts or timestamp(),
            "description": description,
            "mode": mode
        }
        logging.debug("ReportPortal - Start launch: "
                      "request_body={0}".format(sl_pt))
        if not skip_analytics:
            send_event(RobotService.agent_name, RobotService.agent_version)
        return RobotService.rp.start_launch(**sl_pt)

    @staticmethod
    def finish_launch(launch=None, ts=None):
        """Finish started launch.

        :param launch: Launch name
        :param ts:     End time
        """
        fl_rq = {
            "end_time": ts or timestamp(),
            "status": RobotService.status_mapping[launch.status]
        }
        logging.debug("ReportPortal - Finish launch: "
                      "request_body={0}".format(fl_rq))
        RobotService.rp.finish_launch(**fl_rq)

    @staticmethod
    def start_suite(name=None, suite=None, parent_item_id=None,
                    attributes=None, ts=None):
        """Call start_test method of the common client.

        :param name:           Test suite name
        :param suite:          model.Suite object
        :param parent_item_id: Parent item UUID
        :param attributes:     attributes of the test suite
        :param ts:             Start time
        :return:               Suite UUID
        """
        start_rq = {
            "name": name,
            "attributes": attributes,
            "description": suite.doc,
            "start_time": ts or timestamp(),
            "item_type": "SUITE",
            "parent_item_id": parent_item_id
        }
        logging.debug(
            "ReportPortal - Start suite: "
            "request_body={0}".format(start_rq))
        return RobotService.rp.start_test_item(**start_rq)

    @staticmethod
    def finish_suite(item_id, issue=None, suite=None, ts=None):
        """Finish started suite.

        :param item_id: UUID of the started suite item
        :param issue:   Corresponding issue if it exists
        :param suite:   model.Suite object
        :param ts:      End time
        """
        fta_rq = {
            "end_time": ts or timestamp(),
            "status": RobotService.status_mapping[suite.status],
            "issue": issue,
            "item_id": item_id
        }
        logging.debug(
            "ReportPortal - Finish suite:"
            " request_body={0}".format(fta_rq))
        RobotService.rp.finish_test_item(**fta_rq)

    @staticmethod
    def start_test(test=None, parent_item_id=None, attributes=None, ts=None):
        """Call start_test method of the common client.

        :param test:           model.Test object
        :param parent_item_id: Parent item UUID
        :param attributes:     attributes of the test case
        :param ts:             Start time
        """
        # Item type should be sent as "STEP" until we upgrade to RPv6.
        # Details at:
        # https://github.com/reportportal/agent-Python-RobotFramework/issues/56
        start_rq = {
            "name": test.name,
            "attributes": attributes,
            "description": test.doc,
            "start_time": ts or timestamp(),
            "item_type": "STEP",
            "parent_item_id": parent_item_id
        }
        logging.debug(
            "ReportPortal - Start test: "
            "request_body={0}".format(start_rq))
        return RobotService.rp.start_test_item(**start_rq)

    @staticmethod
    def finish_test(item_id, issue=None, test=None, ts=None):
        """Finish started test case.

        :param item_id: UUID of the started test item
        :param issue:   Corresponding issue if it exists
        :param test:    model.Test object
        :param ts:      End time
        """
        fta_rq = {
            "end_time": ts or timestamp(),
            "status": RobotService.status_mapping[test.status],
            "issue": issue,
            "item_id": item_id
        }
        logging.debug(
            "ReportPortal - Finish test:"
            " request_body={0}".format(fta_rq))
        RobotService.rp.finish_test_item(**fta_rq)

    @staticmethod
    def start_keyword(keyword=None, parent_item_id=None, has_stats=True,
                      ts=None):
        """Call start_test method of the common client.

        :param keyword:        model.Keyword object
        :param parent_item_id: Parent item UUID
        :param has_stats:      Flag that indicated whether keyword needs to
                               be nested step or not. (False - nested)
        :param ts:             Start time
        """
        start_rq = {
            "name": keyword.get_name(),
            "description": keyword.doc,
            "start_time": ts or timestamp(),
            "item_type": keyword.get_type(),
            "parent_item_id": parent_item_id,
            "has_stats": has_stats
        }
        logging.debug(
            "ReportPortal - Start keyword: "
            "request_body={0}".format(start_rq))
        return RobotService.rp.start_test_item(**start_rq)

    @staticmethod
    def finish_keyword(item_id, issue=None, keyword=None, ts=None):
        """Finish started test case.

        :param item_id: UUID of the started test item
        :param issue:   Corresponding issue if it exists
        :param keyword: model.Keyword object
        :param ts:      End time
        """
        fta_rq = {
            "end_time": ts or timestamp(),
            "status": RobotService.status_mapping[keyword.status],
            "issue": issue,
            "item_id": item_id
        }
        logging.debug(
            "ReportPortal - Finish keyword:"
            " request_body={0}".format(fta_rq))
        RobotService.rp.finish_test_item(**fta_rq)

    @staticmethod
    def log(message, ts=None):
        """Send log message to Report Portal.

        :param message: model.LogMessage object
        :param ts:      Timestamp
        """
        sl_rq = {
            "time": ts or timestamp(),
            "message": message.message,
            "level": RobotService.log_level_mapping[message.level],
            "attachment": message.attachment,
            "item_id": message.item_id
        }
        RobotService.rp.log(**sl_rq)
