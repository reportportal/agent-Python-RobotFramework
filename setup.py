import os
from setuptools import setup, find_packages


__version__ = '5.0.4'


def read_file(fname):
    """Read the given file.
    
    :param fname: Name of the file to be read
    :return:      Output of the given file
    """
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name='robotframework-reportportal',
    packages=find_packages(),
    version=__version__,
    description='Agent for reporting RobotFramework test results to Report Portal',
    author_email='SupportEPMC-TSTReportPortal@epam.com',
    url='https://github.com/reportportal/agent-Python-RobotFramework',
    download_url=(
        'https://github.com/reportportal/agent-Python-RobotFramework/'
        'tarball/{version}'.format(version=__version__)),
    keywords=['testing', 'reporting', 'robot framework', 'reportportal'],
    classifiers=[
        'Framework :: Robot Framework',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
        ],
    install_requires=read_file('requirements.txt').splitlines(),
    entry_points={
        'console_scripts': [
            'post_report=robotframework_reportportal.post_report:main'
        ]
    }
)
