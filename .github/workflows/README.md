# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automating testing and deployment of the Dirac Hashes package.

## Workflows

### Test (`test.yml`)

This workflow runs automated tests on the codebase whenever changes are pushed to the main branch or a pull request is opened against the main branch.

- **Triggers**: Push to `main`, Pull request to `main`
- **Actions**:
  - Sets up multiple Python versions (3.8, 3.9, 3.10, 3.11)
  - Installs dependencies
  - Runs the verification script to check basic functionality
  - Runs the test suite using pytest

### Publish (`publish.yml`)

This workflow builds and publishes the package to PyPI whenever a new release is created on GitHub.

- **Triggers**: New release created
- **Actions**:
  - Sets up Python 3.10
  - Installs dependencies
  - Verifies the package
  - Builds the package
  - Checks the package with twine
  - Publishes to PyPI

### Version (`version.yml`)

This workflow automatically updates the version number in the package when a new tag is pushed.

- **Triggers**: Push of a tag starting with 'v' (e.g., v0.1.1)
- **Actions**:
  - Extracts the version number from the tag
  - Updates the version in setup.py
  - Updates or adds the __version__ attribute in src/quantum_hash/__init__.py
  - Commits and pushes the changes

## Setting Up

To use these workflows, you need to:

1. For the publish workflow, create a PyPI API token and add it as a secret named `PYPI_API_TOKEN` in your GitHub repository settings.

2. For the version workflow, ensure write permissions are enabled for GitHub Actions in your repository settings.

## Usage

### Publishing a New Release

1. Create and push a new tag with the format `vX.Y.Z` (e.g., `v0.1.1`):
   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```

2. The version workflow will automatically update the version numbers in the code.

3. Create a new release on GitHub using the tag.

4. The publish workflow will automatically build and publish the package to PyPI. 