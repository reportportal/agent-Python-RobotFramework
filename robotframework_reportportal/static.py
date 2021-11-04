"""This module includes static variables of the agent.

Copyright (c) 2021 http://reportportal.io .
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


LOG_LEVEL_MAPPING = {
    'INFO': 'INFO',
    'FAIL': 'ERROR',
    'TRACE': 'TRACE',
    'DEBUG': 'DEBUG',
    'HTML': 'INFO',
    'WARN': 'WARN',
    'ERROR': 'ERROR',
    'SKIP': 'INFO'
}
MAIN_SUITE_ID = 's1'
PABOT_WIHOUT_LAUNCH_ID_MSG = (
    'Pabot library is used but RP_LAUNCH_UUID was not provided. Please, '
    'initialize listener with the RP_LAUNCH_UUID argument.')
STATUS_MAPPING = {
    'PASS': 'PASSED',
    'FAIL': 'FAILED',
    'NOT RUN': 'SKIPPED',
    'SKIP': 'SKIPPED'
}
