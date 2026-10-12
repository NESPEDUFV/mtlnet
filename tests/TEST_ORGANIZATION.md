# Test Organization Guide

This document describes the organization and structure of the MTLnet test suite.

## Directory Structure

```
tests/
├── conftest.py                 # Shared fixtures and pytest configuration
├── fixtures/                   # Test data fixtures
├── README.md                   # Main test documentation
├── TEST_SUMMARY.md            # Test results summary
├── TEST_ORGANIZATION.md       # This file
│
├── etl/                       # ETL and data preparation tests
│   ├── __init__.py
│   ├── test_mtl_input_core.py              # ✅ 32 tests - 96% coverage
│   ├── test_mtl_input_builders.py          # ✅ 7 tests - 52% coverage
│   ├── test_mtl_input_fusion.py            # ✅ 13 tests - 37% coverage
│   └── test_mtl_input_checkin_conversion.py # ✅ Implemented
│
├── criterion/                 # Loss function tests
│   ├── __init__.py
│   ├── test_nash_mtl.py       # 📝 Stub - Nash-MTL gradient balancing
│   ├── test_focal_loss.py     # 📝 Stub - Focal loss for imbalanced data
│   ├── test_pcgrad.py         # 📝 Stub - PCGrad gradient projection
│   └── test_gradnorm.py       # 📝 Stub - GradNorm balancing
│
├── model/                     # Model architecture tests
│   ├── __init__.py
│   ├── test_mtlnet.py         # 📝 Stub - MTLnet main architecture
│   ├── test_category_head.py # 📝 Stub - Category prediction head
│   └── test_next_head.py      # 📝 Stub - Next-POI prediction head
│
├── common/                    # Utility tests
│   ├── __init__.py
│   ├── test_ml_history.py     # 📝 Stub - Experiment tracking
│   ├── test_calc_flops.py     # 📝 Stub - FLOPs calculation
│   └── test_training_progress.py # 📝 Stub - Progress bars
│
├── configs/                   # Configuration tests
│   ├── __init__.py
│   ├── test_model_config.py   # 📝 Stub - Model configuration
│   └── test_paths.py          # 📝 Stub - Path management
│
└── embeddings/                # Embedding utility tests
    ├── __init__.py
    └── test_embedding_utils.py # 📝 Stub - Embedding utilities
```

## Module Mapping

Each test directory corresponds to a source module:

| Test Directory | Source Module | Purpose |
|---------------|---------------|---------|
| `tests/etl/` | `src/etl/mtl_input/` | Input generation, sequence creation, fusion |
| `tests/criterion/` | `src/criterion/` | Loss functions and MTL balancing |
| `tests/model/` | `src/model/mtlnet/` | Model architectures |
| `tests/common/` | `src/common/` | Utilities (history, FLOPs, progress) |
| `tests/configs/` | `src/configs/` | Configuration management |
| `tests/embeddings/` | `src/embeddings/` | Embedding utilities |

## Test Categories

### 1. Unit Tests
- Test individual functions and classes in isolation
- Located in: All test files
- Example: `test_mtl_input_core.py::TestGenerateSequences`

### 2. Integration Tests
- Test interactions between components
- Located in: `test_*_integration` classes
- Example: `test_nash_mtl.py::TestNashMTLIntegration`

### 3. End-to-End Tests
- Test complete workflows (future addition)
- Would be located in: `tests/e2e/` (to be created)
- Example: Full training pipeline test

## Running Tests

### By Module
```bash
# ETL tests (implemented)
pytest tests/etl/ -v

# Model tests (stubs)
pytest tests/model/ -v --allow-skip

# Loss function tests (stubs)
pytest tests/criterion/ -v --allow-skip

# All tests
pytest tests/ -v
```

### By Coverage
```bash
# ETL module coverage
pytest tests/etl/ --cov=src/etl/mtl_input --cov-report=html

# Full project coverage
pytest tests/ --cov=src --cov-report=html

# Specific module coverage
pytest tests/model/ --cov=src/model --cov-report=term-missing
```

### By Pattern
```bash
# All initialization tests
pytest tests/ -k "initialization" -v

# All integration tests
pytest tests/ -k "integration" -v

# All Nash-MTL tests
pytest tests/criterion/test_nash_mtl.py -v
```

## Implementation Status

