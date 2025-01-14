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
from typing import Iterable, Optional, Tuple


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
