import os
import sys
import pytest

# Ensure the package can be imported when running tests directly via pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sd_revolution.__main__ import generate_combinations

def test_generate_combinations_two_lists():
    sections = [["a", "b"], ["1", "2"]]
    expected = [["a", "1"], ["a", "2"], ["b", "1"], ["b", "2"]]
    assert generate_combinations(sections) == expected

def test_generate_combinations_empty():
    assert generate_combinations([]) == []
