from six.moves import mock

REPORT_PORTAL_SERVICE = \
    'robotframework_reportportal.service.ReportPortalService'


class TestListener:

    @mock.patch(REPORT_PORTAL_SERVICE)
    def test_code_ref(self, mock_client_init, mock_listener,
                      test_attributes):
        mock_listener.start_test('Test', test_attributes)
        mock_client = mock_client_init.return_value
        assert mock_client.start_test_item.call_count == 1
        args, kwargs = mock_client.start_test_item.call_args
        assert (kwargs['code_ref'] ==
                '{0}:{1}'.format(test_attributes['source'], 'Test'))

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
    def test_test_case_id(self, mock_client_init, mock_listener,
                          test_attributes):
        test_attributes['tags'] = ['simple', 'test_case_id:12345']
        mock_listener.start_test('Test', test_attributes)
        mock_client = mock_client_init.return_value
        assert mock_client.start_test_item.call_count == 1
        args, kwargs = mock_client.start_test_item.call_args
        assert kwargs['test_case_id'] == '12345'
        assert kwargs['attributes'] == [{'value': 'simple'}]
