import json
import os
import sys
import pytest
from click.testing import CliRunner

# Ensure the package can be imported when running test directly via pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sd_revolution.image_metadata import extract_metadata


def test_extract_metadata():
    """Test image metadata extraction"""
    runner = CliRunner()

    # Set up paths
    test_dir = os.path.dirname(__file__)
    input_file = os.path.join(test_dir, "input", "alphinaud-older-with-beard.png")
    output_dir = os.path.join(test_dir, "output", "alphinaud-older-with-beard")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Output files
    txt_output = os.path.join(output_dir, "metadata.txt")
    json_output = os.path.join(output_dir, "metadata.json")

    # Run extract_metadata command
    result = runner.invoke(extract_metadata, [
        '-i', input_file,
        '-t', txt_output,
        '-j', json_output
    ])

    # Check command succeeded
    assert result.exit_code == 0, f"Command failed with: {result.output}"

    # Verify txt output exists and has content
    assert os.path.exists(txt_output), "Text output file not created"
    with open(txt_output, 'r') as f:
        txt_content = f.read()
    assert len(txt_content) > 0, "Text output is empty"

    # Verify json output exists and is valid JSON
    assert os.path.exists(json_output), "JSON output file not created"
    with open(json_output, 'r') as f:
        json_content = json.load(f)
    assert isinstance(json_content, dict), "JSON output is not a dictionary"
    assert len(json_content) > 0, "JSON output is empty"

    # Print outputs for inspection
    print(f"\n--- Raw metadata (text) ---\n{txt_content}\n")
    print(f"--- Structured metadata (JSON) ---\n{json.dumps(json_content, indent=2)}\n")
