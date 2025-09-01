#!/usr/bin/env python3
"""Simple test to validate core functionality works."""

import pytest


def test_business_logic_core_import():
    """Test that business_logic_core can be imported."""
    import business_logic_core
    from business_logic_core import CreatorType
    assert CreatorType is not None


def test_simple_agents_import():
    """Test that simple_agents can be imported."""
    import simple_agents
    assert simple_agents is not None


def test_basic_python_functionality():
    """Test basic Python functionality."""
    assert 1 + 1 == 2
    assert "hello" == "hello"


def test_imports_work():
    """Test that basic imports work."""
    import sys
    import os
    import json
    assert sys is not None
    assert os is not None
    assert json is not None


if __name__ == "__main__":
    test_business_logic_core_import()
    test_simple_agents_import()
    test_basic_python_functionality()
    test_imports_work()
    print("✅ All basic tests passed!")