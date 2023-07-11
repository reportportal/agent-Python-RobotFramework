"""Setup instructions for the package."""

import os
from setuptools import setup


__version__ = '5.4.1'


def read_file(fname):
    """Read the given file.

    :param fname: Name of the file to be read
    :return:      Output of the given file
    """
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name='robotframework-reportportal',
    packages=['robotframework_reportportal'],
    package_data={'robotframework_reportportal': ['*.pyi']},
    version=__version__,
    description='Agent for reporting RobotFramework test results to '
                'Report Portal',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    author='Report Portal Team',
    author_email='support@reportportal.io',
    url='https://github.com/reportportal/agent-Python-RobotFramework',
    download_url=(
        'https://github.com/reportportal/agent-Python-RobotFramework/'
        'tarball/{version}'.format(version=__version__)),
    keywords=['testing', 'reporting', 'robot framework', 'reportportal',
              'agent'],
    classifiers=[
        'Framework :: Robot Framework',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        ],
    install_requires=read_file('requirements.txt').splitlines(),
    entry_points={
        'console_scripts': [
            'post_report=robotframework_reportportal.post_report:main'
        ]
    },
)
