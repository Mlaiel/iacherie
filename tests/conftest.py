# -*- coding: utf-8 -*-
"""
Configuration globale pour les tests pytest
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from typing import Generator

# Set up test environment
@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Directory for test data"""
    return Path(__file__).parent / "data"

@pytest.fixture(scope="session")
def temp_dir() -> Generator[Path, None, None]:
    """Temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture(scope="session")
def event_loop():
    """Event loop pour les tests asyncio"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_test_file(temp_dir: Path) -> Path:
    """Create a sample test file"""
    test_file = temp_dir / "test_content.txt"
    test_file.write_text("This is a test content file for validation tests.")
    return test_file

@pytest.fixture
def mock_config():
    """Mock configuration for tests"""
    return {
        "debug": True,
        "testing": True,
        "database_url": "sqlite:///:memory:",
        "redis_url": "redis://localhost:6379/1"
    }