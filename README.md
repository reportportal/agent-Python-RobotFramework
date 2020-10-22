# ReportPortal RobotFramework agent

[![Build Status](https://travis-ci.org/reportportal/agent-Python-RobotFramework.svg?branch=master)](https://travis-ci.org/reportportal/agent-Python-RobotFramework)
[![PyPI](https://img.shields.io/pypi/v/robotframework-reportportal.svg?maxAge=2592000)](https://pypi.python.org/pypi/robotframework-reportportal)

Listener for RobotFramework to report results to ReportPortal

* [Installation](https://github.com/reportportal/agent-Python-RobotFramework#installation)
* [Usage](https://github.com/reportportal/agent-Python-RobotFramework#usage)
* [Send attachement (screenshots)](https://github.com/reportportal/agent-Python-RobotFramework#send-attachement-screenshots)
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
--variable RP_TEST_ATTRIBUTES:"Long"
    - Space-separated list of tags/attributes for the tests
--variable RP_LOG_BATCH_SIZE:"10"
    - Default value is "20", affects size of async batch log requests
```

Custom logger which supports attachments can be used in Python keywords.
Usage of this logger is similar to the standard robot.api.logger with addition
of an extra kwarg "attachment":

```python
import subprocess
from robotframework_reportportal import logger

class MyLibrary(object):

    def log_free_memory(self):
        logger.debug("Collecting free memory statistics!")
        logger.debug(
            "Memory consumption report",
            attachment={
                "name": "free_memory.txt",
                "data": subprocess.check_output("free -h".split()),
                "mime": "application/octet-stream",
            },
        )
```

## Send attachement (screenshots)

https://github.com/reportportal/client-Python#send-attachement-screenshots


## Copyright Notice
Licensed under the [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)
license (see the LICENSE.txt file).
