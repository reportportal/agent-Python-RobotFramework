"""This module contains utility code for unit tests."""
#  Copyright 2021 EPAM Systems
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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

    if type(tests) is list:
        for t in tests:
            arguments.append(t)
    else:
        arguments.append(tests)

    RobotFramework().execute_cli(arguments, False)
