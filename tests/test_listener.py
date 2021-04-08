from six.moves import mock

from robotframework_reportportal.listener import listener

ROBOT_SERVICE = 'robotframework_reportportal.service.ReportPortalService'


class TestListener(object):

    @mock.patch(ROBOT_SERVICE)
    def test_critical_test_failure(self, mock_init, mock_variables,
                                   suite_attributes, test_attributes):
        mock_client = mock_init.return_value
        listener_obj = listener()
        listener_obj._variables = mock_variables
        listener_obj.start_suite("Suite", suite_attributes)
        listener_obj.start_test("Test", test_attributes)
        test_attributes['status'] = 'FAIL'
        listener_obj.end_test('Test', test_attributes)

        assert mock_client.finish_test_item.call_count == 1
        args, kwargs = mock_client.finish_test_item.call_args
        assert kwargs['status'] == 'FAILED'

    @mock.patch(ROBOT_SERVICE)
    def test_non_critical_test_skip(self, mock_init, mock_variables,
                                    suite_attributes, test_attributes):
        mock_client = mock_init.return_value
        listener_obj = listener()
        listener_obj._variables = mock_variables
        listener_obj.start_suite("Suite", suite_attributes)
        test_attributes['critical'] = 'no'
        listener_obj.start_test("Test", test_attributes)
        test_attributes['status'] = 'FAIL'
        listener_obj.end_test('Test', test_attributes)

        assert mock_client.finish_test_item.call_count == 1
        args, kwargs = mock_client.finish_test_item.call_args
        assert kwargs['status'] == 'SKIPPED'
