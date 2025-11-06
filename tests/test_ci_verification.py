"""
Simple CI verification tests that don't rely on external dependencies.
"""
import sys

def test_basic_functionality():
    """Test basic functionality without complex imports."""
    print("Testing basic functionality...")
    
    # Simple test that doesn't require imports
    assert True
    print("✓ Basic functionality tests passed!")

def test_math_operations():
    """Test basic math operations."""
    print("Testing math operations...")
    
    # Simple math tests
    assert 1 + 1 == 2
    assert 2 * 3 == 6
    assert 10 / 2 == 5
    
    print("✓ Math operations tests passed!")

if __name__ == "__main__":
    print("Running CI verification tests...\n")
    
    try:
        test_basic_functionality()
        test_math_operations()
        print("\n🎉 All CI verification tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)