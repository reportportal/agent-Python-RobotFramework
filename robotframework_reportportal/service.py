#  Copyright 2023 EPAM Systems
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""This module is a Robot service for reporting results to ReportPortal."""

import logging
from typing import Optional

from dateutil.parser import parse
from reportportal_client import RP, create_client
from reportportal_client.helpers import (
    dict_to_payload,
    get_launch_sys_attrs,
    get_package_version,
    timestamp
)

from robotframework_reportportal.model import Launch, Suite, Test, Keyword, LogMessage
from robotframework_reportportal.static import LOG_LEVEL_MAPPING, STATUS_MAPPING
from robotframework_reportportal.variables import Variables

logger = logging.getLogger(__name__)

TOP_LEVEL_ITEMS = {'BEFORE_SUITE', 'AFTER_SUITE'}


def to_epoch(date: Optional[str]) -> Optional[str]:
    """Convert Robot Framework timestamp to UTC timestamp."""
    if not date:
        return None
    try:
        parsed_date = parse(date)
    except ValueError:
        return None
    if hasattr(parsed_date, 'timestamp'):
        epoch_time = parsed_date.timestamp()
    else:
        epoch_time = float(parsed_date.strftime('%s')) + parsed_date.microsecond / 1e6
    return str(int(epoch_time * 1000))


class RobotService(object):
    """Class represents service that sends Robot items to ReportPortal."""

    agent_name: str
    agent_version: str
    rp: Optional[RP]

    def __init__(self) -> None:
        """Initialize service attributes."""
        self.agent_name = 'robotframework-reportportal'
        self.agent_version = get_package_version(self.agent_name)
        self.rp = None

    def _get_launch_attributes(self, cmd_attrs: list) -> list:
        """Generate launch attributes including both system and user ones.

        :param list cmd_attrs: List for attributes from the command line
        """
        attributes = cmd_attrs or []
        system_attributes = get_launch_sys_attrs()
        system_attributes['agent'] = (
            '{}|{}'.format(self.agent_name, self.agent_version))
        return attributes + dict_to_payload(system_attributes)

    def init_service(self, variables: Variables) -> None:
        """Initialize common ReportPortal client.

        :param variables: ReportPortal variables
        """
        if self.rp is None:
            logger.debug(f'ReportPortal - Init service: endpoint={variables.endpoint}, '
                         f'project={variables.project}, api_key={variables.api_key}')

            self.rp = create_client(
                client_type=variables.client_type,
                endpoint=variables.endpoint,
                project=variables.project,
                api_key=variables.api_key,
                is_skipped_an_issue=variables.skipped_issue,
                log_batch_size=variables.log_batch_size,
                retries=5,
                verify_ssl=variables.verify_ssl,
                max_pool_size=variables.pool_size,
                log_batch_payload_size=variables.log_batch_payload_size,
                launch_uuid=variables.launch_id,
                launch_uuid_print=variables.launch_uuid_print,
                print_output=variables.launch_uuid_print_output,
                http_timeout=variables.http_timeout
            )

    def terminate_service(self) -> None:
        """Terminate common ReportPortal client."""
        if self.rp:
            self.rp.close()

    def start_launch(self, launch: Launch, mode: Optional[str] = None, rerun: bool = False,
                     rerun_of: Optional[str] = None,
                     ts: Optional[str] = None) -> Optional[str]:
        """Call start_launch method of the common client.

        :param launch:   Instance of the Launch class
        :param mode:     Launch mode
        :param rerun:    Rerun mode. Allowable values 'True' of 'False'
        :param rerun_of: Rerun mode. Specifies launch to be re-run.
                         Should be used with the 'rerun' option.
        :param ts:       Start time
        :return:         launch UUID
        """
        sl_pt = {
            'attributes': self._get_launch_attributes(launch.attributes),
            'description': launch.doc,
            'name': launch.name,
            'mode': mode,
            'rerun': rerun,
            'rerun_of': rerun_of,
            'start_time': ts or to_epoch(launch.start_time) or timestamp()
        }
        logger.debug('ReportPortal - Start launch: request_body={0}'.format(sl_pt))
        return self.rp.start_launch(**sl_pt)

    def finish_launch(self, launch: Launch, ts: Optional[str] = None) -> None:
        """Finish started launch.

        :param launch: Launch name
        :param ts:     End time
        """
        fl_rq = {
            'end_time': ts or to_epoch(launch.end_time) or timestamp(),
            'status': STATUS_MAPPING[launch.status]
        }
        logger.debug('ReportPortal - Finish launch: request_body={0}'.format(fl_rq))
        self.rp.finish_launch(**fl_rq)

    def start_suite(self, suite: Suite, ts: Optional[str] = None) -> Optional[str]:
        """Call start_test method of the common client.

        :param suite: model.Suite object
        :param ts:    Start time
        :return:      Suite UUID
        """
        start_rq = {
            'attributes': suite.attributes,
            'description': suite.doc,
            'item_type': suite.type,
            'name': suite.name,
            'parent_item_id': suite.rp_parent_item_id,
            'start_time': ts or to_epoch(suite.start_time) or timestamp()
        }
        logger.debug('ReportPortal - Start suite: request_body={0}'.format(start_rq))
        return self.rp.start_test_item(**start_rq)

    def finish_suite(self, suite: Suite, issue: Optional[str] = None,
                     ts: Optional[str] = None) -> None:
        """Finish started suite.

        :param suite: Instance of the started suite item
        :param issue: Corresponding issue if it exists
        :param ts:    End time
        """
        fta_rq = {
            'end_time': ts or to_epoch(suite.end_time) or timestamp(),
            'issue': issue,
            'item_id': suite.rp_item_id,
            'status': STATUS_MAPPING[suite.status]
        }
        logger.debug('ReportPortal - Finish suite: request_body={0}'.format(fta_rq))
        self.rp.finish_test_item(**fta_rq)

    def start_test(self, test: Test, ts: Optional[str] = None):
        """Call start_test method of the common client.

        :param test: model.Test object
        :param ts:   Start time
        """
        # Item type should be sent as "STEP" until we upgrade to RPv6.
        # Details at:
        # https://github.com/reportportal/agent-Python-RobotFramework/issues/56
        start_rq = {
            'attributes': test.attributes,
            'code_ref': test.code_ref,
            'description': test.doc,
            'item_type': 'STEP',
            'name': test.name,
            'parent_item_id': test.rp_parent_item_id,
            'start_time': ts or to_epoch(test.start_time) or timestamp(),
            'test_case_id': test.test_case_id
        }
        logger.debug('ReportPortal - Start test: request_body={0}'.format(start_rq))
        return self.rp.start_test_item(**start_rq)

    def finish_test(self, test: Test, issue: Optional[str] = None, ts: Optional[str] = None):
        """Finish started test case.

        :param test:  Instance of started test item
        :param issue: Corresponding issue if it exists
        :param ts:    End time
        """
        fta_rq = {
            'attributes': test.attributes,
            'end_time': ts or to_epoch(test.end_time) or timestamp(),
            'issue': issue,
            'item_id': test.rp_item_id,
            'status': STATUS_MAPPING[test.status]
        }
        logger.debug('ReportPortal - Finish test: request_body={0}'.format(fta_rq))
        self.rp.finish_test_item(**fta_rq)

    def start_keyword(self, keyword: Keyword, ts: Optional[str] = None):
        """Call start_test method of the common client.

        :param keyword: model.Keyword object
        :param ts:      Start time
        """
        start_rq = {
            'description': keyword.doc,
            'has_stats': keyword.get_type() in TOP_LEVEL_ITEMS,
            'item_type': keyword.get_type(),
            'name': keyword.get_name(),
            'parent_item_id': keyword.rp_parent_item_id,
            'start_time': ts or to_epoch(keyword.start_time) or timestamp()
        }
        logger.debug('ReportPortal - Start keyword: request_body={0}'.format(start_rq))
        return self.rp.start_test_item(**start_rq)

    def finish_keyword(self, keyword: Keyword, issue: Optional[str] = None, ts: Optional[str] = None):
        """Finish started keyword item.

        :param keyword: Instance of started keyword item
        :param issue:   Corresponding issue if it exists
        :param ts:      End time
        """
        fta_rq = {
            'end_time': ts or to_epoch(keyword.end_time) or timestamp(),
            'issue': issue,
            'item_id': keyword.rp_item_id,
            'status': STATUS_MAPPING[keyword.status]
        }
        logger.debug('ReportPortal - Finish keyword: request_body={0}'.format(fta_rq))
        self.rp.finish_test_item(**fta_rq)

    def log(self, message: LogMessage, ts: Optional[str] = None):
        """Send log message to ReportPortal.

        :param message: model.LogMessage object
        :param ts:      Timestamp
        """
        sl_rq = {
            'attachment': message.attachment,
            'item_id': message.item_id,
            'level': LOG_LEVEL_MAPPING.get(message.level, 'INFO'),
            'message': message.message,
            'time': ts or timestamp()
        }
        self.rp.log(**sl_rq)
