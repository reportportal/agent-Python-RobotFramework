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
from six.moves import mock

from tests import REPORT_PORTAL_SERVICE


SIMPLE_TEST = 'examples/simple.robot'


@mock.patch(REPORT_PORTAL_SERVICE)
def test_code_reference_simple(mock_client_init):
    result = utils.run_robot_tests([SIMPLE_TEST])
    assert result == 0  # the test successfully passed

    mock_client = mock_client_init.return_value
    launch_start = mock_client.start_launch.call_args_list
    launch_finish = mock_client.finish_launch.call_args_list
    assert len(launch_start) == len(launch_finish) == 1

    item_start_calls = mock_client.start_test_item.call_args_list
    item_finish_calls = mock_client.finish_test_item.call_args_list
    assert len(item_start_calls) == len(item_finish_calls) == 3

    test_item = item_start_calls[-2]
    assert test_item[1]['code_ref'] == SIMPLE_TEST + ':3'
