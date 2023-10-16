# Changelog

## [Unreleased]
### Added
- `RP_CLIENT_TYPE` configuration variable, by @HardNorth
- `RP_CONNECT_TIMEOUT` and `RP_READ_TIMEOUT` configuration variables, by @HardNorth
### Changed
- Client version updated on [5.5.0](https://github.com/reportportal/client-Python/releases/tag/5.5.0), by @HardNorth
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
