# ReportPortal RobotFramework agent 

[![Build Status](https://travis-ci.org/reportportal/agent-Python-RobotFramework.svg?branch=master)](https://travis-ci.org/reportportal/agent-Python-RobotFramework)
[![PyPI](https://img.shields.io/pypi/v/robotframework-reportportal.svg?maxAge=2592000)](https://pypi.python.org/pypi/robotframework-reportportal)

Listener for RobotFramework to report results to ReportPortal

## Installation

First you need to install RobotFramework:

    pip install robotframework

The latest stable version of library is available on PyPI:

    pip install robotframework-reportportal

[reportportal-client](https://github.com/reportportal/client-Python) will be installed as a dependency

## Usage

For reporting results to ReportPortal you need to pass some variables to pybot run:

REQUIRED:
- --listener robotframework_reportportal.listener
- --variable RP_UUID:"your_user_uuid"
- --variable RP_ENDPOINT:"your_reportportal_url"
- --variable RP_LAUNCH:"launch_name"
- --variable RP_PROJECT:"reportportal_project_name"

NOT REQUIRED:
- --variable RP_LAUNCH_DOC:"some_documentation_for_launch"
- --variable RP_REPORT_LEVEL:"level_test_or_keyword"
    - Default is "keyword", but if you want to report only tests you can use "test" value
- --variable RP_REPORT_LOGS:"yes_or_no"
    - Default is "yes", but if you don't want to report logs you can use "no" value

## Copyright Notice
Licensed under the [GPLv3](https://www.gnu.org/licenses/quick-guide-gplv3.html)
license (see the LICENSE.txt file).
