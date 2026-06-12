# Changelog

## [Unreleased]

- Upgrade default Pyrefly version to 1.0.0 with official GitHub release binaries.
- Fix sandbox import resolution by mounting the PEX venv via `append_only_caches`.
- Inject Pants source roots as `--search-path` so users need not hard-code them in `pyproject.toml`.
- Fix a typo in the rule description: "Pyreflypecheck using Pyrefly" -> "Typecheck using Pyrefly"

## [0.0.1] - 2026-01-10

First release