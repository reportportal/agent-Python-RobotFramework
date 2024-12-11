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

"""This module includes Robot Framework listener interfaces."""

import binascii
import logging
import os
import re
from abc import abstractmethod, ABC
from functools import wraps
from mimetypes import guess_type
from typing import Optional, Dict, Union, Any, List
from warnings import warn

from reportportal_client.helpers import LifoQueue, is_binary, guess_content_type_from_bytes

from robotframework_reportportal.helpers import translate_glob_to_regex, match_pattern
from robotframework_reportportal.model import Keyword, Launch, Test, LogMessage, Suite
from robotframework_reportportal.service import RobotService
from robotframework_reportportal.static import MAIN_SUITE_ID, PABOT_WITHOUT_LAUNCH_ID_MSG
from robotframework_reportportal.variables import Variables

logger = logging.getLogger(__name__)
VARIABLE_PATTERN = re.compile(r'^\s*\${[^}]*}\s*=\s*')
IMAGE_PATTERN = re.compile(
    r'</td></tr><tr><td colspan="\d+"><a href="[^"]+"(?: target="_blank")?>'
    r'<img src="([^"]+)" width="\d+(?:px|pt)?"/?></a>')

DEFAULT_BINARY_FILE_TYPE = 'application/octet-stream'
TRUNCATION_SIGN = "...'"


def _unescape(binary_string: str, stop_at: int = -1):
    result = bytearray()
    join_list = list()
    join_idx = -3
    skip_next = False
    for i, b in enumerate(binary_string):
        if skip_next:
            skip_next = False
            continue
        if i < join_idx + 2:
            join_list.append(b)
            continue
        else:
            if len(join_list) > 0:
                for bb in binascii.unhexlify(''.join(join_list)):
                    result.append(bb)
                    if stop_at > 0:
                        if len(result) >= stop_at:
                            break
                join_list = list()
        if b == '\\' and binary_string[i + 1] == 'x':
            skip_next = True
            join_idx = i + 2
            continue
        for bb in b.encode('utf-8'):
            result.append(bb)
            if stop_at > 0:
                if len(result) >= stop_at:
                    break
    if len(join_list) > 0:
        for bb in binascii.unhexlify(''.join(join_list)):
            result.append(bb)
    return result


def check_rp_enabled(func):
    """Verify is RP is enabled in config."""

    @wraps(func)
    def wrap(*args, **kwargs):
        if args and isinstance(args[0], listener):
            if not args[0].service:
                return
        func(*args, **kwargs)

    return wrap


class _KeywordMatch(ABC):
    @abstractmethod
    def match(self, line: Optional[str]) -> bool:
        ...


class _KeywordNameMatch(_KeywordMatch):
    pattern: Optional[re.Pattern]

    def __init__(self, pattern: Optional[str]):
        self.pattern = translate_glob_to_regex(pattern)

    def match(self, kw: Keyword) -> bool:
        return match_pattern(self.pattern, kw.name)


class _KeywordTagMatch(_KeywordMatch):
    pattern: Optional[re.Pattern]

    def __init__(self, pattern: Optional[str]):
        self.pattern = translate_glob_to_regex(pattern)

    def match(self, kw: Keyword) -> bool:
        return next((True for t in kw.tags if match_pattern(self.pattern, t)), False)


class _KeywordStatusMatch(_KeywordMatch):
    status: str

    def __init__(self, status: str):
        self.status = status.upper()

    def match(self, kw: Keyword) -> bool:
        return kw.status.upper() == self.status


