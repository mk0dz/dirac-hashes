# Publishing to PyPI

This guide explains how to publish the Dirac Hashes package to PyPI.

## Prerequisites

1. Make sure you have the latest versions of the required tools:

```bash
pip install --upgrade pip setuptools wheel twine
```

2. Create an account on [PyPI](https://pypi.org/) if you don't have one.

## Building the Package

1. Update the version number in:
   - `setup.py`
   - `src/quantum_hash/__init__.py`

2. Clean any previous builds:

```bash
rm -rf build/ dist/ src/*.egg-info/
```

3. Build the package:

```bash
python setup.py sdist bdist_wheel
```

This creates two files in the `dist/` directory:
- A source archive (`.tar.gz`)
- A built distribution (`.whl`)

## Testing with TestPyPI (Recommended)

Before uploading to the main PyPI index, it's a good idea to test with TestPyPI:

1. Upload to TestPyPI:

```bash
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

2. Install from TestPyPI in a new virtual environment:

```bash
# Create and activate a test environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install the package
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ dirac-hashes
```

3. Test the package:

```bash
# Try importing and using the package
python -c "from quantum_hash.dirac import DiracHash; print(DiracHash.hash('test').hex())"
```

## Publishing to PyPI

Once you've tested the package and everything works correctly:

1. Upload to PyPI:

```bash
twine upload dist/*
```

2. Verify the package is available:
   - Visit https://pypi.org/project/dirac-hashes/
   - Install in a new environment: `pip install dirac-hashes`

## After Publishing

1. Create a Git tag for the version:

```bash
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```

2. Update the changelog and documentation to reflect the new release.

## Troubleshooting

- If you encounter error messages during upload, read them carefully. Common issues include:
  - Missing required metadata
  - Version already exists on PyPI
  - Authentication issues

- If you need to remove a version from TestPyPI, you can do so through their web interface, but this is not possible on the main PyPI once a version is published. 