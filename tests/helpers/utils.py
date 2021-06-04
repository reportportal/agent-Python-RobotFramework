"""This module contains utility code for unit tests.

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

from robot.run import RobotFramework

DEFAULT_VARIABLES = {
    'RP_LAUNCH': 'Robot Framework',
    'RP_ENDPOINT': "http://localhost:8080",
    'RP_PROJECT': "default_personal",
    'RP_UUID': "test_uuid",
    'RP_ATTACH_REPORT': False
}


def run_robot_tests(tests, listener='robotframework_reportportal.listener',
                    variables=None):
    if variables is None:
        variables = DEFAULT_VARIABLES

    arguments = ['--listener', listener]
    for k, v in variables.items():
        arguments.append('--variable')
        if type(v) is str:
            arguments.append(k + ':' + '"' + v + '"')
        else:
            arguments.append(k + ':' + str(v))

    for t in tests:
        arguments.append(t)

    return RobotFramework().execute_cli(arguments, False)


def get_launch_log_calls(mock):
    return [e for e in
            filter(lambda x: 'item_id' in x[1] and x[1]['item_id'] is None,
                   mock.log.call_args_list)]
