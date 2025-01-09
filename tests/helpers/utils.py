#  Copyright 2023 EPAM Systems
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""This module contains utility code for unit tests."""

import random
import time
from typing import Any, Dict, List, Optional, Tuple

from robot.run import RobotFramework

DEFAULT_VARIABLES: Dict[str, Any] = {
    "RP_LAUNCH": "Robot Framework",
    "RP_ENDPOINT": "http://localhost:8080",
    "RP_PROJECT": "default_personal",
    "RP_API_KEY": "test_api_key",
    "RP_ATTACH_REPORT": False,
}


def run_robot_tests(
    tests: List[str],
    listener: str = "robotframework_reportportal.listener",
    variables: Optional[Dict[str, Any]] = None,
    arguments: Optional[Dict[str, Any]] = None,
) -> int:
    cmd_arguments = ["--listener", listener]
    if arguments:
        for k, v in arguments.items():
            cmd_arguments.append(k)
            cmd_arguments.append(v)

    if variables is None:
        variables = DEFAULT_VARIABLES

    for k, v in variables.items():
        cmd_arguments.append("--variable")
        if type(v) is not str:
            v = str(v)
        cmd_arguments.append(k + ":" + v)

    for t in tests:
        cmd_arguments.append(t)

    return RobotFramework().execute_cli(cmd_arguments, False)


def get_launch_log_calls(mock) -> List[Tuple[List[Any], Dict[str, Any]]]:
    return [e for e in mock.log.call_args_list if "item_id" in e[1] and e[1]["item_id"] is None]


def get_log_calls(mock) -> List[Tuple[List[Any], Dict[str, Any]]]:
    return [e for e in mock.log.call_args_list if "item_id" in e[1] and e[1]["item_id"]]


def item_id_gen(**kwargs) -> str:
    return "{}-{}-{}".format(kwargs["name"], str(round(time.time() * 1000)), random.randint(0, 9999))
