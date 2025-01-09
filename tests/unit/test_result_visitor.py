"""
Copyright (c) 2021 https://reportportal.io .
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License
"""

import sys

import pytest

from robotframework_reportportal.result_visitor import to_timestamp
from robotframework_reportportal.variables import _variables


def test_parse_message_no_img_tag(visitor):
    with pytest.raises(AttributeError):
        visitor.split_message_and_image("usual test comment without image")


def test_parse_message_bad_img_tag(visitor):
    with pytest.raises(AttributeError):
        visitor.split_message_and_image("<img src='bad.html.img>")


def test_parse_message_contains_image(visitor):
    assert ('src="any.png"', "any.png") == visitor.split_message_and_image('<img alt="" src="any.png" />')


def test_parse_message_contains_image_with_space(visitor):
    assert ('src="any%20image.png"', "any image.png") == visitor.split_message_and_image(
        '<img alt="" src="any%20image.png" />'
    )


TIMESTAMP_TEST_CASES = [
    ("20240920 00:00:00.000", "+3:00", "1726779600000"),
    ("20240919 18:00:00.000", "-3:00", "1726779600000"),
]

if sys.version_info >= (3, 9):
    TIMESTAMP_TEST_CASES += [
        ("20240919 23:00:00.000", "Europe/Warsaw", "1726779600000"),
        ("20240920 00:00:00.000", "UTC", "1726790400000"),
        ("20240919 19:00:00.000", "EST", "1726790400000"),
    ]


@pytest.mark.parametrize("time_str, time_shift, expected", TIMESTAMP_TEST_CASES)
def test_time_stamp_conversion(time_str, time_shift, expected):
    _variables["RP_TIME_ZONE_OFFSET"] = time_shift
    assert to_timestamp(time_str) == expected
