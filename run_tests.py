#!/usr/bin/env python3
"""
Test runner script for the Log Analyzer project.
Runs all unit tests and generates a coverage report.
"""
import subprocess
import sys
import os

def run_tests():
    """Run all tests with pytest and coverage"""
    print("=" * 70)
    print("Running Unit Tests for Log Analyzer Project")
    print("=" * 70)

    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    # Run pytest with coverage
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "test/",
        "-v",
        "--tb=short",
        "--cov=analyzer",
        "--cov=utils",
        "--cov-report=html",
        "--cov-report=term-missing"
    ]

    print(f"\nCommand: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=project_root)

    print("\n" + "=" * 70)
    if result.returncode == 0:
        print("✅ All tests passed!")
        print("\n📊 Coverage report generated in htmlcov/index.html")
    else:
        print("❌ Some tests failed!")
        print(f"Exit code: {result.returncode}")
    print("=" * 70)

    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