### ✅ Completed (52+ tests)
- **etl/test_mtl_input_core.py** - Core logic functions
- **etl/test_mtl_input_builders.py** - Input builders
- **etl/test_mtl_input_fusion.py** - Multi-embedding fusion
- **etl/test_mtl_input_checkin_conversion.py** - Check-in conversions

### 📝 Stub Files (50+ test cases defined)
All stub files contain:
- Test class structure
- Test method signatures
- Docstrings describing test intent
- `pytest.skip()` markers for future implementation

**High Priority:**
- criterion/test_nash_mtl.py
- criterion/test_focal_loss.py
- model/test_mtlnet.py
- model/test_category_head.py
- model/test_next_head.py

**Medium Priority:**
- common/test_ml_history.py
- common/test_calc_flops.py
- configs/test_paths.py

**Low Priority:**
- criterion/test_pcgrad.py
- criterion/test_gradnorm.py
- embeddings/test_embedding_utils.py

## Writing New Tests

### Test File Template

```python
"""Tests for <module_name>."""

import pytest
import torch  # if needed
import torch.nn as nn  # if needed


class Test<ClassName>:
    """Test suite for <ClassName>."""

    def test_initialization(self):
        """Test initialization with valid parameters."""
        # Arrange
        param1 = "value1"
        param2 = 42

        # Act
        instance = ClassName(param1, param2)

        # Assert
        assert instance.param1 == param1
        assert instance.param2 == param2

    def test_edge_case(self):
        """Test behavior with edge case input."""
        # Arrange, Act, Assert
        pass


class Test<ClassName>Integration:
    """Integration tests for <ClassName>."""

    def test_integration_scenario(self):
        """Test integration with other components."""
        pass
```

### Naming Conventions

- **Test files**: `test_<module_name>.py`
- **Test classes**: `Test<ClassName>` or `Test<ClassName>Integration`
- **Test methods**: `test_<what_is_being_tested>`
- **Fixtures**: Descriptive names in `conftest.py`

### Best Practices

1. **Arrange-Act-Assert (AAA)** pattern
2. **One assertion per concept** (not strictly one per test)
3. **Descriptive test names** - should read like documentation
4. **Use fixtures** for common setup
5. **Mock external dependencies** (file I/O, network calls)
6. **Test edge cases** - empty inputs, None, extremes
7. **Aim for ≥90% coverage** on new code

## Coverage Goals

| Module | Current | Target | Priority |
|--------|---------|--------|----------|
| etl/mtl_input | 58% | 90% | High |
| criterion/ | 0% | 85% | High |
| model/ | 0% | 80% | High |
| common/ | 0% | 75% | Medium |
| configs/ | 0% | 70% | Medium |
| embeddings/ | 0% | 60% | Low |

## Fixtures

Shared fixtures are defined in `conftest.py`:

```python
@pytest.fixture
def sample_checkins():
    """Sample check-in data for testing."""
    return pd.DataFrame(...)

@pytest.fixture
def sample_embeddings():
    """Sample embeddings for testing."""
    return {...}
```

## Continuous Integration

The test suite is designed for CI/CD integration:

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest tests/ --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Migration Notes

### What Changed (2026-02-04)

**Before:**
```
tests/
├── conftest.py
├── test_mtl_input_core.py
├── test_mtl_input_builders.py
├── test_mtl_input_fusion.py
└── test_mtl_input_checkin_conversion.py
```

**After:**
```
tests/
├── etl/
│   ├── test_mtl_input_core.py
│   ├── test_mtl_input_builders.py
│   ├── test_mtl_input_fusion.py
│   └── test_mtl_input_checkin_conversion.py
├── criterion/
│   └── [4 stub files]
├── model/
│   └── [3 stub files]
├── common/
│   └── [3 stub files]
├── configs/
│   └── [2 stub files]
└── embeddings/
    └── [1 stub file]
```

### Running Old Commands

Old commands still work:
```bash
# Old: pytest tests/test_mtl_input_core.py
# New: pytest tests/etl/test_mtl_input_core.py
```

## Related Documentation

- [README.md](README.md) - Main test documentation
- [TEST_SUMMARY.md](TEST_SUMMARY.md) - Detailed test results
- [../CLAUDE.md](../CLAUDE.md) - Project overview
- [../REFACTORING_SUMMARY.md](../REFACTORING_SUMMARY.md) - Refactoring details

## Questions?

- Check [README.md](README.md) for common usage patterns
- See stub files for test structure examples
- Review existing ETL tests for implementation examples
