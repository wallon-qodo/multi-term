# Publishing to PyPI

This guide covers how to publish `claude-multi-terminal` to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts on both:
   - [PyPI](https://pypi.org/account/register/) (production)
   - [TestPyPI](https://test.pypi.org/account/register/) (testing)

2. **API Tokens**: Generate API tokens for both:
   - PyPI: https://pypi.org/manage/account/token/
   - TestPyPI: https://test.pypi.org/manage/account/token/

3. **Configure credentials** (`~/.pypirc`):
```ini
[pypi]
username = __token__
password = pypi-AgE... # Your PyPI token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgE... # Your TestPyPI token
```

4. **Install tools**:
```bash
cd ~/claude-multi-terminal
source venv/bin/activate
pip install build twine
```

## Publishing Steps

### 1. Update Version

Edit `pyproject.toml`:
```toml
[project]
version = "0.1.1"  # Increment version
```

### 2. Update Changelog

Create/update `CHANGELOG.md` with release notes.

### 3. Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info
```

### 4. Build Distribution

```bash
python -m build
```

This creates:
- `dist/claude_multi_terminal-0.1.1.tar.gz` (source distribution)
- `dist/claude_multi_terminal-0.1.1-py3-none-any.whl` (wheel)

### 5. Test on TestPyPI (Optional but Recommended)

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ claude-multi-terminal
```

### 6. Upload to PyPI

```bash
twine upload dist/*
```

### 7. Verify Installation

```bash
pip install --upgrade claude-multi-terminal
multi-term --version
```

### 8. Create Git Tag

```bash
git tag v0.1.1
git push origin v0.1.1
```

### 9. Create GitHub Release

1. Go to https://github.com/wallon-qodo/multi-term/releases
2. Click "Draft a new release"
3. Select tag `v0.1.1`
4. Title: "v0.1.1 - [Brief Description]"
5. Copy changelog content
6. Publish release

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- `0.1.0` → `0.1.1`: Bug fixes, minor changes
- `0.1.0` → `0.2.0`: New features, backwards compatible
- `0.1.0` → `1.0.0`: Major release, breaking changes

## Checklist

Before publishing:

- [ ] All tests passing
- [ ] Version number updated in `pyproject.toml`
- [ ] CHANGELOG.md updated
- [ ] README.md accurate
- [ ] Documentation up to date
- [ ] No sensitive data in code
- [ ] Build succeeds locally
- [ ] Tested on TestPyPI
- [ ] Git tag created
- [ ] GitHub release created

## Troubleshooting

**"File already exists" error:**
- You cannot re-upload the same version
- Increment version number and rebuild

**"Invalid credentials" error:**
- Check `~/.pypirc` configuration
- Verify API token is correct
- Ensure token has "Upload packages" scope

**Import errors after install:**
- Check `pyproject.toml` dependencies
- Verify package structure with `tar -tzf dist/*.tar.gz`
- Test in fresh virtual environment

**Missing files in package:**
- Update `MANIFEST.in` to include files
- Rebuild and verify with `tar -tzf dist/*.tar.gz`

## Automation (Future)

Create `.github/workflows/publish.yml` for automatic PyPI publishing on release:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install build twine
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

## Resources

- [PyPI Documentation](https://pypi.org/help/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Semantic Versioning](https://semver.org/)

---

**Note**: This is a living document. Update as the publishing process evolves.
