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

from delayed_assert import assert_expectations, expect
from six.moves import mock

from tests import REPORT_PORTAL_SERVICE
from tests.helpers import utils


@mock.patch(REPORT_PORTAL_SERVICE)
def test_code_reference_template(mock_client_init, test, test_names,
                                 code_ref_suffixes):
    result = utils.run_robot_tests([test])
    assert result == 0  # the test successfully passed

    mock_client = mock_client_init.return_value
    calls = [call for call in mock_client.start_test_item.call_args_list if call[1]['item_type'] == 'STEP' and call[1].get('has_stats', True) is True]
        filter(lambda x: x[1]['item_type'] == 'STEP'
               and x[1].get('has_stats', True) is True,
               mock_client.start_test_item.call_args_list)
    )
    assert len(calls) == len(test_names)

    for call, test_name, code_ref_suff in zip(calls, test_names,
                                              code_ref_suffixes):
        code_ref = call[1]['code_ref']
        test_case_id = call[1]['test_case_id']
        expect(test_case_id == test + ':' + test_name)
        expect(code_ref == test + ':' + code_ref_suff)

    assert_expectations()
