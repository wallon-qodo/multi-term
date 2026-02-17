# Test Suite Documentation

## Phase 0 Comprehensive Tests

### Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Run comprehensive Phase 0 tests
python tests/test_phase0_comprehensive.py
```

### Test Coverage

The Phase 0 test suite (`test_phase0_comprehensive.py`) provides comprehensive coverage of:

#### 1. Import Tests (8 tests)
- Verifies all core packages import correctly
- Tests class instantiation
- Ensures no circular dependencies

#### 2. Config Tests (4 tests)
- Claude CLI path detection
- Storage directory management
- Configuration validation
- Constants accessibility

#### 3. Core Module Tests (5 tests)
- **SessionManager**: Create, list, terminate sessions
- **ClipboardManager**: System clipboard operations
- **TranscriptExporter**: Export to text files

#### 4. Persistence Tests (5 tests)
- **SessionState**: Session data structures
- **WorkspaceState**: Workspace data structures
- **SessionStorage**: Save/load state, history management

#### 5. App Launch Tests (2 tests)
- Main application import
- Required methods verification

### Test Results

**Latest Run:** February 17, 2026

```
Total tests: 24
Passed: 24 (100%)
Failed: 0
Errors: 0
Skipped: 0
Time: 0.033s
```

✅ **ALL TESTS PASSED**

### Test Structure

Each test suite follows this pattern:

```python
class TestSuiteN_Category(unittest.TestCase):
    """Test Suite N: Description"""

    def setUp(self):
        """Initialize test environment"""
        # Set up test fixtures
        pass

    def tearDown(self):
        """Clean up after tests"""
        # Clean up resources
        pass

    def test_NNN_specific_test(self):
        """Test description"""
        # Test implementation
        pass
```

### Running Specific Test Suites

```bash
# Run only import tests
python -m unittest tests.test_phase0_comprehensive.TestSuite1_Imports

# Run only config tests
python -m unittest tests.test_phase0_comprehensive.TestSuite2_Config

# Run only core module tests
python -m unittest tests.test_phase0_comprehensive.TestSuite3_CoreModules

# Run only persistence tests
python -m unittest tests.test_phase0_comprehensive.TestSuite4_Persistence

# Run only app launch tests
python -m unittest tests.test_phase0_comprehensive.TestSuite5_AppLaunch
```

### Running Specific Tests

```bash
# Run a specific test
python -m unittest tests.test_phase0_comprehensive.TestSuite1_Imports.test_001_config_import

# Run with verbose output
python -m unittest -v tests.test_phase0_comprehensive
```

### Test Environment Requirements

- **Python**: 3.14+ (tested on 3.14.2)
- **Virtual Environment**: Required (venv)
- **Dependencies**: Listed in `requirements.txt`
- **Platform**: macOS (should work on Linux/Windows)

### Key Test Features

1. **Isolation**: Each test is isolated with setUp/tearDown
2. **Cleanup**: Temporary files and sessions properly cleaned
3. **Async Support**: Tests handle async session termination
4. **Error Handling**: Tests verify error conditions
5. **Platform Support**: Cross-platform clipboard testing

### Troubleshooting

#### Tests Fail to Import Modules

```bash
# Ensure you're in the correct directory
cd /Users/wallonwalusayi/claude-multi-terminal

# Activate virtual environment
source venv/bin/activate

# Verify package is installed
pip list | grep claude-multi-terminal
```

#### Async Tests Fail

The test suite creates new event loops for async operations. If you encounter issues:

```python
# The tests handle this, but for manual testing:
import asyncio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
result = loop.run_until_complete(async_function())
loop.close()
```

#### Clipboard Tests Skip

Clipboard operations may fail in headless environments. This is expected and the test will skip gracefully.

### Adding New Tests

When adding new functionality, follow this pattern:

```python
def test_NNN_descriptive_name(self):
    """Clear description of what this test verifies"""
    # Arrange: Set up test data
    test_data = create_test_data()

    # Act: Perform the operation
    result = function_under_test(test_data)

    # Assert: Verify the result
    self.assertEqual(result.expected_field, expected_value)
    self.assertTrue(result.success)
```

### Test Naming Convention

- Test methods: `test_NNN_descriptive_name`
- Test classes: `TestSuiteN_Category`
- Test files: `test_*.py`

### Coverage Goals

- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows

### Continuous Testing

For development:

```bash
# Install pytest-watch
pip install pytest-watch

# Run tests on file changes
ptw tests/
```

### Test Reports

Full test report available in: `PHASE0_TEST_REPORT.md`

### Next Steps

1. ✅ Phase 0 tests complete
2. 🔄 Phase 1 tests (TUI implementation)
3. ⏳ Phase 2 tests (Advanced features)

### Contact

For test issues or questions, refer to:
- Test report: `PHASE0_TEST_REPORT.md`
- Core module docs: `CORE_MODULE_DOCUMENTATION.md`
- Implementation summary: `CORE_MODULE_IMPLEMENTATION_SUMMARY.md`