# noinspection PyPep8Naming
class listener:
    """Robot Framework listener interface for reporting to ReportPortal."""

    _items: LifoQueue[Union[Keyword, Launch, Suite, Test]]
    _service: Optional[RobotService]
    _variables: Optional[Variables]
    _remove_keywords: List[_KeywordMatch] = []
    _realtime_keywords: bool = True
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self) -> None:
        """Initialize listener attributes."""
        self._items = LifoQueue()
        self._service = None
        self._variables = None

    def _build_msg_struct(self, message: Dict[str, Any]) -> LogMessage:
        """Check if the given message comes from our custom logger or not.

        :param message: Message passed by the Robot Framework
        """
        if isinstance(message['message'], LogMessage):
            msg = message['message']
        else:
            msg = LogMessage(message['message'])
            msg.level = message['level']
        if not msg.launch_log:
            msg.item_id = getattr(self.current_item, 'rp_item_id', None)

        message_str = msg.message
        if is_binary(message_str):
            variable_match = VARIABLE_PATTERN.search(message_str)
            if variable_match:
                # Treat as partial binary data
                msg_content = message_str[variable_match.end():]
                # remove trailing `'"...`, add `...'`
                msg.message = (message_str[variable_match.start():variable_match.end()]
                               + str(msg_content.encode('utf-8'))[:-5] + TRUNCATION_SIGN)
            else:
                # Do not log full binary data, since it's usually corrupted
                content_type = guess_content_type_from_bytes(_unescape(message_str, 128))
                msg.message = (f'Binary data of type "{content_type}" logging skipped, as it was processed as text and'
                               ' hence corrupted.')
                msg.level = 'WARN'
        elif message.get('html', 'no') == 'yes':
            image_match = IMAGE_PATTERN.match(message_str)
            if image_match:
                image_path = image_match.group(1)
                msg.message = f'Image attached: {image_path}'
                if os.path.exists(image_path):
                    image_type_by_name = guess_type(image_path)[0]
                    with open(image_path, 'rb') as fh:
                        image_data = fh.read()
                        image_type_by_data = guess_content_type_from_bytes(image_data)
                        if image_type_by_name and image_type_by_data and image_type_by_name != image_type_by_data:
                            logger.warning(
                                f'Image type mismatch: type by file name "{image_type_by_name}" '
                                f'!= type by file content "{image_type_by_data}"')
                            mime_type = DEFAULT_BINARY_FILE_TYPE
                        else:
                            mime_type = image_type_by_name or image_type_by_data or DEFAULT_BINARY_FILE_TYPE
                        msg.attachment = {
                            'name': os.path.basename(image_path),
                            'data': image_data,
                            'mime': mime_type
                        }
        return msg

    def _add_current_item(self, item: Union[Keyword, Launch, Suite, Test]) -> None:
        """Add the last item from the self._items queue."""
        self._items.put(item)

    def _remove_current_item(self) -> Union[Keyword, Launch, Suite, Test]:
        """Remove the last item from the self._items queue."""
        return self._items.get()

    @property
    def current_item(self) -> Optional[Union[Keyword, Launch, Suite, Test]]:
        """Get the last item from the self._items queue."""
        return self._items.last()

    @check_rp_enabled
    def log_message(self, message: Dict) -> None:
        """Send log message to the Report Portal.

        :param message: Message passed by the Robot Framework
        """
        msg = self._build_msg_struct(message)
        logger.debug(f'ReportPortal - Log Message: {message}')
        self.service.log(message=msg)

    @check_rp_enabled
    def log_message_with_image(self, msg: Dict, image: str):
        """Send log message to the ReportPortal.

        :param msg:   Message passed by the Robot Framework
        :param image: Path to image
        """
        mes = self._build_msg_struct(msg)
        with open(image, 'rb') as fh:
            mes.attachment = {
                'name': os.path.basename(image),
                'data': fh.read(),
                'mime': guess_type(image)[0] or DEFAULT_BINARY_FILE_TYPE
            }
        logger.debug(f'ReportPortal - Log Message with Image: {mes} {image}')
        self.service.log(message=mes)

    @property
    def parent_id(self) -> Optional[str]:
        """Get rp_item_id attribute of the current item."""
        return getattr(self.current_item, 'rp_item_id', None)

    @property
    def service(self) -> RobotService:
        """Initialize instance of the RobotService."""
        if self.variables.enabled and not self._service:
            self._service = RobotService()
            self._service.init_service(self.variables)
        return self._service

    @property
    def variables(self) -> Variables:
        """Get instance of the variables.Variables class."""
        if not self._variables:
            self._variables = Variables()
        return self._variables

    def _process_keyword_skip(self):
        try:
            # noinspection PyUnresolvedReferences
            from robot.running.context import EXECUTION_CONTEXTS
            current_context = EXECUTION_CONTEXTS.current
            if current_context:
                # noinspection PyProtectedMember
                for pattern_str in set(current_context.output._settings.remove_keywords):
                    if 'ALL' == pattern_str.upper():
                        self._remove_keywords = [_KeywordNameMatch(None)]
                        break
                    if 'PASSED' == pattern_str.upper():
                        self._remove_keywords = [_KeywordStatusMatch('PASS')]
                        self._realtime_keywords = False
                        continue
                    if pattern_str.upper() in {'NOT_RUN', 'NOTRUN', 'NOT RUN'}:
                        self._remove_keywords = [_KeywordStatusMatch('NOT RUN')]
                        self._realtime_keywords = False
                        continue
                    if pattern_str.upper() in {'FOR', 'WHILE', 'WUKS'}:
                        self._remove_keywords = [_KeywordNameMatch(pattern_str)]
                        continue
                    if ':' in pattern_str:
                        pattern_type, pattern = pattern_str.split(':', 1)
                        pattern_type = pattern_type.strip().upper()
                        if 'NAME' == pattern_type.upper():
                            self._remove_keywords.append(_KeywordNameMatch(pattern.strip()))
                        elif 'TAG' == pattern_type.upper():
                            self._remove_keywords.append(_KeywordTagMatch(pattern.strip()))
                            self._realtime_keywords = False
        except ImportError:
            warn('Unable to locate Robot Framework context. "removekeywords" feature will not work.', stacklevel=2)

    @check_rp_enabled
    def start_launch(self, attributes: Dict[str, Any], ts: Optional[Any] = None) -> None:
        """Start a new launch at the ReportPortal.

        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        self._process_keyword_skip()

        launch = Launch(self.variables.launch_name, attributes, self.variables.launch_attributes)
        launch.doc = self.variables.launch_doc or launch.doc
        if self.variables.pabot_used and not self._variables.launch_id:
            warn(PABOT_WITHOUT_LAUNCH_ID_MSG, stacklevel=2)
        logger.debug(f'ReportPortal - Start Launch: {launch.robot_attributes}')
        self.service.start_launch(
            launch=launch,
            mode=self.variables.mode,
            ts=ts,
            rerun=self.variables.rerun,
            rerun_of=self.variables.rerun_of)

    @check_rp_enabled
    def start_suite(self, name: str, attributes: Dict, ts: Optional[Any] = None) -> None:
        """Start a new test suite at the ReportPortal.

        :param name:       Test suite name
        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        if attributes['id'] == MAIN_SUITE_ID:
            self.start_launch(attributes, ts)
            if self.variables.pabot_used:
                name = f'{name}.{self.variables.pabot_pool_id}'
            logger.debug(f'ReportPortal - Create global Suite: {attributes}')
        else:
            logger.debug(f'ReportPortal - Start Suite: {attributes}')
        suite = Suite(name, attributes)
        suite.rp_parent_item_id = self.parent_id
        suite.rp_item_id = self.service.start_suite(suite=suite, ts=ts)
        self._add_current_item(suite)

    @check_rp_enabled
    def end_suite(self, _: Optional[str], attributes: Dict, ts: Optional[Any] = None) -> None:
        """Finish started test suite at the ReportPortal.

        :param _:          Test suite name
        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        suite = self._remove_current_item().update(attributes)
        logger.debug(f'ReportPortal - End Suite: {suite.robot_attributes}')
        self.service.finish_suite(suite=suite, ts=ts)
        if attributes['id'] == MAIN_SUITE_ID:
            launch = Launch(self.variables.launch_name, attributes, None)
            logger.debug(msg=f'ReportPortal - End Launch: {attributes}')
            self.service.finish_launch(launch=launch, ts=ts)

    @check_rp_enabled
    def start_test(self, name: str, attributes: Dict, ts: Optional[Any] = None) -> None:
        """Start a new test case at the ReportPortal.

        :param name:       Test case name
        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        if 'source' not in attributes:
            # no 'source' parameter at this level for Robot versions < 4
            attributes = attributes.copy()
            attributes['source'] = getattr(self.current_item, 'source', None)
        test = Test(name=name, robot_attributes=attributes, test_attributes=self.variables.test_attributes)
        logger.debug(f'ReportPortal - Start Test: {attributes}')
        test.rp_parent_item_id = self.parent_id
        test.rp_item_id = self.service.start_test(test=test, ts=ts)
        self._add_current_item(test)

    @check_rp_enabled
    def end_test(self, _: Optional[str], attributes: Dict, ts: Optional[Any] = None) -> None:
        """Finish started test case at the ReportPortal.

        :param _:          Test case name
        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        test = self.current_item.update(attributes)
        if not test.critical and test.status == 'FAIL':
            test.status = 'SKIP'
        if test.message:
            self.log_message({'message': test.message, 'level': 'DEBUG'})
        logger.debug(f'ReportPortal - End Test: {test.robot_attributes}')
        self._remove_current_item()
        self.service.finish_test(test=test, ts=ts)

    @check_rp_enabled
    def start_keyword(self, name: str, attributes: Dict, ts: Optional[Any] = None) -> None:
        """Start a new keyword(test step) at the ReportPortal.

        :param name:       Keyword name
        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        kwd = Keyword(name=name, parent_type=self.current_item.type, robot_attributes=attributes)
        kwd.rp_parent_item_id = self.parent_id
        logger.debug(f'ReportPortal - Start Keyword: {attributes}')
        kwd.rp_item_id = self.service.start_keyword(keyword=kwd, ts=ts)
        self._add_current_item(kwd)

    @check_rp_enabled
    def end_keyword(self, _: Optional[str], attributes: Dict, ts: Optional[Any] = None) -> None:
        """Finish started keyword at the ReportPortal.

        :param _:          Keyword name
        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        kwd = self._remove_current_item().update(attributes)
        logger.debug(f'ReportPortal - End Keyword: {kwd.robot_attributes}')
        self.service.finish_keyword(keyword=kwd, ts=ts)

    def log_file(self, log_path: str) -> None:
        """Attach HTML log file created by Robot Framework to RP launch.

        :param log_path: Path to the log file
        """
        if self.variables.attach_log:
            message = {'message': 'Execution log', 'level': 'INFO'}
            self.log_message_with_image(message, log_path)

    def report_file(self, report_path: str) -> None:
        """Attach HTML report created by Robot Framework to RP launch.

        :param report_path: Path to the report file
        """
        if self.variables.attach_report:
            message = {'message': 'Execution report', 'level': 'INFO'}
            self.log_message_with_image(message, report_path)

    def xunit_file(self, xunit_path: str) -> None:
        """Attach XUnit file created by Robot Framework to RP launch.

        :param xunit_path: Path to the XUnit file
        """
        if self.variables.attach_xunit:
            message = {'message': 'XUnit result file', 'level': 'INFO'}
            self.log_message_with_image(message, xunit_path)

    @check_rp_enabled
    def close(self) -> None:
        """Call service terminate when the whole test execution is done."""
        self.service.terminate_service()
