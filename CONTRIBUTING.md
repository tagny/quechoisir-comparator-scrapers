# Contributing to quechoisir-comparator-scrapers

Thank you for your interest in contributing to quechoisir-comparator-scrapers! This project welcomes contributions from everyone. By participating in this project, you agree to abide by our Code of Conduct.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request, please open an issue on the GitHub repository. When reporting issues, include:

- A clear description of the problem
- Steps to reproduce the issue
- Expected behavior
- Environment details (Python version, OS, etc.)

Please follow available templates:
- [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md)
- [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md)
- [Custom Request Template](.github/ISSUE_TEMPLATE/custom.md)

### Pull Requests

We welcome pull requests that improve the project. Before submitting a pull request, please:

1. Open an issue to describe the changes you want to make
2. Fork the repository
3. Create a new branch for your changes
4. Make your changes
5. Run tests to ensure no existing functionality is broken
6. Add new tests if applicable
7. Run pre-commit hooks to ensure code quality
8. bump the version as stated in the version management section
9. Update documentation as needed
10. Commit your changes
11. Push your changes to your fork
12. Open a pull request

### Code Style

This project uses several tools to maintain code quality:

- **built-in hooks**: Code quality tool
  - trailing-whitespace
  - end-of-file-fixer
  - check-yaml
  - check-added-large-files
- **Black**: Code formatting
- **Flake8**: Linting
- **isort**: Import sorting
- **ruff**: Linting and fixing
- **detect-secrets**: Secret detection

Install pre-commit hooks to automatically check your changes:
```bash
pre-commit install
```

### Testing

Run tests with pytest:
```bash
pytest
```

### CI/CD

The project uses GitHub Actions for continuous integration and deployment:
- CI workflow runs tests and code quality checks on push and pull request (see .github/workflows/ci.yml)
- CD workflow generate docker image and push to Google Container Registry on push to main (see .github/workflows/cd.yml)

### Version Management

This project follows [Semantic Versioning](https://semver.org/) (SemVer) principles. Version numbers are managed in the `VERSION` and `.bumpversion.toml` files.

To update the version:

1. **For minor releases** (backwards compatible changes):
   ```bash
   # Using bump-my-version
   bump-my-version bump patch  # for bug fixes
   bump-my-version bump minor  # improvements of current tools (e.g. complexity)
   ```

2. **For major releases** (breaking changes):
   ```bash
   bump-my-version bump major  # for new features (new tools) and breaking changes
   ```

3. **Manual version update**:
   - Edit `pyproject.toml` and update the version field under `[project]`
   - Update `CHANGELOG.md` with the new version and release notes

4. **Verify version**:
   ```bash
   python -c "import importlib.metadata; print(importlib.metadata.version('tagny-mcp-server'))"
   ```

5. **Commit and tag the release**:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Bump version to X.X.X"
   git tag -a vX.X.X -m "Release version X.X.X"
   ```

6. The publish workflow will automatically publish to PyPI

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Pull Request Template

See the [PR template](.github/pull_request_template.md)

### Testing GitHub Actions Locally

TODO: this still need to be fixed

You can use the `act` tool to run GitHub Actions workflows locally. Follow these steps to set it up and use it:

1. **Install `act`:**

See https://nektosact.com/installation/index.html for installation instructions.

   ```bash
   curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash # On Ubuntu/Debian
   ```

2. **Configure `act`:**

   Create a `.actrc` file in your project root to configure the tool:

   ```ini
   -P airflow-latest=apache/airflow:3.1.4rc1-python3.13
   ```

3. **Run GitHub Actions Locally:**

   Use the following command to run all workflows or a specific workflow:

   ```bash
   act  # Run all workflows
   act -W .github/workflows/ci.yml  # Run a specific workflow
   ```

This will allow you to test your GitHub Actions locally before pushing changes.
