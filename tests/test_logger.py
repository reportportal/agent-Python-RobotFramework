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

import utils
from six.moves import mock

from tests.conftest import REPORT_PORTAL_SERVICE


@mock.patch(REPORT_PORTAL_SERVICE)
def test_launch_log(mock_client_init):
    utils.run_robot_tests('examples/launch_log.robot')

    mock_client = mock_client_init.return_value
    calls = list(
        filter(lambda x: 'item_id' in x[1] and x[1]['item_id'] is None,
               mock_client.log.call_args_list)
    )
    assert len(calls) == 3

    messages = set(map(lambda x: x[1]['message'], calls))
    assert messages == {'Hello, world!', 'Goodbye, world!', 'Enjoy my pug!'}
