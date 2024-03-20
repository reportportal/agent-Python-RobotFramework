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

"""This module includes static variables of the agent."""

from typing import Dict

LOG_LEVEL_MAPPING: Dict[str, str] = {
    'INFO': 'INFO',
    'FAIL': 'ERROR',
    'TRACE': 'TRACE',
    'DEBUG': 'DEBUG',
    'HTML': 'INFO',
    'WARN': 'WARN',
    'ERROR': 'ERROR',
    'SKIP': 'INFO'
}
MAIN_SUITE_ID: str = 's1'
PABOT_WITHOUT_LAUNCH_ID_MSG: str = ('Pabot library is used but RP_LAUNCH_UUID was not provided. Please, '
                                    'initialize listener with the RP_LAUNCH_UUID argument.')
STATUS_MAPPING: Dict[str, str] = {
    'PASS': 'PASSED',
    'FAIL': 'FAILED',
    'NOT RUN': 'SKIPPED',
    'SKIP': 'SKIPPED'
}
