# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.1] - 2025-01-14

### Changed
- Removed `test.html` and `updateMapping.py` from Git tracking to prevent language detection affecting repository statistics
- Added gzipped versions (`test.html.gz`, `updateMapping.py.gz`) to maintain file availability while excluding them from language analysis
- Updated `.gitignore` to exclude Python and HTML files from tracking

## [v1.0] - 2025-01-14

### Added
- `mapper.js` tool to convert OMIM URIs into Monarch Initiative's own URIs, and viceversa
- `updateMapping.py` script to update the correspondence map
- `data` folder with initial mappings updated to January 13th 2025