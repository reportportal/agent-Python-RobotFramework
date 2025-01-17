#  Copyright 2025 EPAM Systems
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
from tests.helpers.utils import DEFAULT_VARIABLES


@pytest.mark.parametrize(
    "file, keyword_to_flatten, exit_code, expected_statuses, log_number, skip_idx, skip_message",
    [
        (
            "examples/rkie_keyword_error.robot",
            "name: BuiltIn.Run Keyword And Ignore Error",
            0,
            ["PASSED"] * 3 + ["SKIPPED"] * 3 + ["PASSED"] * 3,
            7,
            0,
            "Content flattened.",
        ),
        (
            "examples/for_keyword.robot",
            "FOR",
            0,
            ["PASSED"] * 3,
            4,
            0,
            "Content flattened.",
        ),
        (
            "examples/while_keyword.robot",
            "WHILE",
            0,
            ["PASSED"] * 4,
            9,
            2,
            "Content flattened.",
        ),
        (
            "examples/for_keyword_failed.robot",
            "FOR",
            1,
            ["FAILED"] * 3,
            4,
            0,
            "Content flattened.",
        ),
        (
            "examples/while_keyword_failed.robot",
            "WHILE",
            1,
            ["PASSED"] * 1 + ["FAILED"] * 3,
            8,
            2,
            "Content flattened.",
        ),
        (
            "examples/for_keyword.robot",
            "ITERATION",
            0,
            ["PASSED"] * 3,
            4,
            0,
            "Content flattened.",
        ),
        (
            "examples/while_keyword.robot",
            "ITERATION",
            0,
            ["PASSED"] * 4,
            9,
            2,
            "Content flattened.",
        ),
    ],
)
@mock.patch(REPORT_PORTAL_SERVICE)
def test_keyword_flatten(
    mock_client_init, file, keyword_to_flatten, exit_code, expected_statuses, log_number, skip_idx, skip_message
):
    mock_client = mock_client_init.return_value
    mock_client.start_test_item.side_effect = utils.item_id_gen

    variables = DEFAULT_VARIABLES.copy()
    variables["RP_FLATTEN_KEYWORDS"] = True
    result = utils.run_robot_tests([file], variables=variables, arguments={"--flatten-keywords": keyword_to_flatten})
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
