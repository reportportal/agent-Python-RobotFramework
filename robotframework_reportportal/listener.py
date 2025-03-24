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

import logging
import os
import re
import uuid
from functools import wraps
from mimetypes import guess_type
from typing import Any, Dict, List, Optional, Union
from warnings import warn

from reportportal_client.helpers import LifoQueue, guess_content_type_from_bytes, is_binary

from robotframework_reportportal.helpers import _unescape
from robotframework_reportportal.model import (
    Entity,
    Keyword,
    KeywordMatch,
    KeywordNameMatch,
    KeywordTagMatch,
    KeywordTypeEqual,
    Launch,
    LogMessage,
    Suite,
    Test,
)
from robotframework_reportportal.service import RobotService
from robotframework_reportportal.static import MAIN_SUITE_ID, PABOT_WITHOUT_LAUNCH_ID_MSG
from robotframework_reportportal.variables import Variables


class __DummyContext:
    current = None


try:
    from robot.running.context import EXECUTION_CONTEXTS
except ImportError:
    warn(
        'Unable to locate Robot Framework context. "--remove-keywords" and "--flatten-keywords" feature'
        " will not work.",
        stacklevel=2,
    )
    EXECUTION_CONTEXTS = __DummyContext()

logger = logging.getLogger(__name__)
VARIABLE_PATTERN = re.compile(r"^\s*\${[^}]*}\s*=\s*")
IMAGE_PATTERN = re.compile(
    r'</td></tr><tr><td colspan="\d+"><a href="[^"]+"(?: target="_blank")?>'
    r'<img src="([^"]+)" width="\d+(?:px|pt)?"/?></a>'
)

DEFAULT_BINARY_FILE_TYPE = "application/octet-stream"
TRUNCATION_SIGN = "...'"
REMOVED_KEYWORD_CONTENT_LOG = "Content removed using the --remove-keywords option."
FLATTENED_KEYWORD_CONTENT_LOG = "Content flattened."
REMOVED_WUKS_KEYWORD_LOG = "{number} failing items removed using the --remove-keywords option."
REMOVED_FOR_WHILE_KEYWORD_LOG = "{number} passing items removed using the --remove-keywords option."
WUKS_KEYWORD_NAME = "BuiltIn.Wait Until Keyword Succeeds"
RKIE_KEYWORD_NAME = "BuiltIn.Run Keyword And Ignore Error"
FOR_KEYWORD_TYPE = "FOR"
WHILE_KEYWORD_TYPE = "WHILE"

WUKS_KEYWORD_MATCH = KeywordNameMatch(WUKS_KEYWORD_NAME)
FOR_KEYWORD_MATCH = KeywordTypeEqual(FOR_KEYWORD_TYPE)
WHILE_KEYWORD_MATCH = KeywordTypeEqual(WHILE_KEYWORD_TYPE)


def check_rp_enabled(func):
    """Verify is RP is enabled in config."""

    @wraps(func)
    def wrap(*args, **kwargs):
        if args and isinstance(args[0], listener):
            if not args[0].service:
                return
        func(*args, **kwargs)

    return wrap


def process_keyword_names_and_tags(matcher_list: List[KeywordMatch], pattern_str: str) -> None:
    """Pick name or pattern string, parse it and add to the matcher list.

    :param matcher_list: List of keyword matchers to add to
    :param pattern_str:  Pattern string passed to `--remove-keywords` or `--flatten-keywords` argument
    """
    if ":" in pattern_str:
        pattern_type, pattern = pattern_str.split(":", 1)
        pattern_type = pattern_type.strip().upper()
        if "NAME" == pattern_type.upper():
            matcher_list.append(KeywordNameMatch(pattern.strip()))
        elif "TAG" == pattern_type.upper():
            matcher_list.append(KeywordTagMatch(pattern.strip()))


