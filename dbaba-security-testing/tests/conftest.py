"""
Pytest configuration and fixtures for DBABA security testing.
"""
import pytest
import os
import subprocess
import time
import tempfile
import shutil
from pathlib import Path


@pytest.fixture(scope="session")
def dbaba_path():
    """Path to the DBABA executable."""
    return Path(__file__).parent.parent / "M4-dbaba-2024" / "dbaba" / "dbaba.py"


@pytest.fixture(scope="session")
def dbaba_working_dir():
    """Working directory for DBABA tests."""
    return Path(__file__).parent.parent / "M4-dbaba-2024" / "dbaba"


@pytest.fixture(scope="function")
def clean_dbaba_state(dbaba_working_dir):
    """Clean up DBABA state before each test."""
    # Remove all non-Python files to reset state
    for file in dbaba_working_dir.glob("*"):
        if not file.name.endswith('.py'):
            if file.is_file():
                file.unlink()
            elif file.is_dir():
                shutil.rmtree(file)
    yield
    # Clean up after test
    for file in dbaba_working_dir.glob("*"):
        if not file.name.endswith('.py'):
            if file.is_file():
                file.unlink()
            elif file.is_dir():
                shutil.rmtree(file)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_user():
    """Standard test user for testing."""
    return "testuser"


@pytest.fixture
def test_password():
    """Standard test password for testing."""
    return "TestPass123"


@pytest.fixture
def admin_password():
    """Admin password for testing."""
    return "AdminPass123"
