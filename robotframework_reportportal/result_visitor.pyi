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

from typing import Pattern, List
from .listener import listener as ls
from robot.result import ResultVisitor, Result, TestSuite, TestCase, Keyword, Message

listener: ls

class RobotResultsVisitor(ResultVisitor):
    def __init__(self):
        self._link_pattern = Pattern

    def start_result(self, result: Result) -> bool: ...

    def start_suite(self, suite: TestSuite) -> bool: ...

    def end_suite(self, suite: TestSuite) -> None: ...

    def start_test(self, test: TestCase) -> bool: ...

    def end_test(self, test: TestCase) -> None: ...

    def start_keyword(self, kw: Keyword) -> bool: ...

    def end_keyword(self, kw: Keyword) -> None: ...

    def start_message(self, msg: Message) -> bool: ...

    def parse_message(self, param) -> List[str]: ...
