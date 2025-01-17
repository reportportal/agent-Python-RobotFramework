#  Copyright 2024 EPAM Systems
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""This module contains models representing Robot Framework test items."""

import os
import re
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union

from reportportal_client.helpers import gen_attributes

from robotframework_reportportal.helpers import match_pattern, robot_markup_to_markdown, translate_glob_to_regex

TEST_CASE_ID_SIGN = "test_case_id:"


class Entity:
    """Base class for all test items."""

    type: str
    remove_data: bool
    flattened: bool
    remove_filter: Optional[Any]
    remove_origin: Optional[Any]
    rp_item_id: Optional[str]
    parent: Optional["Entity"]
    skipped_keywords: List["Keyword"]
    posted: bool

    def __init__(self, entity_type: str, parent: Optional["Entity"]):
        """Initialize required attributes.

        :param entity_type: Type of the entity
        :param parent:      Parent entity
        """
        self.type = entity_type
        self.parent = parent
        self.rp_item_id = None
        self.remove_data = False
        self.flattened = False
        self.remove_filter = None
        self.remove_origin = None
        self.skipped_keywords = []
        self.posted = True

    @property
    def rp_parent_item_id(self):
        """Get parent item ID."""
        return getattr(self.parent, "rp_item_id", None)


class LogMessage(str):
    """Class represents Robot Framework messages."""

    attachment: Optional[Dict[str, str]]
    launch_log: bool
    item_id: Optional[str]
    level: str
    message: str
    timestamp: Optional[str]

    def __init__(self, message: str):
        """Initialize required attributes."""
        self.attachment = None
        self.item_id = None
        self.level = "INFO"
        self.launch_log = False
        self.message = message
        self.timestamp = None


class Keyword(Entity):
    """Class represents Robot Framework keyword."""

    robot_attributes: Dict[str, Any]
    args: List[str]
    assign: List[str]
    doc: str
    end_time: str
    keyword_name: str
    keyword_type: str
    libname: str
    name: str
    start_time: str
    status: str
    tags: List[str]
    type: str = "KEYWORD"
    skipped_logs: List[LogMessage]

    def __init__(self, name: str, robot_attributes: Dict[str, Any], parent: Entity):
        """Initialize required attributes.

        :param name:              Name of the keyword
        :param robot_attributes:  Attributes passed through the listener
        :param parent:      Parent entity
        """
        super().__init__("KEYWORD", parent)
        self.robot_attributes = robot_attributes
        self.args = robot_attributes["args"]
        self.assign = robot_attributes["assign"]
        self.doc = robot_markup_to_markdown(robot_attributes["doc"])
        self.end_time = robot_attributes.get("endtime")
        self.keyword_name = robot_attributes["kwname"]
        self.keyword_type = robot_attributes["type"]
        self.libname = robot_attributes["libname"]
        self.name = name
        self.start_time = robot_attributes["starttime"]
        self.status = robot_attributes.get("status")
        self.tags = robot_attributes["tags"]
        self.type = "KEYWORD"
        self.skipped_logs = []

    def get_name(self) -> str:
        """Get name of the keyword suitable for ReportPortal."""
        assign = ", ".join(self.assign)
        assignment = "{0} = ".format(assign) if self.assign else ""
        arguments = ", ".join(self.args)
        full_name = f"{self.keyword_type} {assignment}{self.name} ({arguments})"
        return full_name[:256]

    def get_type(self) -> str:
        """Get keyword type."""
        if self.keyword_type.lower() in ("setup", "teardown"):
            if self.parent.type.lower() == "keyword":
                return "STEP"
            if self.keyword_type.lower() == "setup":
                return "BEFORE_{0}".format(self.parent.type.upper())
            if self.keyword_type.lower() == "teardown":
                return "AFTER_{0}".format(self.parent.type.upper())
        else:
            return "STEP"

    def update(self, attributes: Dict[str, Any]) -> "Keyword":
        """Update keyword attributes on keyword finish.

        :param attributes: Suite attributes passed through the listener
        """
        self.end_time = attributes.get("endtime", "")
        self.status = attributes.get("status")
        return self


class Suite(Entity):
    """Class represents Robot Framework test suite."""

    robot_attributes: Union[List[str], Dict[str, Any]]
    doc: str
    end_time: str
    longname: str
    message: str
    metadata: Dict[str, str]
    name: str
    robot_id: str
    start_time: Optional[str]
    statistics: str
    status: str
    suites: List[str]
    tests: List[str]
    total_tests: int

    def __init__(self, name: str, robot_attributes: Dict[str, Any], parent: Optional[Entity] = None):
        """Initialize required attributes.

        :param name:       Suite name
        :param robot_attributes: Suite attributes passed through the listener
        :param parent:     Parent entity
        """
        super().__init__("SUITE", parent)
        self.robot_attributes = robot_attributes
        self.doc = robot_markup_to_markdown(robot_attributes["doc"])
        self.end_time = robot_attributes.get("endtime", "")
        self.longname = robot_attributes["longname"]
        self.message = robot_attributes.get("message")
        self.metadata = robot_attributes["metadata"]
        self.name = name
        self.robot_id = robot_attributes["id"]
        self.start_time = robot_attributes.get("starttime")
        self.statistics = robot_attributes.get("statistics")
        self.status = robot_attributes.get("status")
        self.suites = robot_attributes["suites"]
        self.tests = robot_attributes["tests"]
        self.total_tests = robot_attributes["totaltests"]

    @property
    def attributes(self) -> Optional[List[Dict[str, str]]]:
        """Get Suite attributes."""
        if self.metadata is None or not self.metadata:
            return None
        return [{"key": key, "value": value} for key, value in self.metadata.items()]

    @property
    def source(self) -> str:
        """Return the test case source file path."""
        if self.robot_attributes.get("source") is not None:
            return os.path.relpath(self.robot_attributes["source"], os.getcwd())

    def update(self, attributes: Dict[str, Any]) -> "Suite":
        """Update suite attributes on suite finish.

        :param attributes: Suite attributes passed through the listener
        """
        self.end_time = attributes.get("endtime", "")
        self.message = attributes.get("message")
        self.status = attributes.get("status")
        self.statistics = attributes.get("statistics")
        return self


class Launch(Suite):
    """Class represents Robot Framework test suite."""

    launch_attributes: Optional[List[Dict[str, str]]]
    type: str = "LAUNCH"

    def __init__(self, name: str, robot_attributes: Dict[str, Any], launch_attributes: Optional[List[str]]):
        """Initialize required attributes.

        :param name:       Launch name
        :param robot_attributes: Suite attributes passed through the listener
        :param launch_attributes: Launch attributes from variables
        """
        super().__init__(name, robot_attributes)
        self.launch_attributes = gen_attributes(launch_attributes or [])
        self.type = "LAUNCH"

    @property
    def attributes(self) -> Optional[List[Dict[str, str]]]:
        """Get Launch attributes."""
        return self.launch_attributes


class Test(Entity):
    """Class represents Robot Framework test case."""

    _critical: str
    _tags: List[str]
    robot_attributes: Dict[str, Any]
    test_attributes: Optional[List[Dict[str, str]]]
    doc: str
    end_time: str
    longname: str
    message: str
    name: str
    robot_id: str
    start_time: str
    status: str
    template: str

    def __init__(self, name: str, robot_attributes: Dict[str, Any], test_attributes: List[str], parent: Entity):
        """Initialize required attributes.

        :param name:             Name of the test
        :param robot_attributes: Attributes passed through the listener
        """
        super().__init__("TEST", parent)
        # for backward compatibility with Robot < 4.0 mark every test case
        # as critical if not set
        self._critical = robot_attributes.get("critical", "yes")
        self._tags = robot_attributes["tags"]
        self.test_attributes = gen_attributes(test_attributes)
        self.robot_attributes = robot_attributes
        self.doc = robot_markup_to_markdown(robot_attributes["doc"])
        self.end_time = robot_attributes.get("endtime", "")
        self.longname = robot_attributes["longname"]
        self.message = robot_attributes.get("message")
        self.name = name
        self.robot_id = robot_attributes["id"]
        self.start_time = robot_attributes["starttime"]
        self.status = robot_attributes.get("status")
        self.template = robot_attributes["template"]

    @property
    def critical(self) -> bool:
        """Form unique value for RF 4.0+ and older versions."""
        return self._critical in ("yes", True)

    @property
    def tags(self) -> List[str]:
        """Get list of test tags excluding test_case_id."""
        return [tag for tag in self._tags if not tag.startswith(TEST_CASE_ID_SIGN)]

    @property
    def attributes(self) -> Optional[List[Dict[str, str]]]:
        """Get Test attributes."""
        return self.test_attributes + gen_attributes(self.tags)

    @property
    def source(self) -> str:
        """Return the test case source file path."""
        if self.robot_attributes["source"] is not None:
            return os.path.relpath(self.robot_attributes["source"], os.getcwd())

    @property
    def code_ref(self) -> str:
        """Return the test case code reference.

        The result line should be exactly how it appears in '.robot' file.
        """
        line_number = self.robot_attributes.get("lineno")
        if line_number is not None:
            return "{0}:{1}".format(self.source, line_number)
        return "{0}:{1}".format(self.source, self.name)

    @property
    def test_case_id(self) -> Optional[str]:
        """Get test case ID through the tags."""
        # use test case id from tags if specified
        for tag in self._tags:
            if tag.startswith(TEST_CASE_ID_SIGN):
                return tag.split(":")[1]
        # generate it if not
        return "{0}:{1}".format(self.source, self.name)

    def update(self, attributes: Dict[str, Any]) -> "Test":
        """Update test attributes on test finish.

        :param attributes: Suite attributes passed through the listener
        """
        self._tags = attributes.get("tags", self._tags)
        self.end_time = attributes.get("endtime", "")
        self.message = attributes.get("message")
        self.status = attributes.get("status")
        return self


class KeywordMatch(ABC):
    """Base class for keyword matchers."""

    @abstractmethod
    def match(self, kw: Keyword) -> bool:
        """Check if the keyword matches the criteria."""


class KeywordEqual(KeywordMatch):
    """Match keyword based on a predicate."""

    predicate: Callable[[Keyword], bool]

    def __init__(self, predicate: Callable[[Keyword], bool] = None) -> None:
        """Initialize the matcher with the predicate."""
        self.predicate = predicate

    def match(self, kw: Keyword) -> bool:
        """Check if the keyword matches the criteria."""
        return self.predicate(kw)


class KeywordNameMatch(KeywordEqual):
    """Match keyword based on the name pattern."""

    def __init__(self, pattern: Optional[str]) -> None:
        """Initialize the matcher with the pattern."""
        re_pattern = translate_glob_to_regex(pattern)
        super().__init__(lambda kw: match_pattern(re_pattern, kw.name))


class KeywordTypeEqual(KeywordEqual):
    """Match keyword based on the type."""

    def __init__(self, expected_value: Optional[str]) -> None:
        """Initialize the matcher with the expected value."""
        super().__init__(lambda kw: kw.keyword_type == expected_value)


class KeywordTagMatch(KeywordMatch):
    """Match keyword based on the tag pattern."""

    pattern: Optional[re.Pattern]

    def __init__(self, pattern: Optional[str]) -> None:
        """Initialize the matcher with the pattern."""
        self.pattern = translate_glob_to_regex(pattern)

    def match(self, kw: Keyword) -> bool:
        """Check if the keyword matches the criteria."""
        return next((True for t in kw.tags if match_pattern(self.pattern, t)), False)


class KeywordStatusEqual(KeywordEqual):
    """Match keyword based on the status."""

    def __init__(self, status: str) -> None:
        """Initialize the matcher with the status."""
        super().__init__(lambda kw: kw.status == status)
