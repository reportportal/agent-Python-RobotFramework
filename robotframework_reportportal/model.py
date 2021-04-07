"""This module contains models representing Robot Framework test items.

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

from reportportal_client.service import _convert_string


class Suite(object):
    """Class represents Robot Framework test suite."""

    def __init__(self, attributes):
        """Initialize required attributes.

        :param attributes: Suite attributes passed through the listener
        """
        self.attributes = attributes
        self.doc = attributes['doc']
        self.longname = attributes['longname']
        self.message = attributes.get('message')
        self.metadata = attributes['metadata']
        self.robot_id = attributes['id']
        self.source = attributes['source']
        self.statistics = attributes.get('statistics')
        self.status = attributes.get('status')
        self.suites = attributes['suites']
        self.tests = attributes['tests']
        self.total_tests = attributes['totaltests']


class Test(object):
    """Class represents Robot Framework test case."""

    def __init__(self, name=None, attributes=None):
        """Initialize required attributes.

        :param name:       Name of the test
        :param attributes: Test attributes passed through the listener
        """
        # for backward compatibility with Robot < 4.0 mark every test case
        # as critical if not set
        self.critical = attributes.get('critical', 'yes') == 'yes'
        self.doc = attributes['doc']
        self.longname = attributes['longname']
        self.message = attributes.get('message')
        self.name = name
        self.robot_id = attributes['id']
        self.status = attributes.get('status')
        self.tags = attributes['tags']
        self.template = attributes['template']


class Keyword(object):
    """Class represents Robot Framework keyword."""

    def __init__(self, name=None, parent_type="TEST", attributes=None):
        """Initialize required attributes.

        :param name:        Name of the keyword
        :param parent_type: Type of the parent test item
        :param attributes:  Keyword attributes passed through the listener
        """
        self.args = attributes['args']
        self.assign = attributes['assign']
        self.doc = attributes['doc']
        self.keyword_name = attributes['kwname']
        self.keyword_type = attributes['type']
        self.libname = attributes['libname']
        self.name = name
        self.parent_type = parent_type
        self.status = attributes.get('status')
        self.tags = attributes['tags']

    def get_name(self):
        """Get name of the keyword suitable for Report Portal."""
        assign = _convert_string(', '.join(self.assign))
        assignment = '{0} = '.format(assign) if self.assign else ''
        arguments = ', '.join(self.args)
        full_name = '{0}{1} ({2})'.format(
            assignment,
            _convert_string(self.name),
            _convert_string(arguments)
        )
        return full_name[:256]

    def get_type(self):
        """Get keyword type."""
        if self.keyword_type == 'Setup':
            return 'BEFORE_{0}'.format(self.parent_type)
        elif self.keyword_type == 'Teardown':
            return 'AFTER_{0}'.format(self.parent_type)
        else:
            return 'STEP'


class LogMessage:
    """Class represents Robot Framework messages."""

    def __init__(self, message):
        """Initialize required attributes."""
        self.attachment = None
        self.item_id = None
        self.level = 'INFO'
        self.message = message

    def __repr__(self):
        """Return string representation of the object."""
        return self.message
