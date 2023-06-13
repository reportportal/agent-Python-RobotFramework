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
import sys

import pytest
import warnings

from six.moves import mock

from tests import REPORT_PORTAL_SERVICE
from tests.helpers import utils


@mock.patch(REPORT_PORTAL_SERVICE)
def test_agent_pass_batch_payload_size_variable(mock_client_init):
    variables = utils.DEFAULT_VARIABLES.copy()
    payload_size = 100
    variables['RP_LOG_BATCH_PAYLOAD_SIZE'] = payload_size
    result = utils.run_robot_tests(['examples/simple.robot'],
                                   variables=variables)
    assert result == 0  # the test successfully passed

    payload_variable = 'log_batch_payload_size'
    assert payload_variable in mock_client_init.call_args_list[0][1]
    assert mock_client_init.call_args_list[0][1][
               payload_variable] == payload_size


@mock.patch(REPORT_PORTAL_SERVICE)
def test_agent_pass_launch_uuid_variable(mock_client_init):
    variables = utils.DEFAULT_VARIABLES.copy()
    test_launch_id = 'my_test_launch'
    variables['RP_LAUNCH_UUID'] = test_launch_id
    result = utils.run_robot_tests(['examples/simple.robot'],
                                   variables=variables)
    assert result == 0  # the test successfully passed

    launch_id_variable = 'launch_id'
    assert launch_id_variable in mock_client_init.call_args_list[0][1]
    assert mock_client_init.call_args_list[0][1][
               launch_id_variable] == test_launch_id

    mock_client = mock_client_init.return_value
    assert mock_client.start_launch.call_count == 0


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason='For some reasons the test passes only for the '
                           'first variable for Python 2.7')
@pytest.mark.parametrize('variable', ['RP_PROJECT', 'RP_UUID', 'RP_ENDPOINT', 'RP_LAUNCH'])
@mock.patch(REPORT_PORTAL_SERVICE)
def test_no_required_variable_warning(mock_client_init, variable):
    variables = utils.DEFAULT_VARIABLES.copy()
    del variables[variable]

    with warnings.catch_warnings(record=True) as w:
        result = utils.run_robot_tests(['examples/simple.robot'],
                                       variables=variables)
        assert result == 0  # the test successfully passed

        assert len(w) == 1
        assert w[0].category == RuntimeWarning

    mock_client = mock_client_init.return_value
    assert mock_client.start_launch.call_count == 0
    assert mock_client.start_test_item.call_count == 0
    assert mock_client.finish_test_item.call_count == 0
    assert mock_client.finish_launch.call_count == 0
