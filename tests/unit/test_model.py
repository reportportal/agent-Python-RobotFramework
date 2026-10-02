"""This module includes unit tests for the model.py module.

Copyright (c) 2021 https://reportportal.io .
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
https://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from unittest import mock

import pytest

from robotframework_reportportal.model import Keyword, Suite
from robotframework_reportportal.model import Test as RobotTest


@pytest.mark.parametrize(
    "self_type, parent_type, expected",
    [
        ("SETUP", "KEYWORD", "STEP"),
        ("SETUP", "TEST", "BEFORE_TEST"),
        ("TEARDOWN", "SUITE", "AFTER_SUITE"),
        ("TEST", "SUITE", "STEP"),
    ],
)
def test_keyword_get_type(kwd_attributes, self_type, parent_type, expected):
    """Test for the get_type() method of the Keyword model."""
    parent = mock.Mock()
    parent.type = parent_type
    kwd = Keyword(name="Test keyword", robot_attributes=kwd_attributes, parent=parent)
    kwd.keyword_type = self_type
    assert kwd.get_type() == expected


@mock.patch("robotframework_reportportal.model.os.path.relpath", return_value="robot\\test.robot")
@mock.patch("robotframework_reportportal.model.os.sep", "\\")
def test_source_uses_forward_slashes_on_windows(_, suite_attributes, test_attributes):
    """Test that Windows source paths are normalized to forward slashes."""
    suite = Suite(name="Suite", robot_attributes=suite_attributes)
    test = RobotTest(name="Test", robot_attributes=test_attributes, test_attributes=[], parent=suite)
    assert suite.source == "robot/test.robot"
    assert test.source == "robot/test.robot"
    assert test.code_ref == "robot/test.robot:Test"
    assert test.test_case_id == "robot/test.robot:Test"
