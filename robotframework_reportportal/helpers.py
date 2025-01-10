#  Copyright 2024 EPAM Systems
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""This module contains functions to ease reporting to ReportPortal."""

import binascii
import fnmatch
import re
from abc import ABC, abstractmethod
from typing import Callable, Iterable, Optional, Tuple

from robotframework_reportportal.model import Keyword


def translate_glob_to_regex(pattern: Optional[str]) -> Optional[re.Pattern]:
    """Translate glob string pattern to regex Pattern.

    :param pattern: glob pattern
    :return: regex pattern
    """
    if pattern is None:
        return None
    if pattern == "":
        return PATTERN_MATCHES_EMPTY_STRING
    return re.compile(fnmatch.translate(pattern))


def match_pattern(pattern: Optional[re.Pattern], line: Optional[str]) -> bool:
    """Check if the line matches given pattern. Handles None values.

    :param pattern: regex pattern
    :param line: line to check
    :return: True if the line matches the pattern, False otherwise
    """
    if pattern is None:
        return True
    if line is None:
        return False

    return pattern.fullmatch(line) is not None


class KeywordMatch(ABC):
    """Base class for keyword matchers."""

    @abstractmethod
    def match(self, kw: Keyword) -> bool:
        """Check if the keyword matches the criteria."""


class KeywordEqual(KeywordMatch):
    """Match keyword based on a predicate."""

    predicate: Callable[[Keyword], bool]

    def __init__(self, predicate: Callable[[Keyword], bool] = None) -> None:
        """Initialize the matcher with the predicate."""
        self.predicate = predicate

    def match(self, kw: Keyword) -> bool:
        """Check if the keyword matches the criteria."""
        return self.predicate(kw)


class KeywordNameMatch(KeywordEqual):
    """Match keyword based on the name pattern."""

    def __init__(self, pattern: Optional[str]) -> None:
        """Initialize the matcher with the pattern."""
        super().__init__(lambda kw: match_pattern(pattern, kw.name))


class KeywordTypeEqual(KeywordEqual):
    """Match keyword based on the type."""

    def __init__(self, expected_value: Optional[str]) -> None:
        """Initialize the matcher with the expected value."""
        super().__init__(lambda kw: kw.keyword_type == expected_value)


class KeywordTagMatch(KeywordMatch):
    """Match keyword based on the tag pattern."""

    pattern: Optional[re.Pattern]

    def __init__(self, pattern: Optional[str]) -> None:
        """Initialize the matcher with the pattern."""
        self.pattern = translate_glob_to_regex(pattern)

    def match(self, kw: Keyword) -> bool:
        """Check if the keyword matches the criteria."""
        return next((True for t in kw.tags if match_pattern(self.pattern, t)), False)


class KeywordStatusEqual(KeywordEqual):
    """Match keyword based on the status."""

    def __init__(self, status: str) -> None:
        """Initialize the matcher with the status."""
        super().__init__(lambda kw: kw.status == status)


def replace_patterns(text: str, patterns: Iterable[Tuple[re.Pattern, str]]) -> str:
    """Replace given patterns in the text."""
    result = text
    for p, repl in patterns:
        result = p.sub(repl, result)
    return result


BARE_LINK_PATTERN = re.compile(r"\[\s*([^]|]+)]")
NAMED_LINK_PATTERN = re.compile(r"\[\s*([^]|]+)\|\s*([^]]+)]")

ROBOT_MARKUP_REPLACEMENT_PATTERS = [
    (BARE_LINK_PATTERN, r"<\1>"),
    (NAMED_LINK_PATTERN, r"[\2](\1)"),
]

PATTERN_MATCHES_EMPTY_STRING: re.Pattern = re.compile("^$")


def robot_markup_to_markdown(text: str) -> str:
    """Convert Robot Framework's text markup to Markdown format."""
    return replace_patterns(text, ROBOT_MARKUP_REPLACEMENT_PATTERS)


def _unescape(binary_string: str, stop_at: int = -1):
    result = bytearray()
    join_list = list()
    join_idx = -3
    skip_next = False
    for i, b in enumerate(binary_string):
        if skip_next:
            skip_next = False
            continue
        if i < join_idx + 2:
            join_list.append(b)
            continue
        else:
            if len(join_list) > 0:
                for bb in binascii.unhexlify("".join(join_list)):
                    result.append(bb)
                    if stop_at > 0:
                        if len(result) >= stop_at:
                            break
                join_list = list()
        if b == "\\" and binary_string[i + 1] == "x":
            skip_next = True
            join_idx = i + 2
            continue
        for bb in b.encode("utf-8"):
            result.append(bb)
            if stop_at > 0:
                if len(result) >= stop_at:
                    break
    if len(join_list) > 0:
        for bb in binascii.unhexlify("".join(join_list)):
            result.append(bb)
    return result
