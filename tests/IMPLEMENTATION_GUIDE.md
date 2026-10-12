# Test Implementation Guide

Quick guide for implementing the stub test files.

## Implementation Priority

### 🔴 High Priority (Core Functionality)

These tests are critical for validating the main components:

1. **criterion/test_nash_mtl.py** - Primary MTL loss
   - Tests Nash equilibrium gradient balancing
   - Validates task weight updates
   - Ensures gradient manipulation works correctly

2. **criterion/test_focal_loss.py** - Class imbalance handling
   - Tests focal loss calculation
   - Validates gamma/alpha parameters
   - Compares with standard CrossEntropy

3. **model/test_mtlnet.py** - Main architecture
   - Tests FiLM modulation
   - Validates shared vs task-specific parameters
   - Ensures forward pass works correctly
   - Tests residual connections

4. **model/test_category_head.py** - Category prediction
   - Tests multi-path ensemble
   - Validates output dimensions
   - Ensures proper classification

5. **model/test_next_head.py** - Next-POI prediction
   - Tests transformer encoder
   - Validates positional encoding
   - Tests causal masking
   - Validates attention pooling

### 🟡 Medium Priority (Infrastructure)

6. **common/test_ml_history.py** - Experiment tracking
   - Tests metric recording
   - Validates storage/serialization
   - Tests plot generation

7. **common/test_calc_flops.py** - Performance profiling
   - Tests FLOPs calculation
   - Validates layer-wise profiling

8. **configs/test_paths.py** - Path management
   - Tests path resolution
   - Validates FUSION routing
   - Tests environment variable handling

### 🟢 Low Priority (Optional)

9. **criterion/test_pcgrad.py** - Alternative MTL
10. **criterion/test_gradnorm.py** - Alternative MTL
11. **common/test_training_progress.py** - Progress utilities
12. **configs/test_model_config.py** - Config validation
13. **embeddings/test_embedding_utils.py** - Embedding utilities

## Implementation Steps

### Step 1: Read the Source Code

Before implementing tests, understand the module:

```bash
# Read the source file
cat src/criterion/nash_mtl.py

# Look for:
# - Class names and constructors
# - Public methods
# - Expected inputs/outputs
# - Edge cases
```

### Step 2: Set Up Test Structure

```python
"""Tests for <ModuleName>."""

import pytest
import torch
import torch.nn as nn
from src.criterion.nash_mtl import NashMTL  # Import what you're testing


class Test<ClassName>:
    """Test suite for <ClassName>."""

    @pytest.fixture
    def instance(self):
        """Create instance for testing."""
        return ClassName(param1="value", param2=42)

    def test_initialization(self):
        """Test initialization with valid parameters."""
        obj = ClassName(param1="value")
        assert obj.param1 == "value"
```

### Step 3: Write Tests

Follow AAA pattern (Arrange-Act-Assert):

```python
def test_something(self):
    """Test that something works correctly."""
    # Arrange - set up test data
    input_data = torch.randn(10, 64)
    expected_output = ...

    # Act - call the method being tested
    actual_output = my_function(input_data)

    # Assert - verify results
    assert actual_output.shape == expected_output.shape
    torch.testing.assert_close(actual_output, expected_output)
```

### Step 4: Test Edge Cases

```python
def test_empty_input(self):
    """Test behavior with empty input."""
    result = my_function([])
    assert result == []

def test_none_input(self):
    """Test behavior with None input."""
    with pytest.raises(ValueError):
        my_function(None)

def test_invalid_dimensions(self):
    """Test behavior with wrong dimensions."""
    with pytest.raises(ValueError):
        my_function(torch.randn(5))  # Expected 2D, got 1D
```

### Step 5: Run and Verify

```bash
# Run your new tests
pytest tests/criterion/test_nash_mtl.py -v

# Check coverage
pytest tests/criterion/test_nash_mtl.py --cov=src/criterion/nash_mtl --cov-report=term-missing

# Aim for >85% coverage
```

## Example: NashMTL Implementation

Here's how to implement `test_nash_mtl.py`:

### 1. Read the source
```bash
cat src/criterion/nash_mtl.py
# Look for: __init__, backward, update_weights, etc.
```

### 2. Replace stub with real tests

