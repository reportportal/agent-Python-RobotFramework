"""Robot Framework test report sender to Report Portal

This tool replays a Robot Framework test session using the output XML file
with ReportPortal's listener agent injected without actually doing the test.
This will allow all the test results to be sent to ReportPortal, after the
test is run. By doing this, we will not disturb the timing when the test is
run. It also has the benefit of using the test result generated after running
multiple parallel robot testing (eg. by using pabot).

Command-line usage:

    post_report --variable RP_UUID:"your_user_uuid"
                --variable RP_ENDPOINT:"your_reportportal_url"
                --variable RP_PROJECT:"reportportal_project_name"
                [--variable RP_LAUNCH:"launch_name"]
                [--variable RP_LAUNCH_DOC:"some_documentation_for_launch"]
                [--variable RP_LAUNCH_ATTRIBUTES:"RF tag_name:tag_value"]
                [--variable RP_TEST_ATTRIBUTES:"Long"]
                [--variable RP_LOG_BATCH_SIZE:"10"]
                [output.xml]

This script needs to be run within the same directory as the report xml file.
Attachments mentioned in the log messages will be referred relative to
current dir.
"""

import sys
import getopt

from robot.api import ExecutionResult
from robotframework_reportportal.result_visitor import RobotResultsVisitor
from robotframework_reportportal.variables import _variables, Variables


def process(infile="output.xml"):
    visitor = RobotResultsVisitor()
    test_run = ExecutionResult(infile)
    test_run.visit(visitor)


def main():
    argument_list = sys.argv[1:]
    short_options = "hv:"
    long_options = ["help", "variable="]
    try:
        arguments, values = getopt.getopt(argument_list, short_options,
                                          long_options)
    except getopt.error as err:
        sys.exit(1)

    for current_argument, current_value in arguments:
        if current_argument in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        elif current_argument in ("-v", "--variable"):
            k, v = str(current_value).split(":", 1)
            _variables[k] = v

    try:
        rc = process(*values)
    except TypeError:
        print(__doc__)
        sys.exit(1)
    sys.exit(rc)


if __name__ == "__main__":
    main()
