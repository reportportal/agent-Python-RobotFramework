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


def verify_attachment(mock_client_init, result, message, name, content_type):
    assert result == 0  # the test successfully passed

    mock_client = mock_client_init.return_value
    calls = utils.get_launch_log_calls(mock_client)
    assert len(calls) == 1

    call_params = calls[0][1]
    assert "attachment" in call_params.keys(), "log entry does not contain attachment"
    assert "level" in call_params.keys(), "log entry does not contain level"
    assert "message" in call_params.keys(), "log entry does not contain message"

    assert call_params["level"] == "INFO"
    assert call_params["message"] == message
    assert call_params["attachment"]["name"] == name
    assert call_params["attachment"]["mime"] == content_type
    assert len(call_params["attachment"]["data"]) > 0


@mock.patch(REPORT_PORTAL_SERVICE)
def test_agent_attaches_report(mock_client_init):
    variables = utils.DEFAULT_VARIABLES.copy()
    variables["RP_ATTACH_REPORT"] = True
    result = utils.run_robot_tests(["examples/templates/settings.robot"], variables=variables)
    verify_attachment(mock_client_init, result, "Execution report", "report.html", "text/html")


@mock.patch(REPORT_PORTAL_SERVICE)
def test_agent_attaches_log(mock_client_init):
    variables = utils.DEFAULT_VARIABLES.copy()
    variables["RP_ATTACH_LOG"] = True
    result = utils.run_robot_tests(["examples/templates/settings.robot"], variables=variables)
    verify_attachment(mock_client_init, result, "Execution log", "log.html", "text/html")
    assert result == 0  # the test successfully passed


XUNIT_FILE_NAME = "xunit.xml"


@mock.patch(REPORT_PORTAL_SERVICE)
def test_agent_attaches_xunit(mock_client_init):
    variables = utils.DEFAULT_VARIABLES.copy()
    variables["RP_ATTACH_XUNIT"] = True
    result = utils.run_robot_tests(
        ["examples/templates/settings.robot"], variables=variables, arguments={"-x": XUNIT_FILE_NAME}
    )
    verify_attachment(mock_client_init, result, "XUnit result file", XUNIT_FILE_NAME, "application/xml")
