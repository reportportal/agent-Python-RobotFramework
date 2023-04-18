# Changelog

## [Unreleased]
### Changed
- Client version updated on [5.3.1](https://github.com/reportportal/client-Python/releases/tag/5.3.1), by @HardNorth

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
