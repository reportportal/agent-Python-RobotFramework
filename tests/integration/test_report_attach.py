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
from delayed_assert import assert_expectations, expect
from six.moves import mock

from tests import REPORT_PORTAL_SERVICE
from tests.helpers import utils


@mock.patch(REPORT_PORTAL_SERVICE)
def test_agent_attaches_report(mock_client_init):
    variables = utils.DEFAULT_VARIABLES.copy()
    variables['RP_ATTACH_REPORT'] = True
    result = utils.run_robot_tests(['examples/templates/settings.robot'],
                                   variables=variables)
    assert result == 0  # the test successfully passed

    mock_client = mock_client_init.return_value
    calls = utils.get_launch_log_calls(mock_client)
    assert len(calls) == 1

    call_params = calls[0][1]

    expect('attachment' in call_params.keys(),
           'log entry does not contain attachment')
    expect('level' in call_params.keys(),
           'log entry does not contain level')
    expect('message' in call_params.keys(),
           'log entry does not contain message')
    assert_expectations()

    expect(call_params['level'] == 'INFO')
    expect(call_params['message'] == 'Execution report')
    expect(call_params['attachment']['name'] == 'report.html')
    expect(call_params['attachment']['mime'] == 'text/html')
    expect(len(call_params['attachment']['data']) > 0)
    assert_expectations()