class listener:
    """Robot Framework listener interface for reporting to ReportPortal."""

    _items: LifoQueue[Union[Keyword, Launch, Suite, Test]]
    _service: Optional[RobotService]
    _variables: Optional[Variables]
    _remove_keyword_filters: List[KeywordMatch] = []
    _flatten_keyword_filters: List[KeywordMatch] = []
    _remove_all_keyword_content: bool = False
    _remove_data_passed_tests: bool = False
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
        if isinstance(message["message"], LogMessage):
            msg = message["message"]
        else:
            msg = LogMessage(message["message"])
            msg.level = message["level"]
        current_item = self.current_item
        if current_item:
            msg.item_id = current_item.rp_item_id

        message_str = msg.message
        if is_binary(message_str):
            variable_match = VARIABLE_PATTERN.search(message_str)
            if variable_match:
                # Treat as partial binary data
                msg_content = message_str[variable_match.end() :]
                # remove trailing `'"...`, add `...'`
                msg.message = (
                    message_str[variable_match.start() : variable_match.end()]
                    + str(msg_content.encode("utf-8"))[:-5]
                    + TRUNCATION_SIGN
                )
            else:
                # Do not log full binary data, since it's usually corrupted
                content_type = guess_content_type_from_bytes(_unescape(message_str, 128))
                msg.message = (
                    f'Binary data of type "{content_type}" logging skipped, as it was processed as text and'
                    " hence corrupted."
                )
                msg.level = "WARN"
        elif message.get("html", "no") == "yes":
            image_match = IMAGE_PATTERN.match(message_str)
            if image_match:
                image_path = image_match.group(1)
                msg.message = f"Image attached: {image_path}"
                if os.path.exists(image_path):
                    image_type_by_name = guess_type(image_path)[0]
                    with open(image_path, "rb") as fh:
                        image_data = fh.read()
                        image_type_by_data = guess_content_type_from_bytes(image_data)
                        if image_type_by_name and image_type_by_data and image_type_by_name != image_type_by_data:
                            logger.warning(
                                f'Image type mismatch: type by file name "{image_type_by_name}" '
                                f'!= type by file content "{image_type_by_data}"'
                            )
                            mime_type = DEFAULT_BINARY_FILE_TYPE
                        else:
                            mime_type = image_type_by_name or image_type_by_data or DEFAULT_BINARY_FILE_TYPE
                        msg.attachment = {"name": os.path.basename(image_path), "data": image_data, "mime": mime_type}
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

    def __post_log_message(self, message: LogMessage) -> None:
        """Send log message to the Report Portal at skipped Keyword reporting.

        :param message: Internal message object to send
        """
        self.service.log(message=message)

    def __post_skipped_keyword(self, kwd: Keyword, clean_data_remove: bool) -> None:
        self._do_start_keyword(kwd)
        if clean_data_remove:
            kwd.remove_data = False
        for log_message in kwd.skipped_logs:
            self.__post_log_message(log_message)
        skipped_keywords = kwd.skipped_keywords
        kwd.skipped_keywords = []
        for skipped_kwd in skipped_keywords:
            self.__post_skipped_keyword(skipped_kwd, clean_data_remove)
        if kwd.status != "NOT SET":
            self._do_end_keyword(kwd)

    def _post_skipped_keywords(self, to_post: Optional[Any], clean_data_remove: bool = False) -> None:
        if not to_post:
            return
        if isinstance(to_post, Keyword) and not to_post.posted:
            self._do_start_keyword(to_post)
            if clean_data_remove:
                to_post.remove_data = False
            log_messages = to_post.skipped_logs
            to_post.skipped_logs = []
            for log_message in log_messages:
                self.__post_log_message(log_message)
        skipped_keywords = to_post.skipped_keywords
        if skipped_keywords:
            to_post.skipped_keywords = []
            for skipped_kwd in skipped_keywords:
                if skipped_kwd.posted:
                    log_messages = skipped_kwd.skipped_logs
                    skipped_kwd.skipped_logs = []
                    for log_message in log_messages:
                        self.__post_log_message(log_message)
                    skipped_child_keywords = skipped_kwd.skipped_keywords
                    for skipped_child_kwd in skipped_child_keywords:
                        if skipped_child_kwd.posted:
                            continue
                        self.__post_skipped_keyword(skipped_child_kwd, clean_data_remove)
                    continue
                self.__post_skipped_keyword(skipped_kwd, clean_data_remove)

    def __find_root_keyword_with_removed_data(self, keyword: Entity) -> Entity:
        if keyword.parent.remove_data and keyword.parent.type == "KEYWORD":
            return self.__find_root_keyword_with_removed_data(keyword.parent)
        return keyword

    def _log_message(self, message: LogMessage) -> None:
        """Send log message to the Report Portal.

        :param message: Internal message object to send
        """
        current_item = self.current_item
        if not current_item:
            # top-level log message
            self.__post_log_message(message)
            return

        if not getattr(current_item, "remove_data", False) and getattr(current_item, "posted", True):
            self.__post_log_message(message)
        else:
            if message.level not in {"ERROR", "WARN"}:
                self.current_item.skipped_logs.append(message)
            else:
                if not self._remove_all_keyword_content:
                    # Post everything skipped by '--removekeywords' option
                    self._post_skipped_keywords(self.__find_root_keyword_with_removed_data(current_item), True)
                    self.__post_log_message(message)

    @check_rp_enabled
    def log_message(self, message: Dict) -> None:
        """Send log message to the Report Portal.

        :param message: Message passed by the Robot Framework
        """
        msg = self._build_msg_struct(message)
        self._log_message(msg)

    @check_rp_enabled
    def log_message_with_image(self, msg: Dict, image: str):
        """Send log message to the ReportPortal.

        :param msg:   Message passed by the Robot Framework
        :param image: Path to image
        """
        mes = self._build_msg_struct(msg)
        with open(image, "rb") as fh:
            mes.attachment = {
                "name": os.path.basename(image),
                "data": fh.read(),
                "mime": guess_type(image)[0] or DEFAULT_BINARY_FILE_TYPE,
            }
        self._log_message(mes)

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

    def _process_keyword_remove(self):
        if not self.variables.remove_keywords:
            return

        self._remove_keyword_filters = []
        current_context = EXECUTION_CONTEXTS.current
        if current_context:
            # noinspection PyProtectedMember
            for pattern_str in set(current_context.output._settings.remove_keywords):
                pattern_str_upper = pattern_str.upper()
                if "ALL" == pattern_str_upper:
                    self._remove_all_keyword_content = True
                    break
                if "PASSED" == pattern_str_upper:
                    self._remove_data_passed_tests = True
                    break
                if pattern_str_upper in {"FOR", "WHILE", "WUKS"}:
                    if pattern_str_upper == "WUKS":
                        self._remove_keyword_filters.append(WUKS_KEYWORD_MATCH)
                    elif pattern_str_upper == "FOR":
                        self._remove_keyword_filters.append(FOR_KEYWORD_MATCH)
                    else:
                        self._remove_keyword_filters.append(WHILE_KEYWORD_MATCH)
                    continue
                process_keyword_names_and_tags(self._remove_keyword_filters, pattern_str)

    def _process_keyword_flatten(self):
        if not self.variables.flatten_keywords:
            return

        self._flatten_keyword_filters = []
        current_context = EXECUTION_CONTEXTS.current
        if current_context:
            # noinspection PyProtectedMember
            for pattern_str in set(current_context.output._settings.flatten_keywords):
                pattern_str_upper = pattern_str.upper()
                if pattern_str_upper in {"FOR", "WHILE", "ITERATION", "FORITEM"}:
                    if pattern_str_upper == "FOR":
                        self._flatten_keyword_filters.append(FOR_KEYWORD_MATCH)
                    elif pattern_str_upper == "WHILE":
                        self._flatten_keyword_filters.append(WHILE_KEYWORD_MATCH)
                    else:
                        self._flatten_keyword_filters.extend([FOR_KEYWORD_MATCH, WHILE_KEYWORD_MATCH])
                    continue
                process_keyword_names_and_tags(self._flatten_keyword_filters, pattern_str)

    def start_launch(self, attributes: Dict[str, Any], ts: Optional[Any] = None) -> None:
        """Start a new launch at the ReportPortal.

        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        self._process_keyword_remove()
        self._process_keyword_flatten()

        launch = Launch(self.variables.launch_name, attributes, self.variables.launch_attributes)
        launch.doc = self.variables.launch_doc or launch.doc
        if self.variables.pabot_used and not self._variables.launch_id:
            warn(PABOT_WITHOUT_LAUNCH_ID_MSG, stacklevel=2)
        logger.debug(f"ReportPortal - Start Launch: {launch.robot_attributes}")
        self.service.start_launch(
            launch=launch,
            mode=self.variables.mode,
            ts=ts,
            rerun=self.variables.rerun,
            rerun_of=self.variables.rerun_of,
        )

    def finish_launch(self, attributes: Dict[str, Any], ts: Optional[Any] = None) -> None:
        """Finish started launch at the ReportPortal.

        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        launch = Launch(self.variables.launch_name, attributes, None)
        logger.debug(f"ReportPortal - End Launch: {launch.robot_attributes}")
        self.service.finish_launch(launch=launch, ts=ts)

    @check_rp_enabled
    def start_suite(self, name: str, attributes: Dict, ts: Optional[Any] = None) -> None:
        """Start a new test suite at the ReportPortal.

        :param name:       Test suite name
        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        if attributes["id"] == MAIN_SUITE_ID:
            self.start_launch(attributes, ts)
            if self.variables.pabot_used:
                name = f"{name}.{self.variables.pabot_pool_id}"
            logger.debug(f"ReportPortal - Create global Suite: {attributes}")
        else:
            logger.debug(f"ReportPortal - Start Suite: {attributes}")
        suite = Suite(name, attributes, self.current_item)
        suite.rp_item_id = self.service.start_suite(suite=suite, ts=ts)
        self._add_current_item(suite)

    def _log_data_removed(self, item_id: str, timestamp: str, message: str) -> None:
        msg = LogMessage(message)
        msg.level = "DEBUG"
        msg.item_id = item_id
        msg.timestamp = timestamp
        self.__post_log_message(msg)

    def _log_keyword_content_removed(self, item_id: str, timestamp: str) -> None:
        self._log_data_removed(item_id, timestamp, REMOVED_KEYWORD_CONTENT_LOG)

    @check_rp_enabled
    def end_suite(self, _: Optional[str], attributes: Dict, ts: Optional[Any] = None) -> None:
        """Finish started test suite at the ReportPortal.

        :param _:          Test suite name
        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        suite = self._remove_current_item().update(attributes)
        logger.debug(f"ReportPortal - End Suite: {suite.robot_attributes}")
        if attributes["status"] == "FAIL" and self._remove_data_passed_tests:
            self._post_skipped_keywords(suite)
        elif self._remove_data_passed_tests:
            for kwd in suite.skipped_keywords:
                self._log_keyword_content_removed(kwd.rp_item_id, kwd.start_time)
        self.service.finish_suite(suite=suite, ts=ts)
        if attributes["id"] == MAIN_SUITE_ID:
            self.finish_launch(attributes, ts)

    @check_rp_enabled
    def start_test(self, name: str, attributes: Dict, ts: Optional[Any] = None) -> None:
        """Start a new test case at the ReportPortal.

        :param name:       Test case name
        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        if "source" not in attributes:
            # no 'source' parameter at this level for Robot versions < 4
            attributes = attributes.copy()
            attributes["source"] = getattr(self.current_item, "source", None)
        test = Test(name, attributes, self.variables.test_attributes, self.current_item)
        logger.debug(f"ReportPortal - Start Test: {attributes}")
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
        if not test.critical and test.status == "FAIL":
            test.status = "SKIP"
        if attributes["status"] == "FAIL" and self._remove_data_passed_tests:
            self._post_skipped_keywords(test)
        elif self._remove_data_passed_tests:
            for kwd in test.skipped_keywords:
                self._log_keyword_content_removed(kwd.rp_item_id, kwd.start_time)
        logger.debug(f"ReportPortal - End Test: {test.robot_attributes}")
        self._remove_current_item()
        self.service.finish_test(test=test, ts=ts)

    def _do_start_keyword(self, keyword: Keyword, ts: Optional[str] = None) -> None:
        logger.debug(f"ReportPortal - Start Keyword: {keyword.robot_attributes}")
        keyword.rp_item_id = self.service.start_keyword(keyword=keyword, ts=ts)
        keyword.posted = True

    def _should_remove(self, keyword: Keyword) -> Optional[KeywordMatch]:
        for matcher in self._remove_keyword_filters:
            if matcher.match(keyword):
                return matcher
        return None

    def _should_flatten(self, keyword: Keyword) -> bool:
        if not isinstance(keyword, Keyword):
            return False
        return any(matcher.match(keyword) for matcher in self._flatten_keyword_filters)

    def _log_keyword_content_flattened(self, item_id: str, timestamp: str) -> None:
        self._log_data_removed(item_id, timestamp, FLATTENED_KEYWORD_CONTENT_LOG)

    @check_rp_enabled
    def start_keyword(self, name: str, attributes: Dict, ts: Optional[Any] = None) -> None:
        """Start a new keyword(test step) at the ReportPortal.

        :param name:       Keyword name
        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        parent = self.current_item
        kwd = Keyword(name, attributes, parent)
        remove_kwd = parent.remove_data
        skip_data = self._remove_all_keyword_content or self._remove_data_passed_tests
        kwd.remove_data = remove_kwd or skip_data

        if kwd.remove_data:
            kwd.remove_filter = parent.remove_filter
            kwd.remove_origin = parent.remove_origin
        else:
            m = self._should_remove(kwd)
            if m:
                kwd.remove_data = True
                kwd.remove_filter = m
                kwd.remove_origin = kwd

        if remove_kwd:
            kwd.rp_item_id = str(uuid.uuid4())
            parent.skipped_keywords.append(kwd)
            kwd.posted = False
        else:
            if parent.flattened or self._should_flatten(parent):
                kwd.rp_item_id = parent.rp_item_id
                kwd.flattened = True
            else:
                self._do_start_keyword(kwd, ts)
                if not kwd.flattened and self._should_flatten(kwd):
                    self._log_keyword_content_flattened(kwd.rp_item_id, kwd.start_time)
            if skip_data:
                kwd.remove_origin = kwd
            if self._remove_data_passed_tests:
                parent.skipped_keywords.append(kwd)

        self._add_current_item(kwd)

    def _do_end_keyword(self, keyword: Keyword, ts: Optional[str] = None) -> None:
        logger.debug(f"ReportPortal - End Keyword: {keyword.robot_attributes}")
        self.service.finish_keyword(keyword=keyword, ts=ts)

    @check_rp_enabled
    def end_keyword(self, _: Optional[str], attributes: Dict, ts: Optional[Any] = None) -> None:
        """Finish started keyword at the ReportPortal.

        :param _:          Keyword name
        :param attributes: Dictionary passed by the Robot Framework
        :param ts:         Timestamp(used by the ResultVisitor)
        """
        kwd = self.current_item.update(attributes)

        if kwd.remove_filter is WUKS_KEYWORD_MATCH and kwd.remove_origin is kwd:
            skipped_keywords = kwd.skipped_keywords
            skipped_keywords_num = len(skipped_keywords)
            if skipped_keywords_num > 2:
                if kwd.status == "FAIL":
                    message = REMOVED_WUKS_KEYWORD_LOG.format(number=len(kwd.skipped_keywords) - 1)
                else:
                    message = REMOVED_WUKS_KEYWORD_LOG.format(number=len(kwd.skipped_keywords) - 2)
                self._log_data_removed(kwd.rp_item_id, kwd.start_time, message)
            if skipped_keywords_num > 1 and kwd.status != "FAIL":
                first_iteration = kwd.skipped_keywords[0]
                self._post_skipped_keywords(first_iteration)
                self._do_end_keyword(first_iteration)
            if skipped_keywords_num > 0:
                last_iteration = kwd.skipped_keywords[-1]
                self._post_skipped_keywords(last_iteration)
                self._do_end_keyword(last_iteration, ts)

        elif (
            (kwd.remove_filter is FOR_KEYWORD_MATCH) or (kwd.remove_filter is WHILE_KEYWORD_MATCH)
        ) and kwd.remove_origin is kwd:
            skipped_keywords = kwd.skipped_keywords
            skipped_keywords_num = len(skipped_keywords)
            if skipped_keywords_num > 1:
                self._log_data_removed(
                    kwd.rp_item_id,
                    kwd.start_time,
                    REMOVED_FOR_WHILE_KEYWORD_LOG.format(number=skipped_keywords_num - 1),
                )
            last_iteration = kwd.skipped_keywords[-1]
            self._post_skipped_keywords(last_iteration)
            self._do_end_keyword(last_iteration, ts)
        elif kwd.posted and kwd.remove_data and kwd.remove_origin is kwd:
            if (self._remove_all_keyword_content or not self._remove_data_passed_tests) and (
                kwd.skipped_keywords or kwd.skipped_logs
            ):
                self._log_keyword_content_removed(kwd.rp_item_id, kwd.start_time)

        self._remove_current_item()
        if not kwd.posted or kwd.flattened:
            return
        self._do_end_keyword(kwd, ts)

    def log_file(self, log_path: str) -> None:
        """Attach HTML log file created by Robot Framework to RP launch.

        :param log_path: Path to the log file
        """
        if self.variables.attach_log:
            message = {"message": "Execution log", "level": "INFO"}
            self.log_message_with_image(message, log_path)

    def report_file(self, report_path: str) -> None:
        """Attach HTML report created by Robot Framework to RP launch.

        :param report_path: Path to the report file
        """
        if self.variables.attach_report:
            message = {"message": "Execution report", "level": "INFO"}
            self.log_message_with_image(message, report_path)

    def xunit_file(self, xunit_path: str) -> None:
        """Attach XUnit file created by Robot Framework to RP launch.

        :param xunit_path: Path to the XUnit file
        """
        if self.variables.attach_xunit:
            message = {"message": "XUnit result file", "level": "INFO"}
            self.log_message_with_image(message, xunit_path)

    @check_rp_enabled
    def close(self) -> None:
        """Call service terminate when the whole test execution is done."""
        self.service.terminate_service()
