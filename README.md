# ReportPortal RobotFramework agent

[![PyPI](https://img.shields.io/pypi/v/robotframework-reportportal.svg?maxAge=259200)](https://pypi.python.org/pypi/robotframework-reportportal)
[![Python versions](https://img.shields.io/pypi/pyversions/robotframework-reportportal.svg)](https://pypi.org/project/robotframework-reportportal)
[![Build Status](https://github.com/reportportal/agent-Python-RobotFramework/actions/workflows/tests.yml/badge.svg)](https://github.com/reportportal/agent-Python-RobotFramework/actions/workflows/tests.yml)
[![codecov.io](https://codecov.io/gh/reportportal/agent-Python-RobotFramework/branch/master/graph/badge.svg)](https://codecov.io/gh/reportportal/agent-Python-RobotFramework)

Listener for RobotFramework to report results to ReportPortal

* [Installation](https://github.com/reportportal/agent-Python-RobotFramework#installation)
* [Usage](https://github.com/reportportal/agent-Python-RobotFramework#usage)
* [Send attachement (screenshots)](https://github.com/reportportal/agent-Python-RobotFramework#send-attachement-screenshots)
* [Integration with GA](https://github.com/reportportal/agent-Python-RobotFramework#integration-with-ga)
* [Copyright Notice](https://github.com/reportportal/agent-Python-RobotFramework#copyright-notice)

## Installation

First you need to install RobotFramework:

    pip install robotframework

The latest stable version of library is available on PyPI:

    pip install robotframework-reportportal

[reportportal-client](https://github.com/reportportal/client-Python) and [six](https://pypi.org/project/six/) will be installed as dependencies

**IMPORTANT!**
The latest version **does not** support Report Portal versions below 5.0.0.

Specify the last one release of the client version 3 to install or update the client for other versions of Report Portal below 5.0.0:

```
pip install robotframework-reportportal~=3.0
```

## Contribution

All the fixes for the agent that supports Report Portal versions below 5.0.0 should go into the v3 branch.
The master branch will store the code base for the agent for Report Portal versions 5 and above.


## Usage

### Properties

For reporting results to ReportPortal you need to pass some variables to pybot run:

REQUIRED:
```
--listener robotframework_reportportal.listener
--variable RP_UUID:"your_user_uuid"
--variable RP_ENDPOINT:"your_reportportal_url"
--variable RP_LAUNCH:"launch_name"
--variable RP_PROJECT:"reportportal_project_name"
```
NOT REQUIRED:
```
--variable RP_LAUNCH_UUID:"id_of_existing_rp_launch"
    - ID of existing Report Portal launch
--variable RP_LAUNCH_DOC:"some_documentation_for_launch"
    - Description for the launch
--variable RP_LAUNCH_ATTRIBUTES:"RF tag_name:tag_value"
    - Space-separated list of tags/attributes for the launch
--variable RP_TEST_ATTRIBUTES:"key1:value1 key1:value2 tag key2:value3"
    - Space-separated list of tags/attributes for the tests
--variable RP_LOG_BATCH_SIZE:"10"
    - Default value is "20", affects size of async batch log requests
--variable RP_LOG_BATCH_PAYLOAD_SIZE:"10240000"
    - Default value is "65000000", maximum payload size of async batch log
      requests
--variable RP_RERUN:"True"
    - Default is "False". Enables rerun mode for the last launch.
--variable RP_RERUN_OF:"xxxxx-xxxx-xxxx-lauch-uuid"
    - Default is "None". Enables rerun mode for the launch with the specified
      UUID. Should be used in combination with the RP_RERUN option.
--variable RP_SKIPPED_ISSUE:"True"
    - Default value is "True", marks skipped test items with 'To Investigate'
--variable RP_ATTACH_LOG:"True"
    - Default value is "False", attaches Robot Framework HTML log file to
      the launch.
--variable RP_ATTACH_REPORT:"True"
    - Default value is "False", attaches Robot Framework HTML report file to
      the launch.
--variable RP_ATTACH_XUNIT:"True"
    - Default value is "False", attaches Robot Framework XUnit result file to
      the launch.
--variable RP_VERIFY_SSL:"True"
    - Default value is "True", disables SSL verification for HTTP requests.
      Also, you can specify a full path to your certificate as the value.
```

### Logging

Custom logger which supports attachments can be used in Python keywords.
Usage of this logger is similar to the standard robot.api.logger with addition
of an extra kwarg "attachment":

```python
import subprocess
from robotframework_reportportal import logger

def log_free_memory():
    logger.debug("Collecting free memory statistics!")
    logger.debug(
        "Memory consumption report",
        attachment={
            "name": "free_memory.txt",
            "data": subprocess.check_output("free -h".split()),
            "mime": "text/plain",
        },
    )
```

## Test case ID
It's possible to tag tests the following way `test_case_id:12345` using default Robot Framework tagging functionality. ID specified after `:` will be sent to ReportPortal.

## Send attachement (screenshots)

https://github.com/reportportal/client-Python#send-attachement-screenshots


## Integration with GA

ReportPortal is now supporting integrations with more than 15 test frameworks simultaneously. In order to define the most popular agents and plan the team workload accordingly, we are using Google analytics.

ReportPortal collects information about agent name and its version only. This information is sent to Google analytics on the launch start. Please help us to make our work effective.
If you still want to switch Off Google analytics, please change env variable the way below.

```bash
export AGENT_NO_ANALYTICS=1
```

## Copyright Notice
Licensed under the [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)
license (see the LICENSE.txt file).
