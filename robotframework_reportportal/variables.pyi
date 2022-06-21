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

from typing import Dict, List, Optional, Text, Union

_variables: Dict

def get_variable(name: Text, default: Optional[Text] = ...) -> Optional[Text]: ...

class Variables:
    _endpoint: Optional[Text] = ...
    _launch_name: Optional[Text] = ...
    _pabot_pool_id: Optional[int] = ...
    _pabot_used: Optional[Text] = ...
    _project: Optional[Text] = ...
    _uuid: Optional[Text] = ...
    attach_log: bool = ...
    attach_report: bool = ...
    attach_xunit: bool = ...
    launch_attributes: List = ...
    launch_id: Optional[Text] = ...
    launch_doc: Optional[Text] = ...
    log_batch_size: Optional[int] = ...
    mode: Optional[Text] = ...
    pool_size: Optional[int] = ...
    rerun: bool = ...
    rerun_of: Optional[Text] = ...
    skip_analytics: Optional[Text] = ...
    test_attributes: Optional[List] = ...
    skipped_issue: bool = ...
    def __init__(self) -> None: ...
    @property
    def endpoint(self) -> Text: ...
    @property
    def launch_name(self) -> Text: ...
    @property
    def pabot_pool_id(self) -> int: ...
    @property
    def pabot_used(self) -> Optional[Text]: ...
    @property
    def project(self) -> Text: ...
    @property
    def uuid(self) -> Text: ...
    @property
    def verify_ssl(self) -> Union[bool, Text]: ...
