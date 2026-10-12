# Quick Start Guide - MTLnet Test Suite

## 🚀 Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Tests by Module
```bash
# ETL tests (✅ implemented)
pytest tests/etl/ -v

# Model tests (📝 stubs)
pytest tests/model/ -v --allow-skip

# Loss function tests (📝 stubs)
pytest tests/criterion/ -v --allow-skip

# Utility tests (📝 stubs)
pytest tests/common/ -v --allow-skip

# Config tests (📝 stubs)
pytest tests/configs/ -v --allow-skip
```

### Run with Coverage
```bash
# Full coverage report
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html

# Module-specific coverage
pytest tests/etl/ --cov=src/etl/mtl_input --cov-report=term-missing
```

## 📁 Test Structure

```
tests/
├── etl/           ✅ 52+ tests - ETL and data preparation
├── criterion/     📝 Stubs - Loss functions (NashMTL, FocalLoss, etc.)
├── model/         📝 Stubs - Model architectures (MTLnet, heads)
├── common/        📝 Stubs - Utilities (history, FLOPs, progress)
├── configs/       📝 Stubs - Configuration management
└── embeddings/    📝 Stubs - Embedding utilities
```

## 📊 Current Status

| Module | Status | Tests | Coverage | Priority |
|--------|--------|-------|----------|----------|
| **etl/** | ✅ Implemented | 52+ | 58% | - |
| **criterion/** | 📝 Stub | 0 | 0% | 🔴 High |
| **model/** | 📝 Stub | 0 | 0% | 🔴 High |
| **common/** | 📝 Stub | 0 | 0% | 🟡 Medium |
| **configs/** | 📝 Stub | 0 | 0% | 🟡 Medium |
| **embeddings/** | 📝 Stub | 0 | 0% | 🟢 Low |

## 🎯 Next Steps

### For Contributors

1. **Pick a stub file** from high priority modules
2. **Read** [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
3. **Implement** tests following the patterns
4. **Run** tests and verify coverage
5. **Commit** when coverage > 85%

### Priority Order

1. 🔴 **High Priority** (implement first):
   - `criterion/test_nash_mtl.py`
   - `criterion/test_focal_loss.py`
   - `model/test_mtlnet.py`
   - `model/test_category_head.py`
   - `model/test_next_head.py`

2. 🟡 **Medium Priority** (implement next):
   - `common/test_ml_history.py`
   - `common/test_calc_flops.py`
   - `configs/test_paths.py`

3. 🟢 **Low Priority** (implement last):
   - `criterion/test_pcgrad.py`
   - `criterion/test_gradnorm.py`
   - `embeddings/test_embedding_utils.py`

## 📚 Documentation

- **[README.md](README.md)** - Main test documentation
- **[TEST_ORGANIZATION.md](TEST_ORGANIZATION.md)** - Detailed structure
- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - How to implement tests
- **[TEST_SUMMARY.md](TEST_SUMMARY.md)** - Test results

## 🛠️ Common Commands

```bash
# Run specific test file
pytest tests/etl/test_mtl_input_core.py -v

# Run specific test class
pytest tests/etl/test_mtl_input_core.py::TestGenerateSequences -v

# Run specific test method
pytest tests/etl/test_mtl_input_core.py::TestGenerateSequences::test_empty_list_returns_empty -v

# Run tests matching pattern
pytest tests/ -k "initialization" -v

# Run with verbose output
pytest tests/ -vv

# Stop on first failure
pytest tests/ -x

# Show print statements
pytest tests/ -s

# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html
```

## ✅ Verification

Test that everything works:

```bash
# Should pass
pytest tests/etl/test_mtl_input_core.py::TestGenerateSequences::test_empty_list_returns_empty -v

# Should show structure
ls -R tests/

# Should show 24 test files
find tests -name "test_*.py" | wc -l
```

## 🐛 Troubleshooting

### Import Errors
```bash
# Verify you're in project root
pwd  # Should end in /ingred

# Verify pytest.ini exists
ls pytest.ini

# Verify Python path
python -c "import sys; print('\\n'.join(sys.path))"
```

### Tests Not Found
```bash
# Clear pytest cache
pytest --cache-clear

# Verify test discovery
pytest tests/ --collect-only
```

### Coverage Not Working
```bash
# Reinstall pytest-cov
pip uninstall pytest-cov
pip install pytest-cov

# Run with explicit source
pytest tests/ --cov=src --cov-report=term
```

## 📞 Need Help?

1. Check existing ETL tests for implementation examples
2. Review [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
3. Read [TEST_ORGANIZATION.md](TEST_ORGANIZATION.md) for structure
4. Look at stub files for test structure
