from setuptools import setup, find_packages

requirements = [
    "reportportal-client>=3.0.0"
]

setup(
    name='robotframework-reportportal',
    packages=find_packages(),
    version='3.0.0',
    description='Listener for RobotFramework reporting to ReportPortal',
    author='Artsiom Tkachou',
    author_email='artsiom_tkachou@epam.com',
    url='https://github.com/reportportal/agent-Python-RobotFramework',
    download_url='https://github.com/reportportal/agent-Python-RobotFramework/tarball/3.0.0',
    keywords=['testing', 'reporting', 'robot framework', 'reportportal'],
    classifiers=[],
    install_requires=requirements
)
