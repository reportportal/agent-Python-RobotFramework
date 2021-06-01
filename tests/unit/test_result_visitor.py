"""
Copyright (c) 2021 http://reportportal.io .
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License
"""

import pytest


class TestResultVisitorTest:

    def test_parse_message_no_img_tag(self, visitor):
        with pytest.raises(AttributeError):
            visitor.parse_message('usual test comment without image')

    def test_parse_message_bad_img_tag(self, visitor):
        with pytest.raises(AttributeError):
            visitor.parse_message('<img src=\'bad.html.img>')

    def test_parse_message_contains_image(self, visitor):
        assert ['src="any.png"', 'any.png'] == visitor.parse_message(
            '<img alt="" src="any.png" />')

    def test_parse_message_contains_image_with_space(self, visitor):
        assert ['src="any%20image.png"', 'any image.png'] == \
               visitor.parse_message('<img alt="" src="any%20image.png" />')
