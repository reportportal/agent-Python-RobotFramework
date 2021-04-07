from six.moves import mock

from robotframework_reportportal import listener

ROBOT_SERVICE = 'robotframework_reportportal.service.RobotService.'


class TestListener(object):

    @mock.patch(ROBOT_SERVICE + 'init_service')
    def test_critical_test_failure(self, mock_init, mock_variables,
                                   suite_attributes, mock_client,
                                   test_attributes):
        with mock.patch('robotframework_reportportal.listener.VARIABLES',
                        mock_variables):
            listener.start_suite("Suite", suite_attributes)
            listener.start_test("Test", test_attributes)
            test_attributes['status'] = 'FAIL'
            listener.end_test('Test', test_attributes)

            assert mock_client.finish_test_item.call_count == 1
            args, kwargs = mock_client.finish_test_item.call_args
            assert kwargs['status'] == 'FAILED'


    @mock.patch(ROBOT_SERVICE + 'init_service')
    def test_non_critical_test_skip(self, mock_init, mock_variables,
                                    suite_attributes, mock_client,
                                    test_attributes):
        with mock.patch('robotframework_reportportal.listener.VARIABLES',
                        mock_variables):
            listener.start_suite("Suite", suite_attributes)
            test_attributes['critical'] = 'no'
            listener.start_test("Test", test_attributes)
            test_attributes['status'] = 'FAIL'
            listener.end_test('Test', test_attributes)

            assert mock_client.finish_test_item.call_count == 1
            args, kwargs = mock_client.finish_test_item.call_args
            assert kwargs['status'] == 'SKIPPED'
