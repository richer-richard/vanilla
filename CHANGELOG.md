# Changelog

All notable changes to the VANILLA Collection will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CI/CD pipeline with GitHub Actions
- Pre-commit hooks configuration
- Development dependencies file (`requirements-dev.txt`)
- CHANGELOG.md for tracking version changes
- `py.typed` marker for PEP 561 compliance
- Structured logging throughout the application
- Rate limiting on legacy API endpoints
- Input validation on all API endpoints
- Configurable CORS policy
- Comprehensive test coverage for CLI and backend modules

### Changed
- Pinned exact dependency versions in `requirements.txt`
- Updated `pyproject.toml` with correct coverage source paths
- Improved error handling consistency across API endpoints
- Refactored server code to reduce duplication

### Fixed
- Security: Rate limiting now applied to all score submission endpoints
- Security: Input validation on legacy endpoints matches v1 API
- Accessibility improvements in frontend HTML

### Security
- Added rate limiting to prevent abuse
- Improved input sanitization
- Configurable CORS origins for production use

## [1.0.0] - 2024-01-01

### Added
- Initial release of VANILLA Collection
- 10 classic games: Snake, Pong, Breakout, Tetris, Minesweeper, Space Shooters, Geometry Dash, Flappy, Pac-Man, Asteroids
- Flask backend with REST API
- Leaderboard system with JSON persistence
- PWA support with service worker
- Procedural sound generation with Web Audio API
- Responsive design for desktop and mobile
- Multiple difficulty levels per game
- Local high score persistence

### Games
- **Snake** - Classic grid-based snake game
- **Pong** - Player vs AI paddle game
- **Breakout** - Brick-breaking arcade game
- **Tetris** - Block-stacking puzzle game
- **Minesweeper** - Logic puzzle game
- **Space Shooters** - Wave-based shooter
- **Geometry Dash** - Endless runner with obstacles
- **Flappy** - Tap-to-fly obstacle game
- **Pac-Man** - Maze navigation game
- **Asteroids** - Space shooter with physics

[Unreleased]: https://github.com/richer-richard/vanilla/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/richer-richard/vanilla/releases/tag/v1.0.0
