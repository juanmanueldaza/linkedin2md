# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-01-20

### Added
- Comprehensive test suite with 146 tests (was 58)
- CLI tests for argument parsing and error handling
- End-to-end tests with realistic LinkedIn export data
- Parser tests for all 12 parser modules
- Formatter tests for all 12 formatter modules
- Edge case tests (empty data, Unicode, special characters)
- Security E2E tests (path traversal, malicious content, CSV injection)

### Changed
- Test coverage significantly improved
- More robust handling of edge cases

## [0.1.3] - 2025-01-20

### Fixed
- Fixed all pyright type checking errors
- Updated type annotations to use `Any` for flexible data types in protocols

## [0.1.2] - 2025-01-20

### Changed
- Added `pipx` as recommended installation method
- Added note about "externally-managed-environment" on modern Linux systems

## [0.1.1] - 2025-01-20

### Changed
- Updated README with LLM use cases and example prompts
- Added documentation for compatible AI tools (NotebookLM, Claude, Obsidian, etc.)

## [0.1.0] - 2025-01-20

### Added
- Initial release
- Convert LinkedIn data exports (ZIP) to Markdown files
- Support for 40+ data categories:
  - Profile (name, title, contact, summary)
  - Experience and education
  - Skills and certifications
  - Recommendations and endorsements
  - LinkedIn Learning history
  - Connections and network
  - Posts, comments, and reactions
  - Job applications and saved jobs
  - Activity history (searches, logins)
  - Advertising and privacy data
- Bilingual support (English and Spanish)
- CLI with customizable output directory
- SOLID architecture for extensibility
- Security features (path traversal protection, URL sanitization, file size limits)

[Unreleased]: https://github.com/juanmanueldaza/linkedin2md/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/juanmanueldaza/linkedin2md/compare/v0.1.3...v0.2.0
[0.1.3]: https://github.com/juanmanueldaza/linkedin2md/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/juanmanueldaza/linkedin2md/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/juanmanueldaza/linkedin2md/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/juanmanueldaza/linkedin2md/releases/tag/v0.1.0
