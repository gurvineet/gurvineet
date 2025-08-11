#!/usr/bin/env python3
"""
Test Runner for CloudKitchens Kitchen Workflow Optimization System

Uses only Python standard library for testing.
"""
import sys
import os
import unittest
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_all_tests():
    """Run all tests in the test suite."""
    print("CloudKitchens Kitchen Workflow Optimization - Test Suite")
    print("=" * 60)
    print("Running tests using Python standard library only...")
    print()
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Total time: {end_time - start_time:.2f} seconds")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)