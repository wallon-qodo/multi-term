# Changelog

All notable changes to Claude Multi-Terminal will be documented in this file.

## [Unreleased]

### Added
- **Full-text search across all sessions** (Task #12)
  - Global search activated with `Ctrl+F` or `/search` command
  - Real-time search as you type
  - Highlight matches in yellow/amber (theme-matched colors)
  - Search panel with match count per session
  - Next/Previous navigation with `Enter`/`Shift+Enter` or `F3`/`Shift+F3`
  - Jump to match with auto-scroll and context
  - Case-insensitive search by default
  - Performance optimized for large histories (< 500ms for 10k lines)
  - Clear highlights on search close
  - Visual feedback with two-tier highlighting (regular + current match)

- **Session transcript export** (Task #10)
  - Export to Markdown or JSON format
  - `/export` command with format specification
  - Right-click context menu integration
  - Preserves conversation structure and timestamps

- **Slash command autocomplete**
  - Smart suggestions for all `/` commands
  - Arrow key navigation in dropdown
  - Tab/Enter to complete
  - Descriptions for each command

### Changed
- Enhanced SelectableRichLog with search highlighting support
- Updated keyboard shortcuts documentation
- Improved README with new features

### Fixed
- Multi-line string syntax errors in session cancellation
- Import organization in app.py

## [0.1.0] - Initial Release

### Added
- Split-pane layout for multiple Claude sessions
- Session persistence (save/load)
- Session naming and management
- Command broadcasting
- Copy/paste functionality
- Basic keyboard navigation
- PTY-based Claude CLI integration
- Rich text formatting with ANSI support
- Real-time output streaming
- Processing indicators with metrics
