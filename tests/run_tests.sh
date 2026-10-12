#!/bin/bash
# Quick test runner for MTL input tests

echo "================================"
echo "MTL Input Test Suite Runner"
echo "================================"
echo ""

# Check if pytest is installed
if ! python -m pytest --version &> /dev/null; then
    echo "Installing test dependencies..."
    pip install pytest pytest-cov -q
fi

# Parse arguments
case "$1" in
    "quick")
        echo "Running quick tests (no coverage)..."
        python -m pytest tests/ -v
        ;;
    "coverage")
        echo "Running tests with coverage report..."
        python -m pytest tests/ --cov=src/etl/mtl_input --cov-report=term-missing --cov-report=html
        echo ""
        echo "Coverage report saved to htmlcov/index.html"
        ;;
    "core")
        echo "Running core tests only..."
        python -m pytest tests/test_mtl_input_core.py -v
        ;;
    "builders")
        echo "Running builder tests only..."
        python -m pytest tests/test_mtl_input_builders.py -v
        ;;
    "fusion")
        echo "Running fusion tests only..."
        python -m pytest tests/test_mtl_input_fusion.py -v
        ;;
    "watch")
        echo "Running tests in watch mode..."
        while true; do
            clear
            python -m pytest tests/ -v
            echo ""
            echo "Watching for changes... (Ctrl+C to stop)"
            sleep 2
        done
        ;;
    *)
        echo "Usage: ./run_tests.sh [command]"
        echo ""
        echo "Commands:"
        echo "  quick     - Run all tests without coverage"
        echo "  coverage  - Run all tests with coverage report (default)"
        echo "  core      - Run core tests only"
        echo "  builders  - Run builder tests only"
        echo "  fusion    - Run fusion tests only"
        echo "  watch     - Run tests in watch mode"
        echo ""
        echo "Running with coverage (default)..."
        python -m pytest tests/ --cov=src/etl/mtl_input --cov-report=term-missing --cov-report=html
        echo ""
        echo "Coverage report saved to htmlcov/index.html"
        ;;
esac

echo ""
echo "================================"
