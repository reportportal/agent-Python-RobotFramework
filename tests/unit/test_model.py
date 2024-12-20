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

import pytest

from robotframework_reportportal.model import Keyword


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
    kwd = Keyword(name="Test keyword", robot_attributes=kwd_attributes, parent_type=parent_type)
    kwd.keyword_type = self_type
    assert kwd.get_type() == expected
