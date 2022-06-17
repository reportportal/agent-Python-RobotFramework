"""This module contains common Pytest fixtures and hooks for unit tests.

Copyright (c) 2021 https://reportportal.io .
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License
"""
import sys

KEYWORDS_EXPECTED_TEST_NAMES = ['Invalid Password']
KEYWORDS_EXPECTED_CODE_REF_SUFFIXES = ['6'] * 6

SETTINGS_EXPECTED_TEST_NAMES = ['Invalid User Name', 'Invalid Password',
                                'Invalid User Name and Password',
                                'Empty User Name',
                                'Empty Password',
                                'Empty User Name and Password']
SETTINGS_EXPECTED_CODE_REF_SUFFIXES = [str(x) for x in range(7, 14)]

DATADRIVER_EXPECTED_TEST_NAMES = \
    ['Login with user \'invalid\' and password \'Password\'',
     'Login with user \'User\' and password \'invalid\'',
     'Login with user \'invalid\' and password \'invalid\'',
     'Login with user \'\' and password \'Password\'',
     'Login with user \'User\' and password \'\'',
     'Login with user \'\' and password \'\'']
DATADRIVER_EXPECTED_CODE_REF_SUFFIXES = ['8'] * 6


def pytest_generate_tests(metafunc):
    if metafunc.function.__name__ == 'test_code_reference_template':
        func_options = 'test,test_names,code_ref_suffixes'
        option_args = [
            ('examples/templates/keyword.robot', KEYWORDS_EXPECTED_TEST_NAMES,
             KEYWORDS_EXPECTED_CODE_REF_SUFFIXES),
            ('examples/templates/settings.robot', SETTINGS_EXPECTED_TEST_NAMES,
             SETTINGS_EXPECTED_CODE_REF_SUFFIXES)]
        if sys.version_info >= (3, 6):
            option_args.append(('examples/templates/datadriver.robot',
                                DATADRIVER_EXPECTED_TEST_NAMES,
                                DATADRIVER_EXPECTED_CODE_REF_SUFFIXES))
        metafunc.parametrize(func_options, option_args)
