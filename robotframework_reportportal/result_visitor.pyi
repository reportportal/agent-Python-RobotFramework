# make_stub_files: Thu 22 Oct 2020 at 15:38:24
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
