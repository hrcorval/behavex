# Release Commands

Quick reference for releasing to PyPI.

## Build Packages

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build source distribution and wheel
python -m build
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
rm -rf build/ dist/ *.egg-info/ && python3 -m build && twine upload dist/*

# Build and deploy to TestPyPI
rm -rf build/ dist/ && python3 -m build && twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```
