#  Copyright (c) 2023 EPAM Systems
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
#  limitations under the License

"""This module contains model that stores Robot Framework variables."""

from os import path
from typing import Optional, Union, Dict, Tuple, Any, List
from warnings import warn

from reportportal_client import OutputType, ClientType
from reportportal_client.helpers import to_bool
from reportportal_client.logs import MAX_LOG_BATCH_PAYLOAD_SIZE
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError

# This is a storage for the result visitor
_variables: Dict[str, Any] = {}


def get_variable(name: str, default: Optional[str] = None) -> Optional[str]:
    """Get Robot Framework variable.

    :param name:    Name of the variable
    :param default: Default value
    :return:        The value of the variable, otherwise default value
    """
    try:
        return BuiltIn().get_variable_value("${" + name + "}", default=default)
    except RobotNotRunningError:
        return _variables.get(name, default)


class Variables:
    """This class stores Robot Framework variables related to ReportPortal."""

    enabled: bool
    endpoint: Optional[str]
    launch_name: Optional[str]
    _pabot_pool_id: Optional[int]
    _pabot_used: Optional[str]
    project: Optional[str]
    api_key: Optional[str]
    attach_log: bool
    attach_report: bool
    attach_xunit: bool
    launch_attributes: List[str]
    launch_id: Optional[str]
    launch_doc: Optional[str]
    log_batch_size: Optional[int]
    mode: Optional[str]
    pool_size: Optional[int]
    rerun: bool
    rerun_of: Optional[str]
    test_attributes: List[str]
    skipped_issue: bool
    log_batch_payload_size: int
    launch_uuid_print: bool
    launch_uuid_print_output: Optional[OutputType]
    client_type: ClientType
    http_timeout: Optional[Union[Tuple[float, float], float]]

    def __init__(self) -> None:
        """Initialize instance attributes."""
        self.endpoint = get_variable('RP_ENDPOINT')
        self.launch_name = get_variable('RP_LAUNCH')
        self.project = get_variable('RP_PROJECT')

        self._pabot_pool_id = None
        self._pabot_used = None
        self.attach_log = to_bool(get_variable('RP_ATTACH_LOG', default='False'))
        self.attach_report = to_bool(get_variable('RP_ATTACH_REPORT', default='False'))
        self.attach_xunit = to_bool(get_variable('RP_ATTACH_XUNIT', default='False'))
        self.launch_attributes = get_variable('RP_LAUNCH_ATTRIBUTES', default='').split()
        self.launch_id = get_variable('RP_LAUNCH_UUID')
        self.launch_doc = get_variable('RP_LAUNCH_DOC')
        self.log_batch_size = int(get_variable(
            'RP_LOG_BATCH_SIZE', default='20'))
        self.mode = get_variable('RP_MODE')
        self.pool_size = int(get_variable('RP_MAX_POOL_SIZE', default='50'))
        self.rerun = to_bool(get_variable('RP_RERUN', default='False'))
        self.rerun_of = get_variable('RP_RERUN_OF', default=None)
        self.skipped_issue = to_bool(get_variable('RP_SKIPPED_ISSUE', default='True'))
        self.test_attributes = get_variable('RP_TEST_ATTRIBUTES', default='').split()
        self.log_batch_payload_size = int(get_variable('RP_LOG_BATCH_PAYLOAD_SIZE',
                                                       default=str(MAX_LOG_BATCH_PAYLOAD_SIZE)))
        self.launch_uuid_print = to_bool(get_variable('RP_LAUNCH_UUID_PRINT', default='False'))
        output_type = get_variable('RP_LAUNCH_UUID_PRINT_OUTPUT')
        self.launch_uuid_print_output = OutputType[output_type.upper()] if output_type else None
        client_type = get_variable('RP_CLIENT_TYPE')
        self.client_type = ClientType[client_type.upper()] if client_type else ClientType.SYNC
        connect_timeout = get_variable('RP_CONNECT_TIMEOUT')
        connect_timeout = float(connect_timeout) if connect_timeout else None

        read_timeout = get_variable('RP_READ_TIMEOUT')
        read_timeout = float(read_timeout) if read_timeout else None

        if connect_timeout is None and read_timeout is None:
            self.http_timeout = None
        elif connect_timeout is not None and read_timeout is not None:
            self.http_timeout = (connect_timeout, read_timeout)
        else:
            self.http_timeout = connect_timeout or read_timeout

        self.api_key = get_variable('RP_API_KEY')
        if not self.api_key:
            token = get_variable('RP_UUID')
            if token:
                warn(
                    message="Argument `RP_UUID` is deprecated since version 5.3.3 and will be subject for "
                            "removing in the next major version. Use `RP_API_KEY` argument instead.",
                    category=DeprecationWarning,
                    stacklevel=2
                )
                self.api_key = token
            else:
                warn(
                    message="Argument `RP_API_KEY` is `None` or empty string, that's not supposed to happen "
                            "because ReportPortal is usually requires an authorization key. Please check your"
                            " configuration.",
                    category=RuntimeWarning,
                    stacklevel=2
                )

        cond = (self.endpoint, self.launch_name, self.project, self.api_key)
        self.enabled = all(cond)
        if not self.enabled:
            warn(
                'One or required parameter is missing, ReportPortal listener will be disabled. '
                'Please check agent documentation.',
                RuntimeWarning,
                2
            )

    @property
    def pabot_pool_id(self) -> int:
        """Get pool id for the current Robot Framework executor.

        :return: Pool id for the current Robot Framework executor
        """
        if not self._pabot_pool_id:
            self._pabot_pool_id = get_variable(name='PABOTEXECUTIONPOOLID')
        return self._pabot_pool_id

    @property
    def pabot_used(self) -> Optional[str]:
        """Get status of using pabot in test execution.

        :return: Cached value of the Pabotlib URI
        """
        if not self._pabot_used:
            self._pabot_used = get_variable(name='PABOTLIBURI')
        return self._pabot_used

    @property
    def verify_ssl(self) -> Union[bool, str]:
        """Get value of the verify_ssl parameter for the client."""
        verify_ssl = get_variable('RP_VERIFY_SSL', default='True')
        if path.exists(verify_ssl):
            return verify_ssl
        return to_bool(verify_ssl)
