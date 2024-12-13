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

import pytest
from unittest import mock

from robotframework_reportportal import logger

ATTACHMENT = {'name': 'test_screenshot.png', 'data': b'x0x0',
              'mime': 'image/png'}

TEST_DATA_METHODS = [
    ('trace', ['Test', False, None, False]),
    ('trace', [None, True, None, False]),
    ('trace', [None, False, ATTACHMENT, False]),
    ('trace', [None, False, None, True]),
    ('debug', ['Test', False, None, False]),
    ('debug', [None, True, None, False]),
    ('debug', [None, False, ATTACHMENT, False]),
    ('debug', [None, False, None, True]),
    ('warn', ['Test', False, None, False]),
    ('warn', [None, True, None, False]),
    ('warn', [None, False, ATTACHMENT, False]),
    ('warn', [None, False, None, True]),
    ('error', ['Test', False, None, False]),
    ('error', [None, True, None, False]),
    ('error', [None, False, ATTACHMENT, False]),
    ('error', [None, False, None, True]),
    ('info', ['Test', False, False, None, False]),
    ('info', [None, True, False, None, False]),
    ('info', [None, False, True, None, False]),
    ('info', [None, False, False, ATTACHMENT, False]),
    ('info', [None, False, False, None, True]),
]


@pytest.mark.parametrize('method, params', TEST_DATA_METHODS)
@mock.patch('robotframework_reportportal.logger.logger')
def test_logger_params_bypass(mock_logger, method, params):
    getattr(logger, method)(*params)
    assert mock_logger.write.call_count == 1

    if method == 'info':
        attachment = params[3]
        launch_log = params[4]
    else:
        attachment = params[2]
        launch_log = params[3]

    if method == 'info' and params[2]:
        assert mock_logger.console.call_count == 1
        assert mock_logger.console.call_args[0][0] == params[0]
        assert mock_logger.console.call_args[0][1] is True
        assert mock_logger.console.call_args[0][2] == 'stdout'
    else:
        assert mock_logger.console.call_count == 0

    message = mock_logger.write.call_args[0][0]
    assert message.level == method.upper()
    assert message.message == params[0]
    assert message.attachment == attachment
    assert message.launch_log == launch_log
    assert mock_logger.write.call_args[0][1] == method.upper()
    assert mock_logger.write.call_args[0][2] == params[1]
