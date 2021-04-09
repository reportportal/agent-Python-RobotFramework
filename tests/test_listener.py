from six.moves import mock

ROBOT_SERVICE = 'robotframework_reportportal.service.ReportPortalService'


class TestListener:

    @mock.patch(ROBOT_SERVICE)
    def test_critical_test_failure(self, mock_init, mock_listener,
                                   test_attributes):
        mock_listener.start_test("Test", test_attributes)
        test_attributes['status'] = 'FAIL'
        mock_listener.end_test('Test', test_attributes)

        mock_client = mock_init.return_value
        assert mock_client.finish_test_item.call_count == 1
        args, kwargs = mock_client.finish_test_item.call_args
        assert kwargs['status'] == 'FAILED'

    @mock.patch(ROBOT_SERVICE)
    def test_non_critical_test_skip(self, mock_init, mock_listener,
                                    test_attributes):
        test_attributes['critical'] = 'no'
        mock_listener.start_test("Test", test_attributes)
        test_attributes['status'] = 'FAIL'
        mock_listener.end_test('Test', test_attributes)

        mock_client = mock_init.return_value
        assert mock_client.finish_test_item.call_count == 1
        args, kwargs = mock_client.finish_test_item.call_args
        assert kwargs['status'] == 'SKIPPED'
