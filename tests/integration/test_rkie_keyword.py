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

from unittest import mock

from tests import REPORT_PORTAL_SERVICE
from tests.helpers import utils


@mock.patch(REPORT_PORTAL_SERVICE)
def test_before_after_suite_with_steps(mock_client_init):
    mock_client = mock_client_init.return_value
    mock_client.start_test_item.side_effect = utils.item_id_gen

    result = utils.run_robot_tests(["examples/rkie_keyword.robot"])
    assert result == 0

    launch_start = mock_client.start_launch.call_args_list
    launch_finish = mock_client.finish_launch.call_args_list
    assert len(launch_start) == len(launch_finish) == 1

    item_start_calls = mock_client.start_test_item.call_args_list
    item_finish_calls = mock_client.finish_test_item.call_args_list
    assert len(item_start_calls) == len(item_finish_calls) == 13

    statuses = [finish[1]["status"] for finish in item_finish_calls]
    assert statuses == ["PASSED"] * 2 + ["FAILED"] * 3 + ["PASSED"] * 3 + ["SKIPPED"] * 2 + ["PASSED"] * 3
