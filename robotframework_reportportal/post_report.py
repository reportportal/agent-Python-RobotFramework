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

"""Robot Framework test report sender to ReportPortal.

This tool replays a Robot Framework test session using the output XML file
with ReportPortal's listener agent injected without actually doing the test.
This will allow all the test results to be sent to ReportPortal, after the
test is run. By doing this, we will not disturb the timing when the test is
run. It also has the benefit of using the test result generated after running
multiple parallel robot testing (eg. by using pabot).

Command-line usage:

    post_report --variable RP_API_KEY:"your_user_api_key"
                --variable RP_ENDPOINT:"your_reportportal_url"
                --variable RP_PROJECT:"reportportal_project_name"
                [--variable RP_LAUNCH:"launch_name"]
                [--variable RP_LAUNCH_DOC:"some_documentation_for_launch"]
                [--variable RP_LAUNCH_ATTRIBUTES:"RF tag_name:tag_value"]
                [--variable RP_TEST_ATTRIBUTES:"Long"]
                [--variable RP_LOG_BATCH_SIZE:"10"]
                [--variable RP_MAX_POOL_SIZE:"50"]
                [--variable RP_MODE:"DEBUG"]
                [--loglevel CRITICAL|ERROR|WARNING|INFO|DEBUG]
                [--timezone "+03:00"|"EST"|"Europe/Warsaw"]
                [output.xml]

This script needs to be run within the same directory as the report xml file.
Attachments mentioned in the log messages will be referred relative to
current dir.
"""

import getopt
import logging
import sys

from robot.api import ExecutionResult

from robotframework_reportportal.result_visitor import RobotResultsVisitor
from robotframework_reportportal.time_visitor import TimeVisitor, corrections
# noinspection PyUnresolvedReferences
from robotframework_reportportal.variables import _variables


def process(infile="output.xml"):
    test_run = ExecutionResult(infile)
    test_run.visit(TimeVisitor())
    if corrections:
        logging.warning("{0} is missing some of its starttime/endtime. "
                        "This might cause inconsistencies with your "
                        "duration report.".format(infile))
    test_run.visit(RobotResultsVisitor())


def main():
    argument_list = sys.argv[1:]
    short_options = "hv:"
    long_options = ["help", "variable=", "loglevel=", 'timezone=']
    try:
        arguments, values = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error:
        sys.exit(1)

    for current_argument, current_value in arguments:
        if current_argument in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        elif current_argument in ("-v", "--variable"):
            k, v = str(current_value).split(":", 1)
            _variables[k] = v
        elif current_argument == "--loglevel":
            numeric_level = getattr(logging, current_value.upper(), None)
            logging.basicConfig(level=numeric_level)
        elif current_argument == "--timezone":
            _variables['RP_TIME_ZONE_OFFSET'] = current_value

    try:
        process(*values)
    except TypeError:
        print(__doc__)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
