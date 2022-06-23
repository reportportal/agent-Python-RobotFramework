"""This module contains utility code for unit tests.

Copyright (c) 2021 https://reportportal.io .
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License
"""
import random
import time

from robot.run import RobotFramework

DEFAULT_VARIABLES = {
    'RP_LAUNCH': 'Robot Framework',
    'RP_ENDPOINT': "http://localhost:8080",
    'RP_PROJECT': "default_personal",
    'RP_UUID': "test_uuid",
    'RP_ATTACH_REPORT': False
}


def run_robot_tests(tests, listener='robotframework_reportportal.listener',
                    variables=None, arguments=None):
    cmd_arguments = ['--listener', listener]
    if arguments:
        for k, v in arguments.items():
            cmd_arguments.append(k)
            cmd_arguments.append(v)

    if variables is None:
        variables = DEFAULT_VARIABLES

    for k, v in variables.items():
        cmd_arguments.append('--variable')
        if type(v) is str:
            cmd_arguments.append(k + ':' + '"' + v + '"')
        else:
            cmd_arguments.append(k + ':' + str(v))

    for t in tests:
        cmd_arguments.append(t)

    return RobotFramework().execute_cli(cmd_arguments, False)


def get_launch_log_calls(mock):
    return [e for e in mock.log.call_args_list
            if 'item_id' in e[1] and e[1]['item_id'] is None]


def item_id_gen(**kwargs):
    return "{}-{}-{}".format(kwargs['name'], str(round(time.time() * 1000)),
                             random.randint(0, 9999))
