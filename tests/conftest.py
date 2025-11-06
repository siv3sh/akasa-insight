"""
pytest configuration and fixtures for CI.
"""
import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database for testing."""
    # Create temporary database
    temp_db_path = tempfile.mktemp(suffix='.db')
    database_url = f"sqlite:///{temp_db_path}"

    yield database_url

    # Cleanup
    if os.path.exists(temp_db_path):
        os.unlink(temp_db_path)


@pytest.fixture
def test_data_dir():
    """Provide path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_csv_file(test_data_dir):
    """Provide path to sample CSV file."""
    return test_data_dir / "customers.csv"


@pytest.fixture
def sample_xml_file(test_data_dir):
    """Provide path to sample XML file."""
    return test_data_dir / "orders.xml"
