"""This module contains model that stores Robot Framework variables.

Copyright (c) 2021 http://reportportal.io .
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from os import getenv
from distutils.util import strtobool

from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError

from .exception import RobotServiceException

# This is a storage for the result visitor
_variables = {}


def get_variable(name, default=None):
    """Get Robot Framework variable.

    :param name:    Name of the variable
    :param default: Default value
    :return:        The value of the variable, otherwise default value
    """
    try:
        return BuiltIn().get_variable_value("${" + name + "}", default=default)
    except RobotNotRunningError:
        return _variables.get(name, default)


class Variables(object):
    """This class stores Robot Framework variables related to Report Portal."""

    def __init__(self):
        """Initialize instance attributes."""
        self._endpoint = None
        self._launch_name = None
        self._pabot_pool_id = None
        self._pabot_used = None
        self._project = None
        self._uuid = None
        self.attach_report = strtobool(get_variable(
            'RP_ATTACH_REPORT', default='True'))
        self.launch_attributes = get_variable(
            'RP_LAUNCH_ATTRIBUTES', default='').split()
        self.launch_id = get_variable('RP_LAUNCH_UUID')
        self.launch_doc = get_variable('RP_LAUNCH_DOC')
        self.log_batch_size = int(get_variable(
            'RP_LOG_BATCH_SIZE', default='20'))
        self.mode = get_variable('RP_MODE')
        self.pool_size = int(get_variable('RP_MAX_POOL_SIZE', default='50'))
        self.skip_analytics = getenv('AGENT_NO_ANALYTICS')
        self.skipped_issue = strtobool(get_variable(
            'RP_SKIPPED_ISSUE', default='True'))
        self.test_attributes = get_variable(
            'RP_TEST_ATTRIBUTES', default='').split()

    @property
    def endpoint(self):
        """Get Report Portal API endpoint.

        :raises: RobotServiceException if it is None
        :return: Report Portal API endpoint
        """
        self._endpoint = self._endpoint or get_variable('RP_ENDPOINT')
        if self._endpoint is None:
            raise RobotServiceException(
                'Missing parameter RP_ENDPOINT for robot run\n'
                'You should pass -v RP_ENDPOINT:<endpoint_value>')
        return self._endpoint

    @property
    def launch_name(self):
        """Get Report Portal launch name.

        :raises: RobotServiceException if it is None
        :return: Report Portal launch name
        """
        self._launch_name = self._launch_name or get_variable('RP_LAUNCH')
        if self._launch_name is None:
            raise RobotServiceException(
                'Missing parameter RP_LAUNCH for robot run\n'
                'You should pass -v RP_LAUNCH:<launch_name_value>')
        return self._launch_name

    @property
    def pabot_pool_id(self):
        """Get pool id for the current Robot Framework executor.

        :return: Pool id for the current Robot Framework executor
        """
        if not self._pabot_pool_id:
            self._pabot_pool_id = get_variable(name='PABOTEXECUTIONPOOLID')
        return self._pabot_pool_id

    @property
    def pabot_used(self):
        """Get status of using pabot in test execution.

        :return: Cached value of the Pabotlib URI
        """
        if not self._pabot_used:
            self._pabot_used = get_variable(name='PABOTLIBURI')
        return self._pabot_used

    @property
    def project(self):
        """Get Report Portal project name.

        :raises: RobotServiceException if it is None
        :return: Report Portal project name
        """
        self._project = self._project or get_variable('RP_PROJECT')
        if self._project is None:
            raise RobotServiceException(
                'Missing parameter RP_PROJECT for robot run\n'
                'You should pass -v RP_PROJECT:<project_name_value>')
        return self._project

    @property
    def uuid(self):
        """Get Report Portal API token UUID.

        :raises: RobotServiceException if it is None
        :return: Report Portal token UUID
        """
        self._uuid = self._uuid or get_variable('RP_UUID')
        if self._uuid is None:
            raise RobotServiceException(
                'Missing parameter RP_UUID for robot run\n'
                'You should pass -v RP_UUID:<uuid_value>')
        return self._uuid
