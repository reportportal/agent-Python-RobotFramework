"""
Copyright (c) 2022 https://reportportal.io .
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

import re
from tests.helpers import utils
from six.moves import mock

from tests import REPORT_PORTAL_SERVICE


NO_KEYWORDS_MESSAGE_PATTERN = \
    re.compile(r'Test(?: case)? (?:contains no keywords|cannot be empty)\.')


@mock.patch(REPORT_PORTAL_SERVICE)
def test_no_keyword_message(mock_client_init):
    mock_client = mock_client_init.return_value
    mock_client.start_test_item.side_effect = utils.item_id_gen

    result = utils.run_robot_tests(['examples/no_keywords.robot'])
    assert result == 1

    log_calls = mock_client.log.call_args_list
    assert len(log_calls) == 1

    log_call = log_calls[0][1]
    assert NO_KEYWORDS_MESSAGE_PATTERN.match(log_call['message'])
    assert log_call['item_id'].startswith('No keyword test case')

    item_start_calls = mock_client.start_test_item.call_args_list
    item_finish_calls = mock_client.finish_test_item.call_args_list
    assert len(item_start_calls) == len(item_finish_calls) == 2

    statuses = [finish[1]['status'] for finish in item_finish_calls]
    assert statuses == ['FAILED', 'FAILED']
