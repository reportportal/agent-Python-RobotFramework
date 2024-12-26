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

from unittest import mock

import pytest

from tests import REPORT_PORTAL_SERVICE
from tests.helpers import utils


@pytest.mark.parametrize(
    "file, exit_code, expected_statuses, log_number",
    [
        (
            "examples/wuks_keyword.robot",
            0,
            ["PASSED"] * 2 + ["FAILED"] * 3 + ["PASSED"] * 2 + ["SKIPPED"] * 2 + ["PASSED"] * 4,
            6,
        ),
        (
            "examples/wuks_keyword_failed.robot",
            1,
            ["PASSED"] * 2 + ["FAILED"] * 3 + ["PASSED"] * 2 + ["FAILED"] * 6,
            7,
        ),
    ],
)
@mock.patch(REPORT_PORTAL_SERVICE)
def test_wuks_keyword_remove(mock_client_init, file, exit_code, expected_statuses, log_number):
    mock_client = mock_client_init.return_value
    mock_client.start_test_item.side_effect = utils.item_id_gen

    result = utils.run_robot_tests([file], arguments={"--remove-keywords": "WUKS"})
    assert result == exit_code

    launch_start = mock_client.start_launch.call_args_list
    launch_finish = mock_client.finish_launch.call_args_list
    assert len(launch_start) == len(launch_finish) == 1

    item_start_calls = mock_client.start_test_item.call_args_list
    item_finish_calls = mock_client.finish_test_item.call_args_list
    assert len(item_start_calls) == len(item_finish_calls)
    assert len(item_finish_calls) == len(expected_statuses)

    statuses = [finish[1]["status"] for finish in item_finish_calls]
    assert statuses == expected_statuses

    calls = utils.get_log_calls(mock_client)
    assert len(calls) == log_number


@pytest.mark.parametrize(
    "file, keyword_to_remove, exit_code, expected_statuses, log_number, skip_idx, skip_message",
    [
        (
            "examples/for_keyword.robot",
            "FOR",
            0,
            ["PASSED"] * 5,
            2,
            0,
            "2 passing items removed using the --remove-keywords option.",
        ),
        (
            "examples/while_keyword.robot",
            "WHILE",
            0,
            ["PASSED"] * 7,
            5,
            2,
            "2 passing items removed using the --remove-keywords option.",
        ),
        (
            "examples/for_keyword_failed.robot",
            "FOR",
            1,
            ["FAILED"] * 2 + ["PASSED"] + ["FAILED"] * 4,
            3,
            0,
            "1 passing items removed using the --remove-keywords option.",
        ),
        (
            "examples/while_keyword_failed.robot",
            "WHILE",
            1,
            ["PASSED"] + ["FAILED"] * 2 + ["PASSED"] * 2 + ["FAILED"] * 4,
            6,
            2,
            "1 passing items removed using the --remove-keywords option.",
        ),
    ],
)
@mock.patch(REPORT_PORTAL_SERVICE)
def test_for_keyword_remove(
    mock_client_init, file, keyword_to_remove, exit_code, expected_statuses, log_number, skip_idx, skip_message
):
    mock_client = mock_client_init.return_value
    mock_client.start_test_item.side_effect = utils.item_id_gen

    result = utils.run_robot_tests([file], arguments={"--remove-keywords": keyword_to_remove})
    assert result == exit_code

    launch_start = mock_client.start_launch.call_args_list
    launch_finish = mock_client.finish_launch.call_args_list
    assert len(launch_start) == len(launch_finish) == 1

    item_start_calls = mock_client.start_test_item.call_args_list
    item_finish_calls = mock_client.finish_test_item.call_args_list
    assert len(item_start_calls) == len(item_finish_calls)
    assert len(item_finish_calls) == len(expected_statuses)

    statuses = [finish[1]["status"] for finish in item_finish_calls]
    assert statuses == expected_statuses

    log_calls = utils.get_log_calls(mock_client)
    assert len(log_calls) == log_number
    assert sorted(log_calls, key=lambda x: x[1]["time"])[skip_idx][1]["message"] == skip_message
