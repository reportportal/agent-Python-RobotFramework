from setuptools import setup, find_packages

setup(
    name='robotframework-reportportal',
    packages=find_packages(),
    version='2.5.0',
    description='Listener for RobotFramework reporting to ReportPortal',
    author='Artsiom Tkachou',
    author_email='artsiom_tkachou@epam.com',
    url='https://github.com/EPAMReportPortal/ReportPortal-RobotFramework-agent',    #ADD URL
    download_url='https://github.com/EPAMReportPortal/ReportPortal-RobotFramework-agent/tarball/2.5.0',
    keywords=['testing', 'reporting', 'robot framework', 'reportportal'],  # arbitrary keywords
    classifiers=[],
    install_requires=["reportportal-client"]
)
