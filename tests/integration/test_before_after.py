"""
Copyright (c) 2022 https://reportportal.io .
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

import pytest
from six.moves import mock

from tests import REPORT_PORTAL_SERVICE
from tests.helpers import utils


@pytest.mark.parametrize(
    'test, idx_to_check, step_name, suite_name', [
        ('examples/before_after/before_suite_with_steps.robot', 1,
         'Log suite setup', 'Before Suite With Steps'),
        ('examples/before_after/after_suite_with_steps.robot', 3,
         'Log suite tear down', 'After Suite With Steps')
    ])
@mock.patch(REPORT_PORTAL_SERVICE)
def test_before_after_suite_with_steps(mock_client_init, test, idx_to_check,
                                       step_name, suite_name):
    mock_client = mock_client_init.return_value
    mock_client.start_test_item.side_effect = utils.item_id_gen

    result = utils.run_robot_tests([test])
    assert result == 0

    launch_start = mock_client.start_launch.call_args_list
    launch_finish = mock_client.finish_launch.call_args_list
    assert len(launch_start) == len(launch_finish) == 1

    item_start_calls = mock_client.start_test_item.call_args_list
    item_finish_calls = mock_client.finish_test_item.call_args_list
    assert len(item_start_calls) == len(item_finish_calls) == 5

    statuses = [finish[1]['status'] for finish in item_finish_calls]
    assert statuses == ['PASSED'] * 5

    before_suite_start = item_start_calls[idx_to_check][1]
    assert before_suite_start['name'].startswith(step_name)
    assert before_suite_start['has_stats']
    assert before_suite_start['parent_item_id'].startswith(suite_name)
