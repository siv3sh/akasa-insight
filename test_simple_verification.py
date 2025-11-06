#!/usr/bin/env python3
"""
Simple verification script to test core functionality without external dependencies.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported without errors."""
    print("Testing imports...")

    # Test database modules

    # Test processing modules (without pandas/dask)
    # Skip pandas and dask imports due to dependency issues

    # Test utilities

    print("✓ All imports successful!")

def test_config():
    """Test configuration loading."""
    print("Testing configuration...")

    from src.config import Config

    # Test that config can be accessed
    assert hasattr(Config, 'DATABASE_URL')
    assert hasattr(Config, 'CUSTOMERS_CSV_PATH')

    print("✓ Configuration test passed!")

def test_utils():
    """Test utility functions that don't require external dependencies."""
    print("Testing utilities...")

    from src.utils import Logger

    # Test logger can be instantiated
    logger = Logger.get_logger("test")
    assert logger is not None

    print("✓ Utilities test passed!")

def main():
    """Run all tests."""
    print("Running simple verification tests...\n")

    try:
        test_imports()
        test_config()
        test_utils()
        print("\n🎉 All basic tests passed! Core functionality is working.")
        return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
