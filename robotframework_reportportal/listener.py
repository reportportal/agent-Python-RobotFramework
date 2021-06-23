"""This module includes Robot Framework listener interfaces..

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
import os
from mimetypes import guess_type

from reportportal_client.helpers import gen_attributes

from .exception import RobotServiceException
from .model import Keyword, Launch, Test, LogMessage, Suite
from .service import RobotService
from .static import MAIN_SUITE_ID, PABOT_WIHOUT_LAUNCH_ID_MSG
from .variables import Variables

logger = logging.getLogger(__name__)


class listener(object):
    """Robot Framework listener interface for reporting to Report Portal."""

    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self):
        """Initialize listener attributes."""
        self._items = []
        self._service = None
        self._variables = None

    def _build_msg_struct(self, message):
        """Check if the given message comes from our custom logger or not.

        :param message: Message passed by the Robot Framework
        """
        if isinstance(message['message'], LogMessage):
            msg = message['message']
        else:
            msg = LogMessage(message['message'])
            msg.level = message['level']
        if not getattr(msg, 'launch_log', False):
            msg.item_id = getattr(self.current_item, 'rp_item_id', None)
        return msg

    def _finish_current_item(self):
        """Remove the last item from the self._items list."""
        return self._items.pop()

    @property
    def current_item(self):
        """Get the last item from the self._items list."""
        if self._items:
            return self._items[-1]

    def log_message(self, message):
        """Send log message to the Report Portal.

        :param message: Message passed by the Robot Framework
        """
        msg = self._build_msg_struct(message)
        logger.debug('ReportPortal - Log Message: {0}'.format(message))
        self.service.log(message=msg)

    def log_message_with_image(self, msg, image):
        """Send log message to the Report Portal.

        :param msg:   Message passed by the Robot Framework
        :param image: Path to image
        """
        mes = self._build_msg_struct(msg)
        with open(image, 'rb') as fh:
            mes.attachment = {
                'name': os.path.basename(image),
                'data': fh.read(),
                'mime': guess_type(image)[0] or 'application/octet-stream'
            }
        logger.debug('ReportPortal - Log Message with Image: {0} {1}'
                     .format(mes, image))
        self.service.log(message=mes)

    @property
    def parent_id(self):
        """Get rp_item_id attribute of the current item."""
        return getattr(self.current_item, 'rp_item_id', None)

    @property
    def service(self):
        """Initialize instance of the RobotService."""
        if self._service is None:
            self._service = RobotService()
            self._service.init_service(
                endpoint=self.variables.endpoint,
                project=self.variables.project,
                uuid=self.variables.uuid,
                log_batch_size=self.variables.log_batch_size,
                pool_size=self.variables.pool_size,
                skipped_issue=self.variables.skipped_issue,
                verify_ssl=self.variables.verify_ssl
            )
        return self._service

    @property
    def variables(self):
        """Get instance of the variables.Variables class."""
        if not self._variables:
            self._variables = Variables()
        return self._variables

    def start_launch(self, attributes, ts=None):
        """Start a new launch at the Report Portal.

        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        launch = Launch(self.variables.launch_name, attributes)
        launch.attributes = gen_attributes(self.variables.launch_attributes)
        launch.doc = self.variables.launch_doc or launch.doc
        if not self.variables.launch_id:
            if self.variables.pabot_used:
                raise RobotServiceException(PABOT_WIHOUT_LAUNCH_ID_MSG)
            logger.debug('ReportPortal - Start Launch: {0}'.format(
                launch.attributes))
            self.service.start_launch(
                launch=launch,
                mode=self.variables.mode,
                ts=ts,
                skip_analytics=self.variables.skip_analytics)
        else:
            self.service.rp.launch_id = self.variables.launch_id

    def start_suite(self, name, attributes, ts=None):
        """Start a new test suite at the Report Portal.

        :param name:       Test suite name
        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        if attributes['id'] == MAIN_SUITE_ID:
            self.start_launch(attributes, ts)
            if self.variables.pabot_used:
                name += '.{0}'.format(self.variables.pabot_pool_id)
            logger.debug(
                'ReportPortal - Create global Suite: {0}'
                .format(attributes))
            suite = Suite(name, attributes)
            suite.rp_item_id = self.service.start_suite(suite=suite, ts=ts)
            self._items.append(suite)
        else:
            logger.debug('ReportPortal - Start Suite: {0}'.format(attributes))
            suite = Suite(name, attributes)
            suite.rp_parent_item_id = self.parent_id
            suite.rp_item_id = self.service.start_suite(suite=suite, ts=ts)
            self._items.append(suite)

    def end_suite(self, _, attributes, ts=None):
        """Finish started test suite at the Report Portal.

        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        if attributes['id'] == MAIN_SUITE_ID:
            suite = self._finish_current_item().update(attributes)
            logger.debug('ReportPortal - End Suite: {0}'
                         .format(suite.attributes))
            self.service.finish_suite(suite=suite, ts=ts)
            launch = Launch(self.variables.launch_name, attributes)
            logger.debug(
                msg='ReportPortal - End Launch: {0}'.format(attributes))
            self.service.finish_launch(launch=launch, ts=ts)
        else:
            suite = self._finish_current_item().update(attributes)
            logger.debug(
                'ReportPortal - End Suite: {0}'.format(suite.attributes))
            self.service.finish_suite(suite=suite, ts=ts)

    def start_test(self, name, attributes, ts=None):
        """Start a new test case at the Report Portal.

        :param name:       Test case name
        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        if 'source' not in attributes:
            # no 'source' parameter at this level for Robot versions < 4
            attributes = attributes.copy()
            attributes['source'] = getattr(self.current_item, 'source', None)
        test = Test(name=name, attributes=attributes)
        logger.debug('ReportPortal - Start Test: {0}'.format(attributes))
        test.attributes = gen_attributes(
            self.variables.test_attributes + test.tags)
        test.rp_parent_item_id = self.parent_id
        test.rp_item_id = self.service.start_test(test=test, ts=ts)
        self._items.append(test)

    def end_test(self, _, attributes, ts=None):
        """Finish started test case at the Report Portal.

        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        test = self._finish_current_item().update(attributes)
        test.attributes = gen_attributes(
            self.variables.test_attributes + test.tags)
        if not test.critical and test.status == 'FAIL':
            test.status = 'SKIP'
        logger.debug('ReportPortal - End Test: {0}'.format(test.attributes))
        self.service.finish_test(test=test, ts=ts)

    def start_keyword(self, name, attributes, ts=None):
        """Start a new keyword(test step) at the Report Portal.

        :param name:       Keyword name
        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        kwd = Keyword(name=name, parent_type=self.current_item.type,
                      attributes=attributes)
        kwd.rp_parent_item_id = self.parent_id
        logger.debug('ReportPortal - Start Keyword: {0}'.format(attributes))
        kwd.rp_item_id = self.service.start_keyword(keyword=kwd, ts=ts)
        self._items.append(kwd)

    def end_keyword(self, _, attributes, ts=None):
        """Finish started keyword at the Report Portal.

        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        kwd = self._finish_current_item().update(attributes)
        logger.debug('ReportPortal - End Keyword: {0}'.format(kwd.attributes))
        self.service.finish_keyword(keyword=kwd, ts=ts)

    def report_file(self, report_path):
        """Attach HTML report created by Robot Framework to RP launch.

        :param report_path: Path to the report file
        """
        if self.variables.attach_report:
            message = {'message': 'Execution report', 'level': 'INFO'}
            self.log_message_with_image(message, report_path)

    def close(self):
        """Call service terminate when the whole test execution is done."""
        self.service.terminate_service()
