import os
import sys
import pytest
from click.testing import CliRunner

# Ensure the package can be imported when running test directly via pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sd_revolution.utils import generate_combinations
from sd_revolution.matrixify import matrixify

def test_generate_combinations_two_lists():
    sections = [["a", "b"], ["1", "2"]]
    expected = [["a", "1"], ["a", "2"], ["b", "1"], ["b", "2"]]
    assert generate_combinations(sections) == expected

def test_generate_combinations_empty():
    assert generate_combinations([]) == []

def test_matrixify_example1():
    """Test matrixify command using Example 1 from the docstring"""
    runner = CliRunner()

    # Set up paths
    test_dir = os.path.dirname(__file__)
    input_dir = os.path.join(test_dir, "input", "matrixify", "1")
    output_dir = os.path.join(test_dir, "output", "matrixify", "1")

    # Create directories if they don't exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # Create input files
    file1 = os.path.join(input_dir, "file1.txt")
    file2 = os.path.join(input_dir, "file2.txt")
    file3 = os.path.join(input_dir, "file3.txt")

    with open(file1, 'w') as f:
        f.write("abc, 123, yyy\n111, 222,\n")

    with open(file2, 'w') as f:
        f.write("lion, tiger,\nhippo, elephant,\n")

    with open(file3, 'w') as f:
        f.write("a,\nb, 12345,\nc, 6789,\n")

    # Output file
    output_file = os.path.join(output_dir, "output.txt")

    # Run matrixify command
    result = runner.invoke(matrixify, [
        '-p', file1,
        '-p', file2,
        '-p', file3,
        '-o', output_file
    ])

    # Check command succeeded
    assert result.exit_code == 0, f"Command failed with: {result.output}"

    # Read output
    with open(output_file, 'r') as f:
        output_content = f.read()

    # Expected output from Example 1
    expected = """abc, 123, yyy, lion, tiger, a,
abc, 123, yyy, lion, tiger, b, 12345,
abc, 123, yyy, lion, tiger, c, 6789,
abc, 123, yyy, hippo, elephant, a,
abc, 123, yyy, hippo, elephant, b, 12345,
abc, 123, yyy, hippo, elephant, c, 6789,
111, 222, lion, tiger, a,
111, 222, lion, tiger, b, 12345,
111, 222, lion, tiger, c, 6789,
111, 222, hippo, elephant, a,
111, 222, hippo, elephant, b, 12345,
111, 222, hippo, elephant, c, 6789,"""

    assert output_content == expected, f"Output mismatch:\nGot:\n{output_content}\n\nExpected:\n{expected}"
