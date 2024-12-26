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
#  limitations under the License.s

import re
from unittest import mock

from docutils.nodes import description

from tests import REPORT_PORTAL_SERVICE
from tests.helpers import utils

NO_KEYWORDS_MESSAGE_PATTERN = re.compile(r"Message:\s+Test(?: case)? (?:contains no keywords|cannot be empty)\.")


@mock.patch(REPORT_PORTAL_SERVICE)
def test_no_keyword_message(mock_client_init):
    mock_client = mock_client_init.return_value
    mock_client.start_test_item.side_effect = utils.item_id_gen

    result = utils.run_robot_tests(["examples/no_keywords.robot"])
    assert result == 1

    launch_start = mock_client.start_launch.call_args_list
    launch_finish = mock_client.finish_launch.call_args_list
    assert len(launch_start) == len(launch_finish) == 1

    item_start_calls = mock_client.start_test_item.call_args_list
    item_finish_calls = mock_client.finish_test_item.call_args_list
    assert len(item_start_calls) == len(item_finish_calls)
    assert len(item_finish_calls) == 2

    statuses = [finish[1]["status"] for finish in item_finish_calls]
    assert statuses == ["FAILED", "FAILED"]

    test_finish_call = item_finish_calls[0][1]
    assert "description" in test_finish_call
    assert NO_KEYWORDS_MESSAGE_PATTERN.match(test_finish_call["description"])
