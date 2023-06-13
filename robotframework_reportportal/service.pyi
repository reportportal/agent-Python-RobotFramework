#  Copyright 2022 EPAM Systems
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

from logging import Logger
from typing import List, Optional, Text, Union

from reportportal_client.client import RPClient

from .model import Keyword as Keyword, Launch as Launch, \
    LogMessage as LogMessage, Suite as Suite, Test as Test

logger: Logger


def to_epoch(date: Optional[Text]) -> Optional[Text]: ...


class RobotService:
    agent_name: Text = ...
    agent_version: Text = ...
    rp: Optional[RPClient] = ...

    def __init__(self) -> None: ...

    def _get_launch_attributes(self, cmd_attrs: List) -> List: ...

    def init_service(self, endpoint: Text, project: Text, api_key: Text,
                     log_batch_size: int, pool_size: int, skipped_issue: bool,
                     verify_ssl: Union[Text, bool],
                     log_batch_payload_size: int, launch_id: str) -> None: ...

    def terminate_service(self) -> None: ...

    def start_launch(self, launch: Launch, mode: Optional[Text] = ...,
                     rerun: bool = ...,
                     rerun_of: Optional[Text] = ...,
                     ts: Optional[Text] = ...) -> Text: ...

    def finish_launch(self, launch: Launch,
                      ts: Optional[Text] = None) -> None: ...

    def start_suite(self, suite: Suite, ts: Optional[Text] = None): ...

    def finish_suite(self, suite: Suite, issue: Optional[Text] = ...,
                     ts: Optional[Text] = None) -> None: ...

    def start_test(self, test: Test, ts: Optional[Text] = None): ...

    def finish_test(self, test: Test, issue: Optional[Text] = ...,
                    ts: Optional[Text] = None) -> None: ...

    def start_keyword(self, keyword: Keyword, ts: Optional[Text] = None): ...

    def finish_keyword(self, keyword: Keyword, issue: Optional[Text] = ...,
                       ts: Optional[Text] = None) -> None: ...

    def log(self, message: LogMessage, ts: Optional[Text] = None) -> None: ...
