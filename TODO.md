# PyMdown Extensions TODO List

## High Priority - Foundation & Modernization

### Build System & Packaging
- [ ] Create `pyproject.toml` with modern setuptools configuration
- [ ] Migrate all metadata from `setup.py` to `pyproject.toml`
- [ ] Add `setuptools-scm` for automatic versioning
- [ ] Update `MANIFEST.in` for new structure
- [ ] Create `py.typed` marker file for type hints

### Python Version Support
- [ ] Update minimum Python version to 3.7 in all configuration files
- [ ] Remove Python 2.7 compatibility code
- [ ] Update classifiers in project metadata
- [ ] Test with Python 3.7-3.12

### CI/CD Migration
- [ ] Create `.github/workflows/tests.yml` for GitHub Actions
- [ ] Create `.github/workflows/release.yml` for automated PyPI releases
- [ ] Configure matrix testing for multiple Python versions and OS
- [ ] Remove `.travis.yml` and `appveyor.yml`
- [ ] Set up Dependabot for automated dependency updates

### Development Tooling
- [ ] Add `pre-commit` configuration file
- [ ] Configure Black for code formatting
- [ ] Configure isort for import sorting
- [ ] Configure Ruff to replace flake8
- [ ] Add mypy configuration for type checking
- [ ] Update `.gitignore` for new tools

## Medium Priority - Code Quality & Testing

### Type Hints
- [ ] Add type hints to `pymdownx/util.py`
- [ ] Add type hints to base extension classes
- [ ] Add type hints to all public APIs
- [ ] Configure mypy in `pyproject.toml`
- [ ] Add type checking to CI pipeline

### Testing Infrastructure
- [ ] Migrate from nose to pytest
- [ ] Reorganize test structure by extension
- [ ] Update test discovery configuration
- [ ] Add pytest-cov for coverage reports
- [ ] Create integration test suite
- [ ] Add performance benchmark tests

### Code Modernization
- [ ] Convert string formatting to f-strings
- [ ] Use pathlib for file operations
- [ ] Apply Black formatting to all Python files
- [ ] Run isort on all Python files
- [ ] Fix any Ruff/mypy warnings

### Documentation
- [ ] Update MkDocs to latest version
- [ ] Switch to MkDocs Material theme
- [ ] Add mkdocstrings for API documentation
- [ ] Update all documentation for Python 3.7+ syntax
- [ ] Create comprehensive migration guide for v4.0
- [ ] Add quickstart guide
- [ ] Update installation instructions

## Low Priority - Features & Enhancements

### Performance Optimization
- [ ] Profile emoji database loading
- [ ] Implement lazy loading for large databases
- [ ] Add caching where beneficial
- [ ] Optimize regex patterns in hot paths

### New Features
- [ ] Research Mermaid diagram support implementation
- [ ] Design KaTeX support for Arithmatex
- [ ] Plan custom emoji set support
- [ ] Investigate Rust extensions for performance

### Security
- [ ] Add Bandit security scanning
- [ ] Configure Safety for dependency checking
- [ ] Review HTML output for XSS vulnerabilities
- [ ] Add security policy documentation

### Developer Experience
- [ ] Create VS Code devcontainer configuration
- [ ] Add GitHub issue templates
- [ ] Add pull request template
- [ ] Update CONTRIBUTING.md
- [ ] Create example projects repository

## Release Planning

### Version 3.6.0 (Deprecation Release)
- [ ] Add deprecation warnings for Python 2.7
- [ ] Add deprecation warnings for removed features
- [ ] Update changelog
- [ ] Release to PyPI

### Version 4.0.0-alpha
- [ ] Complete all high priority tasks
- [ ] Run full test suite
- [ ] Update version number
- [ ] Create alpha release
- [ ] Announce to community for testing

### Version 4.0.0 (Final)
- [ ] Address feedback from alpha/beta testing
- [ ] Complete all medium priority tasks
- [ ] Final documentation review
- [ ] Create release announcement
- [ ] Release to PyPI

## Continuous Improvements
- [ ] Monitor GitHub issues for bug reports
- [ ] Review and merge community pull requests
- [ ] Keep dependencies up to date
- [ ] Maintain changelog
- [ ] Regular security audits

---

*Note: Tasks should be completed in order of priority. High priority tasks lay the foundation for modernization. Check off tasks as they are completed.*