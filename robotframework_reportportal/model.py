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

"""This module contains models representing Robot Framework test items."""

import os


class Suite(object):
    """Class represents Robot Framework test suite."""

    def __init__(self, name, attributes):
        """Initialize required attributes.

        :param name:       Suite name
        :param attributes: Suite attributes passed through the listener
        """
        self.attributes = attributes
        self.doc = attributes['doc']
        self.end_time = attributes.get('endtime', '')
        self.longname = attributes['longname']
        self.message = attributes.get('message')
        self.metadata = attributes['metadata']
        self.name = name
        self.robot_id = attributes['id']
        self.rp_item_id = None
        self.rp_parent_item_id = None
        self.start_time = attributes.get('starttime')
        self.statistics = attributes.get('statistics')
        self.status = attributes.get('status')
        self.suites = attributes['suites']
        self.tests = attributes['tests']
        self.total_tests = attributes['totaltests']
        self.type = 'SUITE'

    @property
    def source(self):
        """Return the test case source file path."""
        if self.attributes.get('source') is not None:
            return os.path.relpath(self.attributes['source'], os.getcwd())

    def update(self, attributes):
        """Update suite attributes on suite finish.

        :param attributes: Suite attributes passed through the listener
        """
        self.end_time = attributes.get('endtime', '')
        self.message = attributes.get('message')
        self.status = attributes.get('status')
        self.statistics = attributes.get('statistics')
        return self


class Launch(Suite):
    """Class represents Robot Framework test suite."""

    def __init__(self, name, attributes):
        """Initialize required attributes.

        :param name:       Launch name
        :param attributes: Suite attributes passed through the listener
        """
        # noinspection PySuperArguments
        super(Launch, self).__init__(name, attributes)
        self.type = 'LAUNCH'


class Test(object):
    """Class represents Robot Framework test case."""

    def __init__(self, name, attributes):
        """Initialize required attributes.

        :param name:       Name of the test
        :param attributes: Test attributes passed through the listener
        """
        # for backward compatibility with Robot < 4.0 mark every test case
        # as critical if not set
        self._critical = attributes.get('critical', 'yes')
        self._tags = attributes['tags']
        self._attributes = attributes
        self.doc = attributes['doc']
        self.end_time = attributes.get('endtime', '')
        self.longname = attributes['longname']
        self.message = attributes.get('message')
        self.name = name
        self.robot_id = attributes['id']
        self.rp_item_id = None
        self.rp_parent_item_id = None
        self.start_time = attributes['starttime']
        self.status = attributes.get('status')
        self.template = attributes['template']
        self.type = 'TEST'

    @property
    def critical(self):
        """Form unique value for RF 4.0+ and older versions."""
        return self._critical in ('yes', True)

    @property
    def tags(self):
        """Get list of test tags excluding test_case_id."""
        return [
            tag for tag in self._tags if not tag.startswith('test_case_id')]

    @property
    def source(self):
        """Return the test case source file path."""
        if self._attributes['source'] is not None:
            return os.path.relpath(self._attributes['source'], os.getcwd())

    @property
    def code_ref(self):
        """Return the test case code reference.

        The result line should be exactly how it appears in '.robot' file.
        """
        line_number = self._attributes.get("lineno")
        if line_number is not None:
            return '{0}:{1}'.format(self.source, line_number)
        return '{0}:{1}'.format(self.source, self.name)

    @property
    def test_case_id(self):
        """Get test case ID through the tags."""
        # use test case id from tags if specified
        for tag in self._tags:
            if tag.startswith('test_case_id:'):
                return tag.split(':')[1]
        # generate it if not
        return '{0}:{1}'.format(self.source, self.name)

    def update(self, attributes):
        """Update test attributes on test finish.

        :param attributes: Suite attributes passed through the listener
        """
        self._tags = attributes.get('tags', self._tags)
        self.end_time = attributes.get('endtime', '')
        self.message = attributes.get('message')
        self.status = attributes.get('status')
        return self


class Keyword(object):
    """Class represents Robot Framework keyword."""

    def __init__(self, name, attributes, parent_type=None):
        """Initialize required attributes.

        :param name:        Name of the keyword
        :param attributes:  Keyword attributes passed through the listener
        :param parent_type: Type of the parent test item
        """
        self.attributes = attributes
        self.args = attributes['args']
        self.assign = attributes['assign']
        self.doc = attributes['doc']
        self.end_time = attributes.get('endtime')
        self.keyword_name = attributes['kwname']
        self.keyword_type = attributes['type']
        self.libname = attributes['libname']
        self.name = name
        self.rp_item_id = None
        self.rp_parent_item_id = None
        self.parent_type = parent_type
        self.start_time = attributes['starttime']
        self.status = attributes.get('status')
        self.tags = attributes['tags']
        self.type = 'KEYWORD'

    def get_name(self):
        """Get name of the keyword suitable for Report Portal."""
        assign = ', '.join(self.assign)
        assignment = '{0} = '.format(assign) if self.assign else ''
        arguments = ', '.join(self.args)
        full_name = f'{assignment}{self.name} ({arguments})'
        return full_name[:256]

    def get_type(self):
        """Get keyword type."""
        if self.keyword_type.lower() in ('setup', 'teardown'):
            if self.parent_type.lower() == 'keyword':
                return 'STEP'
            if self.keyword_type.lower() == 'setup':
                return 'BEFORE_{0}'.format(self.parent_type.upper())
            if self.keyword_type.lower() == 'teardown':
                return 'AFTER_{0}'.format(self.parent_type.upper())
        else:
            return 'STEP'

    def update(self, attributes):
        """Update keyword attributes on keyword finish.

        :param attributes: Suite attributes passed through the listener
        """
        self.end_time = attributes.get('endtime', '')
        self.status = attributes.get('status')
        return self


class LogMessage(str):
    """Class represents Robot Framework messages."""

    def __init__(self, message):
        """Initialize required attributes."""
        self.attachment = None
        self.item_id = None
        self.level = 'INFO'
        self.launch_log = False
        self.message = message

    def __repr__(self):
        """Return string representation of the object."""
        return self.message