```python
"""Tests for NashMTL loss function."""

import pytest
import torch
import torch.nn as nn
from src.criterion.nash_mtl import NashMTL


class TestNashMTL:
    """Test suite for Nash-MTL gradient balancing."""

    @pytest.fixture
    def simple_model(self):
        """Create a simple two-task model."""
        class SimpleMTL(nn.Module):
            def __init__(self):
                super().__init__()
                self.shared = nn.Linear(10, 20)
                self.task1_head = nn.Linear(20, 5)
                self.task2_head = nn.Linear(20, 3)

            def forward(self, x):
                shared_features = self.shared(x)
                return {
                    'task1': self.task1_head(shared_features),
                    'task2': self.task2_head(shared_features)
                }

            def shared_parameters(self):
                return self.shared.parameters()

            def task_specific_parameters(self):
                return list(self.task1_head.parameters()) + \
                       list(self.task2_head.parameters())

        return SimpleMTL()

    def test_initialization(self, simple_model):
        """Test NashMTL initialization with valid parameters."""
        nash_mtl = NashMTL(
            model=simple_model,
            n_tasks=2,
            max_norm=2.2,
            update_weights_every=4,
            optim_niter=30
        )

        assert nash_mtl.n_tasks == 2
        assert nash_mtl.max_norm == 2.2
        assert nash_mtl.update_weights_every == 4

    def test_backward_pass(self, simple_model):
        """Test gradient balancing in backward pass."""
        nash_mtl = NashMTL(model=simple_model, n_tasks=2)

        # Create dummy losses
        task1_loss = torch.tensor(1.5, requires_grad=True)
        task2_loss = torch.tensor(2.0, requires_grad=True)
        losses = [task1_loss, task2_loss]

        # Perform backward pass
        nash_mtl.backward(losses)

        # Check that gradients were computed
        for param in simple_model.parameters():
            assert param.grad is not None

    def test_weight_update(self, simple_model):
        """Test task weight updates."""
        nash_mtl = NashMTL(
            model=simple_model,
            n_tasks=2,
            update_weights_every=2
        )

        initial_weights = nash_mtl.task_weights.clone()

        # Run a few iterations
        for i in range(5):
            task1_loss = torch.tensor(1.0 + i * 0.1, requires_grad=True)
            task2_loss = torch.tensor(2.0 - i * 0.1, requires_grad=True)
            nash_mtl.backward([task1_loss, task2_loss])

        # Weights should have been updated
        assert not torch.allclose(nash_mtl.task_weights, initial_weights)

    def test_nash_equilibrium(self, simple_model):
        """Test Nash equilibrium convergence."""
        nash_mtl = NashMTL(model=simple_model, n_tasks=2, optim_niter=50)

        # Test that weights sum to n_tasks (normalization)
        assert torch.isclose(
            nash_mtl.task_weights.sum(),
            torch.tensor(2.0),
            rtol=1e-3
        )


class TestNashMTLIntegration:
    """Integration tests for NashMTL with multiple tasks."""

    def test_two_task_training(self):
        """Test NashMTL with two tasks in training loop."""
        # Create model, optimizer, NashMTL
        # Run a few training iterations
        # Verify losses decrease
        pass  # Implement based on actual training logic

    def test_gradient_manipulation(self):
        """Test gradient manipulation across tasks."""
        # Test that conflicting gradients are balanced
        pass  # Implement based on gradient analysis
```

### 3. Run tests
```bash
pytest tests/criterion/test_nash_mtl.py -v
```

## Common Patterns

### Testing PyTorch Models

```python
def test_forward_pass(self):
    """Test model forward pass."""
    model = MyModel(input_dim=64, output_dim=10)
    x = torch.randn(32, 64)  # batch_size=32

    output = model(x)

    assert output.shape == (32, 10)
    assert not torch.isnan(output).any()
    assert not torch.isinf(output).any()
```

### Testing Loss Functions

```python
def test_loss_computation(self):
    """Test loss computation."""
    criterion = MyLoss()
    predictions = torch.randn(10, 5)
    targets = torch.randint(0, 5, (10,))

    loss = criterion(predictions, targets)

    assert loss.item() >= 0  # Loss should be non-negative
    assert loss.requires_grad  # Should be differentiable
```

### Testing with Fixtures

```python
@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {
        'input': torch.randn(10, 64),
        'target': torch.randint(0, 7, (10,)),
        'embeddings': torch.randn(100, 64)
    }

def test_with_fixture(self, sample_data):
    """Test using fixture data."""
    output = my_function(sample_data['input'])
    assert output.shape[0] == 10
```

### Testing Exceptions

```python
def test_invalid_input_raises_error(self):
    """Test that invalid input raises ValueError."""
    with pytest.raises(ValueError, match="dimension must be"):
        MyClass(dimension=-1)
```

## Coverage Tips

1. **Test all public methods** - Every public method should have at least one test
2. **Test edge cases** - Empty inputs, None, extremes, invalid types
3. **Test error conditions** - What happens when things go wrong?
4. **Test integration** - How do components work together?
5. **Don't test private methods** - Focus on public API

## Running Your Tests

```bash
# Run specific test file
pytest tests/criterion/test_nash_mtl.py -v

# Run with coverage
pytest tests/criterion/test_nash_mtl.py \
    --cov=src/criterion/nash_mtl \
    --cov-report=term-missing

# Run only tests you're working on
pytest tests/criterion/test_nash_mtl.py::TestNashMTL::test_initialization -v

# Run all high-priority tests
pytest tests/criterion/ tests/model/ -v
```

## When You're Done

1. ✅ All tests pass
2. ✅ Coverage > 85%
3. ✅ No `pytest.skip()` markers remain
4. ✅ Tests are well-documented
5. ✅ Edge cases are covered

## Questions?

- Look at implemented ETL tests for examples
- Check pytest documentation: https://docs.pytest.org
- Review PyTorch testing guide: https://pytorch.org/docs/stable/testing.html
