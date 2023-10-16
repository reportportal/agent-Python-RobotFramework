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
from datetime import datetime

from robot.api import ResultVisitor
from urllib.parse import unquote

from . import listener
from .time_visitor import corrections
# noinspection PyUnresolvedReferences
from .variables import _variables


listener = listener.listener()


def to_timestamp(time_str):
    if time_str:
        dt = datetime.strptime(time_str, '%Y%m%d %H:%M:%S.%f')
        return str(int(dt.timestamp() * 1000))
    return None


class RobotResultsVisitor(ResultVisitor):
    _link_pattern = re.compile("src=[\"\']([^\"\']+)[\"\']")

    def start_result(self, result):
        if "RP_LAUNCH" not in _variables:
            _variables["RP_LAUNCH"] = result.suite.name
        if "RP_LAUNCH_DOC" not in _variables:
            _variables["RP_LAUNCH_DOC"] = result.suite.doc

    def start_suite(self, suite):
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

    def end_suite(self, suite):
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

    def start_test(self, test):
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

    def end_test(self, test):
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

    def start_keyword(self, kw):
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

    def end_keyword(self, kw):
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

    def start_message(self, msg):
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
                    pass

    def parse_message(self, msg):
        m = self._link_pattern.search(msg)
        return [m.group(), unquote(m.group(1))]
