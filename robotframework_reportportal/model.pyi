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

from six import text_type
from typing import Any, Dict, List, Optional, Text, Tuple, Union

class Suite:
    attributes: Union[List[Text], Dict[Text]] = ...
    doc: Text = ...
    end_time: Text = ...
    longname: Text = ...
    message: Text = ...
    metadata: Dict[Text, Text] = ...
    name: Text = ...
    robot_id: Text = ...
    rp_item_id: Optional[Text] = ...
    rp_parent_item_id: Optional[Text] = ...
    start_time: Optional[Text] = ...
    statistics: Text = ...
    status: Text = ...
    suites: List[Text] = ...
    tests: List[Text] = ...
    total_tests: int = ...
    type: Text = 'SUITE'
    def __init__(self, name: Text, attributes: Dict[Text, Any]) -> None: ...
    @property
    def source(self) -> Text: ...
    def update(self, attributes: Dict[Text, Any]) -> Union[Launch, Suite]: ...

class Launch(Suite):
    type: Text = 'LAUNCH'
    def __init__(self, name: Text, attributes: Dict[Text, Any]) -> None: ...

class Test:
    _critical: Text = ...
    _tags: List[Text] = ...
    _attributes: Dict[Text, Any] = ...
    attributes: List[Dict[Text, Text]] = ...
    doc: Text = ...
    end_time: Text = ...
    longname: Text = ...
    message: Text = ...
    name: Text = ...
    robot_id: Text = ...
    rp_item_id: Optional[Text] = ...
    rp_parent_item_id: Optional[Text] = ...
    start_time: Text = ...
    status: Text = ...
    template: Text = ...
    type: Text = 'TEST'
    def __init__(self, name: Text, attributes: Dict[Text, Any]) -> None: ...
    @property
    def critical(self) -> bool: ...
    @property
    def tags(self) -> List[Text]: ...
    @property
    def source(self) -> Text: ...
    @property
    def code_ref(self) -> Text: ...
    @property
    def test_case_id(self) -> Optional[Text]: ...
    def update(self, attributes: Dict[Text, Any]) -> Test: ...

class Keyword:
    attributes: Dict[Text, Any] = ...
    args: List[Text] = ...
    assign: List[Text] = ...
    doc: Text = ...
    end_time: Text = ...
    keyword_name: Text = ...
    keyword_type: Text = ...
    libname: Text = ...
    name: Text = ...
    rp_item_id: Optional[Text] = ...
    rp_parent_item_id: Optional[Text] = ...
    parent_type: Text = ...
    start_time: Text = ...
    status: Text = ...
    tags: List[Text] = ...
    type: Text = 'KEYWORD'
    def __init__(self, name: Text, attributes: Dict[Text, Any], parent_type: Optional[Text] = None) -> None: ...
    def get_name(self) -> Text: ...
    def get_type(self) -> Text: ...
    def update(self, attributes: Dict[Text, Any]) -> Keyword: ...

class LogMessage(text_type):
    attachment: Optional[Dict[Text, Text]] = ...
    launch_log: bool = ...
    item_id: Optional[Text] = ...
    level: Text = ...
    message: Text = ...
    def __init__(self, *args: Tuple, **kwargs: Dict) -> None: ...
