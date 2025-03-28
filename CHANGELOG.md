# Changelog

## [Unreleased]
### Added
- `RP_DEBUG_MODE` configuration variable, by @HardNorth

## [5.6.3]
### Removed
- Logging in the `listener.__post_log_message` method, to avoid logging the same message recursively, by @HardNorth

## [5.6.2]
### Fixed
- SETUP / TEARDOWN keyword removing, by @HardNorth

## [5.6.1]
### Added
- `RP_FLATTEN_KEYWORDS` configuration variable, by @HardNorth
- `--flatten-keywords` argument support, by @HardNorth

## [5.6.0]
### Changed
- Client version updated on [5.6.0](https://github.com/reportportal/client-Python/releases/tag/5.6.0), by @HardNorth
- Test end message now posts to the Test description, by @HardNorth
- Keywords names now contain Keyword types, by @HardNorth
### Added
- Support for `Python 3.13`, by @HardNorth
- `RP_REMOVE_KEYWORDS` configuration variable, by @HardNorth
- `--remove-keywords` argument support, by @HardNorth
### Removed
- `Python 3.7` support, by @HardNorth

## [5.5.8]
### Added
- Issue [#191](https://github.com/reportportal/agent-Python-RobotFramework/issues/191): Add seamless screenshot logging for Selenium and Browser libraries, by @HardNorth

## [5.5.7]
### Added
- `Test Case ID` reporting on Item Finish, by @HardNorth
### Changed
- Client version updated on [5.5.8](https://github.com/reportportal/client-Python/releases/tag/5.5.8), by @HardNorth

## [5.5.6]
### Added
- `timezone` command line argument for `post_report.py` script, by @HardNorth

## [5.5.5]
### Added
- Issue [#192](https://github.com/reportportal/agent-Python-RobotFramework/issues/192): Robot link markup to Markdown conversion, by @HardNorth

## [5.5.4]
### Fixed
- Issue [#187](https://github.com/reportportal/agent-Python-RobotFramework/issues/187): Distutils in the agent, by @HardNorth
### Added
- Python 12 support, by @HardNorth

## [5.5.3]
### Added
- Issue [#178](https://github.com/reportportal/agent-Python-RobotFramework/issues/178) Metadata attributes handling, by @HardNorth
### Changed
- Client version updated on [5.5.6](https://github.com/reportportal/client-Python/releases/tag/5.5.6), by @HardNorth
### Removed
- `model.pyi`, `static.pyi` stub files, as we don't really need them anymore, by @HardNorth

## [5.5.2]
### Added
- Binary data escaping in `listener` module (enhancing `Get Binary File` keyword logging), by @HardNorth
### Changed
- Client version updated on [5.5.5](https://github.com/reportportal/client-Python/releases/tag/5.5.5), by @HardNorth

## [5.5.1]
### Changed
- Unified ReportPortal product spelling, by @HardNorth
- Client version updated on [5.5.4](https://github.com/reportportal/client-Python/releases/tag/5.5.4), by @HardNorth
### Fixed
- Issue [#181](https://github.com/reportportal/agent-Python-RobotFramework/issues/181) `RP_LAUNCH_UUID` variable passing to new Client, by @HardNorth

## [5.5.0]
### Added
- `RP_CLIENT_TYPE` configuration variable, by @HardNorth
- `RP_CONNECT_TIMEOUT` and `RP_READ_TIMEOUT` configuration variables, by @HardNorth
### Changed
- Client version updated on [5.5.1](https://github.com/reportportal/client-Python/releases/tag/5.5.1), by @HardNorth
### Removed
- Dependency on `six`, by @HardNorth

## [5.4.0]
### Added
- `RP_LAUNCH_UUID_PRINT` and `RP_LAUNCH_UUID_PRINT_OUTPUT` configuration variables, by @HardNorth
### Changed
- Internal item list was replaced with LifoQueue, by @HardNorth
- Client version updated on [5.4.0](https://github.com/reportportal/client-Python/releases/tag/5.4.0), by @HardNorth
- `service.RobotService.init_service` method now accepts `variables.Variables` object as single argument instead of many of them, which were just copy-paste, by @HardNorth
### Removed
- Python 2.7, 3.6 support, by @HardNorth

## [5.3.3]
### Changed
- Client version updated on [5.3.5](https://github.com/reportportal/client-Python/releases/tag/5.3.5), by @HardNorth
- The Agent publish a warning and does not report anything in case of a missed required variable now,  by @HardNorth
- `RP_UUID` configuration parameter was renamed to `RP_API_KEY` to maintain common convention, by @HardNorth

## [5.3.2]
### Changed
- Client version updated on [5.3.0](https://github.com/reportportal/client-Python/releases/tag/5.3.0), by @HardNorth

## [5.3.1]
### Fixed
- Issue [#160](https://github.com/reportportal/agent-Python-RobotFramework/issues/160) `RP_LAUNCH_UUID` variable passing to the Client, by @HardNorth

## [5.3.0]
### Added
- `RP_LOG_BATCH_PAYLOAD_SIZE` parameter, by @HardNorth
### Changed
- Client version updated on [5.2.3](https://github.com/reportportal/client-Python/releases/tag/5.2.3), by @HardNorth
- The agent switched to use new client with async log processing, by @HardNorth

## [5.2.2]
### Fixed
- Issue [#140](https://github.com/reportportal/agent-Python-RobotFramework/issues/140) Process test message at the end of the test, by @iivanou
- Issue [#139](https://github.com/reportportal/agent-Python-RobotFramework/issues/139) Broken view in Before/After Suites items, by @HardNorth

## [5.2.1]
### Added
- Support of the rerun functionality;
- Allow attaching log and xunit result files to the launch;
- Add the ability to disable SSL verification.
### Fixed
- SKIP message handling.
