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
import warnings
from io import StringIO
from unittest import mock

import pytest

from reportportal_client import OutputType
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
@pytest.mark.parametrize('variable, warn_num',
                         [('RP_PROJECT', 1), ('RP_API_KEY', 2),
                          ('RP_ENDPOINT', 1), ('RP_LAUNCH', 1)])
@mock.patch(REPORT_PORTAL_SERVICE)
def test_no_required_variable_warning(mock_client_init, variable, warn_num):
    variables = utils.DEFAULT_VARIABLES.copy()
    del variables[variable]

    with warnings.catch_warnings(record=True) as w:
        result = utils.run_robot_tests(['examples/simple.robot'],
                                       variables=variables)
        assert result == 0  # the test successfully passed

        assert len(w) == warn_num
        assert w[0].category == RuntimeWarning

    mock_client = mock_client_init.return_value
    assert mock_client.start_launch.call_count == 0
    assert mock_client.start_test_item.call_count == 0
    assert mock_client.finish_test_item.call_count == 0
    assert mock_client.finish_launch.call_count == 0


def filter_agent_call(warn):
    category = getattr(warn, 'category', None)
    if category:
        return category.__name__ == 'DeprecationWarning' \
            or category.__name__ == 'RuntimeWarning'
    return False


def filter_agent_calls(warning_list):
    return list(
        filter(
            lambda call: filter_agent_call(call),
            warning_list
        )
    )


@mock.patch(REPORT_PORTAL_SERVICE)
def test_rp_api_key(mock_client_init):
    api_key = 'rp_api_key'
    variables = dict(utils.DEFAULT_VARIABLES)
    variables.update({'RP_API_KEY': api_key}.items())

    with warnings.catch_warnings(record=True) as w:
        result = utils.run_robot_tests(['examples/simple.robot'],
                                       variables=variables)
        assert int(result) == 0, 'Exit code should be 0 (no errors)'

        assert mock_client_init.call_count == 1

        constructor_args = mock_client_init.call_args_list[0][1]
        assert constructor_args['api_key'] == api_key
        assert len(filter_agent_calls(w)) == 0


@mock.patch(REPORT_PORTAL_SERVICE)
def test_rp_uuid(mock_client_init):
    api_key = 'rp_api_key'
    variables = dict(utils.DEFAULT_VARIABLES)
    del variables['RP_API_KEY']
    variables.update({'RP_UUID': api_key}.items())

    with warnings.catch_warnings(record=True) as w:
        result = utils.run_robot_tests(['examples/simple.robot'],
                                       variables=variables)
        assert int(result) == 0, 'Exit code should be 0 (no errors)'

        assert mock_client_init.call_count == 1

        constructor_args = mock_client_init.call_args_list[0][1]
        assert constructor_args['api_key'] == api_key
        assert len(filter_agent_calls(w)) == 1


@mock.patch(REPORT_PORTAL_SERVICE)
def test_rp_api_key_priority(mock_client_init):
    api_key = 'rp_api_key'
    variables = dict(utils.DEFAULT_VARIABLES)
    variables.update({'RP_API_KEY': api_key, 'RP_UUID': 'rp_uuid'}.items())

    with warnings.catch_warnings(record=True) as w:
        result = utils.run_robot_tests(['examples/simple.robot'],
                                       variables=variables)
        assert int(result) == 0, 'Exit code should be 0 (no errors)'

        assert mock_client_init.call_count == 1

        constructor_args = mock_client_init.call_args_list[0][1]
        assert constructor_args['api_key'] == api_key
        assert len(filter_agent_calls(w)) == 0


@mock.patch(REPORT_PORTAL_SERVICE)
def test_rp_api_key_empty(mock_client_init):
    api_key = ''
    variables = dict(utils.DEFAULT_VARIABLES)
    variables.update({'RP_API_KEY': api_key}.items())

    with warnings.catch_warnings(record=True) as w:
        result = utils.run_robot_tests(['examples/simple.robot'],
                                       variables=variables)
        assert int(result) == 0, 'Exit code should be 0 (no errors)'

        assert mock_client_init.call_count == 0
        assert len(filter_agent_calls(w)) == 2


@mock.patch(REPORT_PORTAL_SERVICE)
def test_launch_uuid_print(mock_client_init):
    print_uuid = True
    variables = utils.DEFAULT_VARIABLES.copy()
    variables.update({'RP_LAUNCH_UUID_PRINT': str(print_uuid)}.items())

    result = utils.run_robot_tests(['examples/simple.robot'],
                                   variables=variables)

    assert int(result) == 0, 'Exit code should be 0 (no errors)'
    assert mock_client_init.call_count == 1
    assert mock_client_init.call_args_list[0][1]['launch_uuid_print'] == print_uuid
    assert mock_client_init.call_args_list[0][1]['print_output'] is None


@mock.patch(REPORT_PORTAL_SERVICE)
def test_launch_uuid_print_stderr(mock_client_init):
    print_uuid = True
    variables = utils.DEFAULT_VARIABLES.copy()
    variables.update({'RP_LAUNCH_UUID_PRINT': str(print_uuid), 'RP_LAUNCH_UUID_PRINT_OUTPUT': 'stderr'}.items())

    result = utils.run_robot_tests(['examples/simple.robot'], variables=variables)

    assert int(result) == 0, 'Exit code should be 0 (no errors)'
    assert mock_client_init.call_count == 1
    assert mock_client_init.call_args_list[0][1]['launch_uuid_print'] == print_uuid
    assert mock_client_init.call_args_list[0][1]['print_output'] is OutputType.STDERR


@mock.patch(REPORT_PORTAL_SERVICE)
def test_launch_uuid_print_invalid_output(mock_client_init):
    print_uuid = True
    variables = utils.DEFAULT_VARIABLES.copy()
    variables.update({'RP_LAUNCH_UUID_PRINT': str(print_uuid), 'RP_LAUNCH_UUID_PRINT_OUTPUT': 'something'}.items())

    str_io = StringIO()
    result = utils.run_robot_tests(['examples/simple.robot'],
                                   variables=variables)

    assert int(result) == 0, 'Exit code should be 0 (no errors)'
    assert mock_client_init.call_count == 1
    assert mock_client_init.call_args_list[0][1]['launch_uuid_print'] == print_uuid
    assert mock_client_init.call_args_list[0][1]['print_output'] is None


@mock.patch(REPORT_PORTAL_SERVICE)
def test_no_launch_uuid_print(mock_client_init):
    variables = utils.DEFAULT_VARIABLES.copy()

    str_io = StringIO()
    result = utils.run_robot_tests(['examples/simple.robot'],
                                   variables=variables)

    assert int(result) == 0, 'Exit code should be 0 (no errors)'
    assert mock_client_init.call_count == 1
    assert mock_client_init.call_args_list[0][1]['launch_uuid_print'] is False
    assert mock_client_init.call_args_list[0][1]['print_output'] is None
