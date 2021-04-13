import pytest
from six.moves import mock

from robotframework_reportportal.listener import listener

REPORT_PORTAL_SERVICE = \
    'robotframework_reportportal.service.ReportPortalService'


class TestListener:

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
    def test_non_critical_test_skip(self, mock_client_init, mock_listener,
                                    test_attributes):
        test_attributes['critical'] = 'no'
        mock_listener.start_test('Test', test_attributes)
        test_attributes['status'] = 'FAIL'
        mock_listener.end_test('Test', test_attributes)

        mock_client = mock_client_init.return_value
        assert mock_client.finish_test_item.call_count == 1
        args, kwargs = mock_client.finish_test_item.call_args
        assert kwargs['status'] == 'SKIPPED'

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
