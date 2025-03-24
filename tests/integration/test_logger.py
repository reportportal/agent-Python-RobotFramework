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

import platform
from unittest import mock

from tests import REPORT_PORTAL_SERVICE
from tests.helpers import utils


@mock.patch(REPORT_PORTAL_SERVICE)
def test_launch_log(mock_client_init):
    result = utils.run_robot_tests(["examples/launch_log.robot"])
    assert result == 0  # the test successfully passed

    mock_client = mock_client_init.return_value
    calls = utils.get_launch_log_calls(mock_client)
    assert len(calls) == 3

    messages = set(map(lambda x: x[1]["message"], calls))
    assert messages == {"Hello, world!", "Goodbye, world!", "Enjoy my pug!"}


@mock.patch(REPORT_PORTAL_SERVICE)
def test_binary_file_log(mock_client_init):
    if platform.system() == "Linux" and platform.release().endswith("-azure"):
        # GitHub Actions Linux runner has an issue with binary data reading
        data_type = "application/octet-stream"
    else:
        data_type = "image/jpeg"
    result = utils.run_robot_tests(["examples/binary_file_log_as_text.robot"])
    assert result == 0  # the test successfully passed

    mock_client = mock_client_init.return_value
    calls = utils.get_log_calls(mock_client)
    assert len(calls) == 3

    messages = set(map(lambda x: x[1]["message"], calls))
    error_msg = f'Binary data of type "{data_type}" logging skipped, as it was processed as text and hence corrupted.'
    assert error_msg in messages
