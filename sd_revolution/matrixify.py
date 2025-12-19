"""Matrixify CLI commands"""
import glob
import os
from itertools import product
from typing import List

import click

from .utils import process_input, generate_combinations, format_output, read_file_lines


DEFAULT_MATRIXIFY = 'matrixify1_input.txt'


@click.command()
@click.argument('path', type=click.Path(exists=True), default=DEFAULT_MATRIXIFY)
def matrixify_1(path):
    """input file matrices should be delimited by 'x'. Example:
    # Example 1
    input:
    aaa
    x
    bbb
    ddd
    x
    eee

    output:
    aaa, bbb, eee
    aaa, ddd, eee

    # Example 2
    input:
    aaa
    x
    bbb
    ccc
    ddd

    output:
    aaa, bbb
    aaa, ccc
    aaa, ddd
    """
    try:
        with open(path, 'r') as f:
            input_str = f.read().strip()
    except FileNotFoundError:
        with open('../' + path, 'r') as f:
            input_str = f.read().strip()
    inputs = [input_str]
    for i, input_str in enumerate(inputs, 1):
        print(f"Batch {i}:")
        print("Input:")
        print(input_str.strip())
        print("\nOutput:")
        sections = process_input(input_str)
        combinations = generate_combinations(sections)
        output = format_output(combinations)
        for line in output:
            print(line)
        print()


# TODO: by default, instead of having a 4th prompt with 1 line, have the last (or first) one have 1 more prompt
@click.command()
@click.option('-p', '--paths', type=click.Path(exists=True, dir_okay=False, readable=True), multiple=True)
@click.option('-P', '--paths-glob', type=click.Path(readable=True), default=None,
    help='Glob pattern for files to select. if a glob pattern is not present and a directory is passed instead, will '
         'glob everything in the immediate directory (not subfolders). Defaults to "data/input/prompts*.txt" if neither -p nor -P is provided.')
@click.option('-o', '--output-file', type=click.Path(writable=True), default='data/output/prompts.txt',
              help='Output file path')
@click.option('-r', '--reverse', is_flag=True, help='Reverse the order of the input files')
@click.option('-a', '--and-split', type=int, default=0,
    help='Split the output into multiple files, each with this number of lines. The number of lines in the first file '
         'must be divisible by this number.')
def matrixify(
    paths: List[str] = None, paths_glob: str = None, output_file: str = 'data/output/prompts.txt', reverse=False,
    and_split=0
):
    """Matrixify

    Generate the Cartesian product of lines across multiple input files, concatenating
    each combination into a single output line.

    :param reverse: If True, reverse the nesting order so the first file varies slowest.
        This is useful when you want to primarily group output by the first file.
        For example, if the first file has two lines, the first half of the output
        will correspond to the first line, and the second half to the second line.
    :param and_split: If greater than 0, additionally write multiple output files
        (promptsN.txt). Each file will contain (number of lines in the first input file)
        divided by and_split.
    :param paths: Explicit list of input file paths.
    :param paths_glob: Glob pattern used to select input files.
        Defaults to "input/prompts*.txt".
    :param output_file: Path to the main output file.

    Inputs:
    - N input files, each containing one or more lines.

    Outputs:
    - A single file containing the Cartesian product of all input lines, where each
      output line is formed by concatenating one line from each input file.

    If there are N files, and file i has Li lines, the output will contain:
    L1 × L2 × ... × LN lines.

    Example 1:

    Input:
    - file 1:
        abc, 123, yyy
        111, 222,

    - file 2:
        lion, tiger,
        hippo, elephant,

    - file 3:
        a,
        b, 12345,
        c, 6789,

    Output:
        abc, 123, yyy, lion, tiger, a,
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
        111, 222, hippo, elephant, c, 6789,

    Example 2:

    Input:
    - file 1:
        dog cat, rope, hat,
        hello there

    - file 2:
        dolphin flying,

    - file 3:
        usagi, sailor moon,
        jinx,
        ahri, girl,

    - file 4:
        apartment,
        bedroom, bed,

    Output:
        dog cat, rope, hat, dolphin flying, usagi, sailor moon, apartment,
        dog cat, rope, hat, dolphin flying, usagi, sailor moon, bedroom, bed,
        dog cat, rope, hat, dolphin flying, jinx, apartment,
        dog cat, rope, hat, dolphin flying, jinx, bedroom, bed,
        dog cat, rope, hat, dolphin flying, ahri, girl, apartment,
        dog cat, rope, hat, dolphin flying, ahri, girl, bedroom, bed,
        hello there, dolphin flying, usagi, sailor moon, apartment,
        hello there, dolphin flying, usagi, sailor moon, bedroom, bed,
        hello there, dolphin flying, jinx, apartment,
        hello there, dolphin flying, jinx, bedroom, bed,
        hello there, dolphin flying, ahri, girl, apartment,
        hello there, dolphin flying, ahri, girl, bedroom, bed,
    """
    # Read files
    # Apply default if neither option was provided
    if not paths and paths_glob is None:
        paths_glob = 'data/input/prompts*.txt'

    # Validate that at least one was provided
    if not paths and not paths_glob:
        raise click.UsageError("Error: At least one input file is required.")
    # Validate that both weren't provided
    elif paths and paths_glob:
        raise click.UsageError("Error: Only one of 'paths' or 'paths_glob' can be used at a time.")

    if paths_glob:
        paths: List[str] = glob.glob(os.path.join(paths_glob, '*')) if os.path.isdir(paths_glob) \
            else glob.glob(paths_glob)
        paths = [path for path in paths if os.path.isfile(path)]
    if reverse:
        paths.reverse()
    all_lines = [read_file_lines(file_path) for file_path in paths]
    if not all_lines:
        return

    # Combine lines
    def format_combination(combination):
        """Format a combination by ensuring proper comma-space separation between parts"""
        if not combination:
            return ''
        result = []
        for i, item in enumerate(combination):
            if i < len(combination) - 1:  # Not the last item
                # Ensure this item ends with ", " for proper separation
                if item.endswith(', '):
                    result.append(item)
                elif item.endswith(','):
                    result.append(item + ' ')
                else:
                    result.append(item + ', ')
            else:
                # Last item - keep as is
                result.append(item)
        return ''.join(result)

    combined_lines = [format_combination(combination) for combination in product(*all_lines)]
    combined_lines = [x + '\n' if not x.endswith('\n') else x for x in combined_lines]

    # Write
    # todo: abstract these 3 lines to func; shared below
    combined_lines[-1] = combined_lines[-1].strip()  # remove last newline
    with open(output_file, 'w') as file:
        file.writelines(combined_lines)
    if and_split:
        lines_per_file = len(combined_lines) // and_split
        for i in range(1, and_split + 2):  # +2 to include the last file in cases of odd number of lines
            output_file_i = output_file.replace('.txt', f'{i}.txt')
            lines_i = combined_lines[(i - 1) * lines_per_file:i * lines_per_file]
            if lines_i:  # will be empty if n lines is even
                lines_i[-1] = lines_i[-1].strip()  # remove last newline
                with open(output_file_i, 'w') as file:
                    file.writelines(lines_i)
