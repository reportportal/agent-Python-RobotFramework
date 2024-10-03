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

from tests import REPORT_PORTAL_SERVICE
from tests.helpers import utils

EXAMPLE_TEST = 'examples/dynamic_test_case_id.robot'


@mock.patch(REPORT_PORTAL_SERVICE)
def test_case_id_simple(mock_client_init):
    result = utils.run_robot_tests([EXAMPLE_TEST], arguments={'--metadata': 'Scope:Smoke'})
    assert result == 0  # the test successfully passed

    mock_client = mock_client_init.return_value
    launch_start = mock_client.start_launch.call_args_list
    launch_finish = mock_client.finish_launch.call_args_list
    assert len(launch_start) == len(launch_finish) == 1

    item_start_calls = mock_client.start_test_item.call_args_list
    item_finish_calls = mock_client.finish_test_item.call_args_list
    assert len(item_start_calls) == len(item_finish_calls) == 3

    test_item_start = item_start_calls[-2]
    assert test_item_start[1]['test_case_id'] == f'{EXAMPLE_TEST}:Test set dynamic Test Case ID'

    test_item_finish = item_finish_calls[-2]
    assert test_item_finish[1]['test_case_id'] == 'dynamic_tags.robot[Smoke]'
