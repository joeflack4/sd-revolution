"""Image metadata extraction CLI commands"""
import json
import re
from typing import Dict, Any

import click
from PIL import Image
from PIL.PngImagePlugin import PngInfo


def parse_metadata_to_structured(raw_metadata: str) -> Dict[str, Any]:
    """
    Parse raw metadata string into structured format.

    Typical Stable Diffusion metadata format:
    prompt text (can be multi-line)
    Negative prompt: negative prompt text (can be multi-line)
    Steps: 20, Sampler: DPM++ 2M Karras, CFG scale: 7, Seed: 123456, Size: 512x768, Model: model_name
    """
    structured = {}

    if not raw_metadata or not raw_metadata.strip():
        return structured

    lines = raw_metadata.strip().split('\n')

    # Find the indices of key sections
    negative_prompt_idx = None
    parameters_idx = None

    for i, line in enumerate(lines):
        if line.startswith('Negative prompt:'):
            negative_prompt_idx = i
        elif 'Steps:' in line and ',' in line:
            # This looks like the parameters line
            parameters_idx = i
            break

    # Extract prompt (everything before "Negative prompt:" or parameters)
    prompt_end = negative_prompt_idx if negative_prompt_idx is not None else parameters_idx
    if prompt_end is not None:
        prompt_lines = lines[:prompt_end]
        structured['prompt'] = '\n'.join(prompt_lines).strip()
    elif lines:
        structured['prompt'] = '\n'.join(lines).strip()

    # Extract negative prompt (everything between "Negative prompt:" and parameters)
    if negative_prompt_idx is not None:
        neg_prompt_start = negative_prompt_idx
        neg_prompt_end = parameters_idx if parameters_idx is not None else len(lines)
        neg_prompt_lines = lines[neg_prompt_start:neg_prompt_end]
        # Remove the "Negative prompt:" prefix from the first line
        if neg_prompt_lines:
            neg_prompt_lines[0] = neg_prompt_lines[0].replace('Negative prompt:', '').strip()
        structured['negative_prompt'] = '\n'.join(neg_prompt_lines).strip()

    # Extract parameters
    if parameters_idx is not None:
        params_line = lines[parameters_idx]
        params = {}
        # Split by comma, but be careful with quoted values
        parts = []
        current_part = ""
        in_quotes = False

        for char in params_line:
            if char == '"':
                in_quotes = not in_quotes
            if char == ',' and not in_quotes:
                parts.append(current_part)
                current_part = ""
            else:
                current_part += char

        if current_part:
            parts.append(current_part)

        for part in parts:
            part = part.strip()
            if ':' in part:
                key, value = part.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Try to convert to appropriate type
                if value.isdigit():
                    params[key] = int(value)
                elif value.replace('.', '', 1).replace('-', '', 1).isdigit() and value.count('.') <= 1:
                    params[key] = float(value)
                else:
                    # Remove surrounding quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    params[key] = value

        if params:
            structured['parameters'] = params

    # Store raw metadata as well
    structured['raw'] = raw_metadata

    return structured


def extract_image_metadata(image_path: str) -> Dict[str, Any]:
    """
    Extract metadata from an image file.

    Returns a dictionary with:
    - raw: raw metadata string
    - structured: parsed structured metadata
    """
    img = Image.open(image_path)

    # Extract all metadata
    metadata = {}
    raw_parts = []

    # For PNG files, check text chunks
    if hasattr(img, 'text'):
        for key, value in img.text.items():
            metadata[key] = value
            raw_parts.append(f"{key}: {value}")

    # Also check info dict
    if hasattr(img, 'info'):
        for key, value in img.info.items():
            if key not in metadata:
                metadata[key] = value
                raw_parts.append(f"{key}: {value}")

    # Get the raw metadata string (usually in 'parameters' key for SD images)
    raw_metadata = metadata.get('parameters', '') or '\n'.join(raw_parts)

    return {
        'raw': raw_metadata,
        'metadata': metadata
    }


@click.command()
@click.option('-i', '--input', 'input_file', type=click.Path(exists=True), required=True,
              help='Input image file path')
@click.option('-t', '--txt-output', type=click.Path(), required=True,
              help='Output text file path for raw metadata')
@click.option('-j', '--json-output', type=click.Path(), required=True,
              help='Output JSON file path for structured metadata')
def extract_metadata(input_file: str, txt_output: str, json_output: str):
    """
    Extract metadata from an image file and save to text and JSON formats.

    Reads metadata from image files (primarily PNG files from Stable Diffusion)
    and outputs both raw and structured representations.

    Example:
        python -m sd_revolution.image_metadata -i input.png -t metadata.txt -j metadata.json
    """
    # Extract metadata
    result = extract_image_metadata(input_file)
    raw_metadata = result['raw']
    all_metadata = result['metadata']

    # Parse into structured format
    structured = parse_metadata_to_structured(raw_metadata)

    # Write raw metadata to text file
    with open(txt_output, 'w') as f:
        f.write(raw_metadata)

    # Write structured metadata to JSON file
    with open(json_output, 'w') as f:
        json.dump(structured, f, indent=2)

    click.echo(f"Metadata extracted successfully!")
    click.echo(f"  Raw metadata: {txt_output}")
    click.echo(f"  Structured metadata: {json_output}")
