"""
Copyright (c) 2021 http://reportportal.io .
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License
"""

from itertools import product, chain

import pytest
from delayed_assert import assert_expectations, expect
from six.moves import mock

from robotframework_reportportal import logger

ATTACHMENT = {'name': 'test_screenshot.png', 'data': b'x0x0',
              'mime': 'image/png'}

BASIC_PARAMS = [
    {'msg': None, 'html': False, 'attachment': None, 'launch_log': False},
    {'msg': 'Test', 'html': False, 'attachment': None, 'launch_log': False},
    {'msg': None, 'html': True, 'attachment': None, 'launch_log': False},
    {'msg': None, 'html': False, 'attachment': ATTACHMENT,
     'launch_log': False},
    {'msg': None, 'html': False, 'attachment': None, 'launch_log': True}]

INFO_PARAMS = [{k: v for k, v in chain(e.items(), [('also_console', False)])}
               for e in BASIC_PARAMS + [BASIC_PARAMS[0]]]
INFO_PARAMS[-1]['also_console'] = True
INFO_PARAMS[-1]['msg'] = 'Test console message'

TEST_DATA_METHODS = chain(
    product(['trace', 'debug', 'warn', 'error'], BASIC_PARAMS),
    product(['info'], INFO_PARAMS))


@pytest.mark.parametrize('method, params', TEST_DATA_METHODS)
@mock.patch('robotframework_reportportal.logger.logger')
def test_logger_params_bypass(mock_logger, method, params):
    getattr(logger, method)(**params)
    assert mock_logger.write.call_count == 1

    message = mock_logger.write.call_args[0][0]
    expect(message.level == method.upper())
    expect(message.message == params['msg'])
    expect(message.attachment == params['attachment'])
    expect(message.launch_log == params['launch_log'])

    expect(mock_logger.write.call_args[0][1] == method.upper())
    expect(mock_logger.write.call_args[0][2] == params['html'])

    if 'also_console' in params and params['also_console']:
        expect(mock_logger.console.call_count == 1)
        expect(mock_logger.console.call_args[0][0] == params['msg'])
        expect(mock_logger.console.call_args[0][1] is True)
        expect(mock_logger.console.call_args[0][2] == 'stdout')

    assert_expectations()
