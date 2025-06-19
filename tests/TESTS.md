# BehaveX Package Testing Commands

## Quick Test (Minimal Commands)

```bash
# 1. Uninstall and clean
pip uninstall behavex -y && rm -rf build/ dist/ *.egg-info/

# 2. Build and install package
python3 -m build && pip install dist/*.whl

# 3. Run tests
python3 -m behavex ./tests/features/*.feature
```
