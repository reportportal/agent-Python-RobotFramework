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

import uuid

from delayed_assert import assert_expectations, expect
from six.moves import mock

from tests import REPORT_PORTAL_SERVICE
from tests.helpers import utils

TEST_CASES = ['Test tag set', 'Test no tag', 'Test set multiple tags']
TEST_CASE_UUIDS = [str(uuid.uuid5(uuid.NAMESPACE_OID, i)) for i in TEST_CASES]


def generate_id(*args, **kwargs):
    return str(uuid.uuid5(uuid.NAMESPACE_OID, str(kwargs['name'])))


@mock.patch(REPORT_PORTAL_SERVICE)
def test_launch_log(mock_client_init):
    mock_client = mock_client_init.return_value
    mock_client.start_test_item.side_effect = generate_id

    result = utils.run_robot_tests(['examples/dynamic_tags.robot'])
    assert result == 0  # the test successfully passed

    start_tests = [
        call for call in mock_client.start_test_item.call_args_list if
        call[1]['item_type'] == 'STEP' and call[1].get('has_stats', True)]
    finish_tests = [call for call in
                    mock_client.finish_test_item.call_args_list if
                    call[1]['item_id'] in TEST_CASE_UUIDS]

    for start in start_tests:
        expect(len(start[1]['attributes']) == 0)

    expect(finish_tests[0][1]['attributes'] == [{'value': 'dynamic_tag'}])
    expect(finish_tests[1][1]['attributes'] == [])
    expect(finish_tests[2][1]['attributes'] ==
           [{'value': 'multiple_tags_one'}, {'value': 'multiple_tags_two'}])
    assert_expectations()
