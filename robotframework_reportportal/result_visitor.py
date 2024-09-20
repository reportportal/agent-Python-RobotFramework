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

import re
import string
import sys
from datetime import datetime, timedelta, timezone

if sys.version_info >= (3, 9):
    from zoneinfo import available_timezones, ZoneInfo
from typing import List, Pattern, Optional
from urllib.parse import unquote

from robot.result import ResultVisitor, Result, TestSuite, TestCase, Keyword, Message

from robotframework_reportportal import listener
from robotframework_reportportal.time_visitor import corrections
# noinspection PyUnresolvedReferences
from robotframework_reportportal.variables import _variables

listener = listener.listener()
if sys.version_info >= (3, 9):
    AVAILABLE_TIMEZONES: set[str] = available_timezones()
else:
    AVAILABLE_TIMEZONES = set()


def to_timestamp(time_str: str) -> Optional[str]:
    if not time_str:
        return None

    timezone_offset_str: Optional[str] = _variables.get('RP_TIME_ZONE_OFFSET', None)
    dt = datetime.strptime(time_str, '%Y%m%d %H:%M:%S.%f')

    if timezone_offset_str:
        if timezone_offset_str in AVAILABLE_TIMEZONES:
            tz = ZoneInfo(timezone_offset_str)
            dt = dt.replace(tzinfo=tz)
        else:
            hours, minutes = map(int, timezone_offset_str.split(':'))
            offset = timedelta(hours=hours, minutes=minutes)
            dt = dt.replace(tzinfo=timezone(offset))
    return str(int(dt.timestamp() * 1000))


class RobotResultsVisitor(ResultVisitor):
    _link_pattern: Pattern = re.compile("src=[\"\']([^\"\']+)[\"\']")

    def start_result(self, result: Result) -> bool:
        if "RP_LAUNCH" not in _variables:
            _variables["RP_LAUNCH"] = result.suite.name
        if "RP_LAUNCH_DOC" not in _variables:
            _variables["RP_LAUNCH_DOC"] = result.suite.doc
        return True

    def start_suite(self, suite: TestSuite) -> bool:
        ts = to_timestamp(suite.starttime if suite.id not in corrections else corrections[suite.id][0])
        attrs = {
            'id': suite.id,
            'longname': suite.longname,
            'doc': suite.doc,
            'metadata': suite.metadata,
            'source': suite.source,
            'suites': suite.suites,
            'tests': suite.tests,
            'totaltests': getattr(suite.statistics, 'all', suite.statistics).total,
            'starttime': ts
        }
        listener.start_suite(suite.name, attrs, ts)
        return True

    def end_suite(self, suite: TestSuite) -> None:
        ts = to_timestamp(suite.endtime if suite.id not in corrections else corrections[suite.id][1])
        attrs = {
            'id': suite.id,
            'longname': suite.longname,
            'doc': suite.doc,
            'metadata': suite.metadata,
            'source': suite.source,
            'suites': suite.suites,
            'tests': suite.tests,
            'totaltests': getattr(suite.statistics, 'all', suite.statistics).total,
            'endtime': ts,
            'elapsedtime': suite.elapsedtime,
            'status': suite.status,
            'statistics': suite.statistics,
            'message': suite.message,
        }
        listener.end_suite(None, attrs, ts)

    def start_test(self, test: TestCase) -> bool:
        ts = to_timestamp(test.starttime if test.id not in corrections else corrections[test.id][0])
        attrs = {
            'id': test.id,
            'longname': test.longname,
            # 'originalname': test.originalname,
            'doc': test.doc,
            'tags': list(test.tags),
            # for backward compatibility with Robot < 4.0 mark every test case
            # as critical if not set
            'critical': getattr(test, 'critical', 'yes'),
            'source': test.source,
            'template': '',
            # 'lineno': test.lineno,
            'starttime': ts,
        }
        listener.start_test(test.name, attrs, ts)
        return True

    def end_test(self, test: TestCase) -> None:
        ts = to_timestamp(test.endtime if test.id not in corrections else corrections[test.id][1])
        attrs = {
            'id': test.id,
            'longname': test.longname,
            # 'originalname': test.originalname,
            'doc': test.doc,
            'tags': list(test.tags),
            # for backward compatibility with Robot < 4.0 mark every test case
            # as critical if not set
            'critical': getattr(test, 'critical', 'yes'),
            'template': '',
            # 'lineno': test.lineno,
            'endtime': ts,
            'elapsedtime': test.elapsedtime,
            'source': test.source,
            'status': test.status,
            'message': test.message,
        }
        listener.end_test(test.name, attrs, ts)

    def start_keyword(self, kw: Keyword) -> bool:
        ts = to_timestamp(kw.starttime if kw.id not in corrections else corrections[kw.id][0])
        attrs = {
            'type': string.capwords(kw.type),
            'kwname': kw.kwname,
            'libname': kw.libname,
            'doc': kw.doc,
            'args': kw.args,
            'assign': kw.assign,
            'tags': kw.tags,
            'starttime': ts,
        }
        listener.start_keyword(kw.name, attrs, ts)
        return True

    def end_keyword(self, kw: Keyword) -> None:
        ts = to_timestamp(kw.endtime if kw.id not in corrections else corrections[kw.id][1])
        attrs = {
            'type': string.capwords(kw.type),
            'kwname': kw.kwname,
            'libname': kw.libname,
            'doc': kw.doc,
            'args': kw.args,
            'assign': kw.assign,
            'tags': kw.tags,
            'endtime': ts,
            'elapsedtime': kw.elapsedtime,
            'status': 'PASS' if kw.assign else kw.status,
        }
        listener.end_keyword(kw.name, attrs, ts)

    def start_message(self, msg: Message) -> bool:
        if msg.message:
            message = {
                'message': msg.message,
                'level': msg.level,
            }
            try:
                m = self.parse_message(message['message'])
                message["message"] = m[0]
                listener.log_message_with_image(message, m[1])
            except (AttributeError, IOError):
                # noinspection PyBroadException
                try:
                    listener.log_message(message)
                except Exception:
                    return False
        return True

    def parse_message(self, msg: str) -> List[str]:
        m = self._link_pattern.search(msg)
        return [m.group(), unquote(m.group(1))]
