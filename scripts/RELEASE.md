# Release Commands

Quick reference for releasing to PyPI.

## Build Packages

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build source distribution and wheel
python setup.py sdist bdist_wheel
```

## Deploy to PyPI

```bash
# Deploy to PyPI
twine upload dist/*

# Deploy to TestPyPI
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

## One-liners

```bash
# Build and deploy to PyPI
rm -rf build/ dist/ *.egg-info/ && python3 setup.py sdist bdist_wheel && twine upload dist/*

# Build and deploy to TestPyPI
rm -rf build/ dist/ *.egg-info/ && python setup.py sdist bdist_wheel && twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```
