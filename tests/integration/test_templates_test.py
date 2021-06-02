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
import sys

import pytest
from delayed_assert import assert_expectations, expect
from six.moves import mock

from tests import REPORT_PORTAL_SERVICE
from tests.helpers import utils

KEYWORDS_EXPECTED_TEST_NAMES = ['Invalid Password']
KEYWORDS_EXPECTED_CODE_REF_SUFFIXES = KEYWORDS_EXPECTED_TEST_NAMES

SETTINGS_EXPECTED_TEST_NAMES = ['Invalid User Name', 'Invalid Password',
                                'Invalid User Name and Password',
                                'Empty User Name',
                                'Empty Password',
                                'Empty User Name and Password']
SETTINGS_EXPECTED_CODE_REF_SUFFIXES = SETTINGS_EXPECTED_TEST_NAMES

DATADRIVER_EXPECTED_TEST_NAMES = \
    ['Login with user \'invalid\' and password \'Password\'',
     'Login with user \'User\' and password \'invalid\'',
     'Login with user \'invalid\' and password \'invalid\'',
     'Login with user \'\' and password \'Password\'',
     'Login with user \'User\' and password \'\'',
     'Login with user \'\' and password \'\'']
DATADRIVER_EXPECTED_CODE_REF_SUFFIXES = \
    ['Login with user \'${username}\' and password \'${password}\'',
     'Login with user \'${username}\' and password \'${password}\'',
     'Login with user \'${username}\' and password \'${password}\'',
     'Login with user \'${username}\' and password \'${password}\'',
     'Login with user \'${username}\' and password \'${password}\'',
     'Login with user \'${username}\' and password \'${password}\'']


@pytest.mark.parametrize(
    'test,test_names,code_ref_suffixes',
    [('examples/templates/keyword.robot', KEYWORDS_EXPECTED_TEST_NAMES,
      KEYWORDS_EXPECTED_CODE_REF_SUFFIXES),
     ('examples/templates/settings.robot', SETTINGS_EXPECTED_TEST_NAMES,
      SETTINGS_EXPECTED_CODE_REF_SUFFIXES),
     ('examples/templates/datadriver.robot', DATADRIVER_EXPECTED_TEST_NAMES,
      DATADRIVER_EXPECTED_CODE_REF_SUFFIXES)])
@mock.patch(REPORT_PORTAL_SERVICE)
def test_code_reference_settings_template(mock_client_init, test, test_names,
                                          code_ref_suffixes):
    if test.endswith('datadriver.robot') and sys.version_info < (3, 6):
        return  # DataDriver requires Python 3.6
    result = utils.run_robot_tests([test])
    assert result == 0  # the test successfully passed

    mock_client = mock_client_init.return_value
    calls = list(
        filter(lambda x: x[1]['item_type'] == 'STEP'
                         and x[1].get('has_stats', True) is True,
               mock_client.start_test_item.call_args_list)
    )
    assert len(calls) == len(test_names)

    for i, call in enumerate(calls):
        code_ref = call[1]['code_ref']
        test_case_id = call[1]['test_case_id']
        expect(test_case_id == test + ':' + test_names[i])
        expect(code_ref == test + ':' + code_ref_suffixes[i])

    assert_expectations()
