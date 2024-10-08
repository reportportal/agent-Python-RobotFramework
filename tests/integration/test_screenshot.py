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

from tests.helpers import utils
from unittest import mock

from tests import REPORT_PORTAL_SERVICE

EXAMPLE_TEST = 'examples/screenshot.robot'
SELENIUM_SCREENSHOT = 'examples/res/selenium-screenshot-1.png'
PLAYWRIGHT_SCREENSHOT = 'examples/res/Screenshot_test_FAILURE_SCREENSHOT_1.png'
SCREENSHOTS = [SELENIUM_SCREENSHOT, PLAYWRIGHT_SCREENSHOT]


@mock.patch(REPORT_PORTAL_SERVICE)
def test_screenshot_log(mock_client_init):
    result = utils.run_robot_tests([EXAMPLE_TEST])
    assert result == 0  # the test successfully passed

    mock_client = mock_client_init.return_value
    calls = utils.get_log_calls(mock_client)
    assert len(calls) == 2

    for i, call in enumerate(calls):
        message = call[1]['message']
        assert message == f'Image attached: {SCREENSHOTS[i]}'

        attachment = call[1]['attachment']

        assert attachment['name'] == SCREENSHOTS[i].split('/')[-1]
        assert attachment['mime'] == 'image/png'
        with open(SCREENSHOTS[i], 'rb') as file:
            assert attachment['data'] == file.read()
