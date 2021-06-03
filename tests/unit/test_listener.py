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

import pytest
from six.moves import mock

from robotframework_reportportal.listener import listener
from tests import REPORT_PORTAL_SERVICE


class TestListener:

    @mock.patch(REPORT_PORTAL_SERVICE)
    def test_code_ref(self, mock_client_init, mock_listener,
                      test_attributes):
        mock_listener.start_test('Test', test_attributes)
        mock_client = mock_client_init.return_value
        assert mock_client.start_test_item.call_count == 1
        args, kwargs = mock_client.start_test_item.call_args
        assert (kwargs['code_ref'] ==
                '{0}:{1}'.format('robot/test.robot', 'Test'))

    # Robot Framework of versions < 4 does not bypass 'source' attribute on
    # 'start_test' method call
    @mock.patch(REPORT_PORTAL_SERVICE)
    def test_code_ref_robot_3_2_2(self, mock_client_init, mock_listener,
                                  suite_attributes, test_attributes):
        test_attributes = test_attributes.copy()
        del test_attributes['source']
        mock_listener.start_suite('Suite', suite_attributes)
        mock_listener.start_test('Test', test_attributes)
        mock_client = mock_client_init.return_value
        assert mock_client.start_test_item.call_count == 2
        args, kwargs = mock_client.start_test_item.call_args
        assert (kwargs['code_ref'] ==
                '{0}:{1}'.format('robot/test.robot', 'Test'))

    @mock.patch(REPORT_PORTAL_SERVICE)
    def test_code_ref_robot_3_2_2_no_source_in_parent(self, mock_client_init,
                                                      mock_listener,
                                                      test_attributes):
        test_attributes = test_attributes.copy()
        del test_attributes['source']
        mock_listener.start_test('Test', test_attributes)
        mock_client = mock_client_init.return_value
        assert mock_client.start_test_item.call_count == 1
        args, kwargs = mock_client.start_test_item.call_args
        assert (kwargs['code_ref'] == '{0}:{1}'.format(None, 'Test'))

    @mock.patch(REPORT_PORTAL_SERVICE)
    def test_suite_no_source_attribute(self, mock_client_init, mock_listener,
                                       suite_attributes, test_attributes):
        suite_attributes = suite_attributes.copy()
        del suite_attributes['source']
        del test_attributes['source']
        mock_listener.start_suite('Suite', suite_attributes)
        mock_listener.start_test('Test', test_attributes)
        mock_client = mock_client_init.return_value
        assert mock_client.start_test_item.call_count == 2
        args, kwargs = mock_client.start_test_item.call_args
        assert (kwargs['code_ref'] == '{0}:{1}'.format(None, 'Test'))

    @mock.patch(REPORT_PORTAL_SERVICE)
    def test_critical_test_failure(self, mock_client_init, mock_listener,
                                   test_attributes):
        mock_listener.start_test('Test', test_attributes)
        test_attributes['status'] = 'FAIL'
        mock_listener.end_test('Test', test_attributes)
        mock_client = mock_client_init.return_value
        assert mock_client.finish_test_item.call_count == 1
        args, kwargs = mock_client.finish_test_item.call_args
        assert kwargs['status'] == 'FAILED'

    @mock.patch(REPORT_PORTAL_SERVICE)
    def test_dynamic_attributes(self, mock_client_init, mock_listener,
                                test_attributes):
        test_attributes['tags'] = ['simple']
        mock_listener.start_test('Test', test_attributes)
        test_attributes['tags'] = ['simple', 'SLID:12345']
        test_attributes['status'] = 'PASS'
        mock_listener.end_test('Test', test_attributes)
        mock_client = mock_client_init.return_value
        assert mock_client.start_test_item.call_count == 1
        assert mock_client.finish_test_item.call_count == 1
        args, kwargs = mock_client.start_test_item.call_args
        assert kwargs['attributes'] == [{'value': 'simple'}]
        args, kwargs = mock_client.finish_test_item.call_args
        assert kwargs['attributes'] == [{'value': 'simple'},
                                        {'key': 'SLID', 'value': '12345'}]

    @mock.patch(REPORT_PORTAL_SERVICE)
    @pytest.mark.parametrize('critical, expected_status', [
        (True, 'FAILED'), ('yes', 'FAILED'), ('no', 'SKIPPED')])
    def test_non_critical_test_skip(
            self, mock_client_init, mock_listener,
            test_attributes, critical, expected_status):
        test_attributes['critical'] = critical
        mock_listener.start_test('Test', test_attributes)
        test_attributes['status'] = 'FAIL'
        mock_listener.end_test('Test', test_attributes)
        mock_client = mock_client_init.return_value
        assert mock_client.finish_test_item.call_count == 1
        args, kwargs = mock_client.finish_test_item.call_args
        assert kwargs['status'] == expected_status

    @mock.patch(REPORT_PORTAL_SERVICE)
    @pytest.mark.parametrize('skipped_issue_value', [True, False])
    def test_skipped_issue_variable_bypass(self, mock_client_init,
                                           mock_variables,
                                           skipped_issue_value):
        mock_variables.skipped_issue = skipped_issue_value
        mock_listener = listener()
        mock_listener._variables = mock_variables
        mock_listener.service
        assert mock_client_init.call_count == 1
        args, kwargs = mock_client_init.call_args
        assert kwargs['is_skipped_an_issue'] == skipped_issue_value

    @mock.patch(REPORT_PORTAL_SERVICE)
    def test_test_case_id(self, mock_client_init, mock_listener,
                          test_attributes):
        test_attributes['tags'] = ['simple', 'test_case_id:12345']
        mock_listener.start_test('Test', test_attributes)
        mock_client = mock_client_init.return_value
        assert mock_client.start_test_item.call_count == 1
        args, kwargs = mock_client.start_test_item.call_args
        assert kwargs['test_case_id'] == '12345'
        assert kwargs['attributes'] == [{'value': 'simple'}]
