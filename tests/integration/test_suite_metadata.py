#  Copyright 2022 EPAM Systems
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

from tests.helpers import utils
from unittest import mock

from tests import REPORT_PORTAL_SERVICE


SIMPLE_TEST = 'examples/suite_metadata.robot'


@mock.patch(REPORT_PORTAL_SERVICE)
def test_suite_metadata_simple(mock_client_init):
    result = utils.run_robot_tests([SIMPLE_TEST])
    assert result == 0  # the test successfully passed

    mock_client = mock_client_init.return_value
    launch_start = mock_client.start_launch.call_args_list
    launch_finish = mock_client.finish_launch.call_args_list
    assert len(launch_start) == len(launch_finish) == 1

    item_start_calls = mock_client.start_test_item.call_args_list
    item_finish_calls = mock_client.finish_test_item.call_args_list
    assert len(item_start_calls) == len(item_finish_calls) == 3

    test_suite = item_start_calls[0]
    assert test_suite[1]['attributes'] == [{'key': 'Author', 'value': 'John Doe'}]


@mock.patch(REPORT_PORTAL_SERVICE)
def test_suite_metadata_command_line_simple(mock_client_init):
    result = utils.run_robot_tests([SIMPLE_TEST], arguments={'--metadata': 'Scope:Smoke'})
    assert result == 0  # the test successfully passed

    mock_client = mock_client_init.return_value
    launch_start = mock_client.start_launch.call_args_list
    launch_finish = mock_client.finish_launch.call_args_list
    assert len(launch_start) == len(launch_finish) == 1

    item_start_calls = mock_client.start_test_item.call_args_list
    item_finish_calls = mock_client.finish_test_item.call_args_list
    assert len(item_start_calls) == len(item_finish_calls) == 3

    test_suite = item_start_calls[0]
    attributes = test_suite[1]['attributes']
    assert len(attributes) == 2
    assert {'value': 'Smoke', 'key': 'Scope'} in attributes
    assert {'key': 'Author', 'value': 'John Doe'} in attributes
