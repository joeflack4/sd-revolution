"""Stable Diffusion Revolution"""
import glob
import os
import shutil
from datetime import datetime
from itertools import product
from pathlib import Path
from typing import List, Union

import click

# TODO: add these dirs to each set dir created: 1best, etc
# TODO: get these via config, calling dir, and/or CLI
# TODO: auto detect highest num folder
#  - assuming no folders in there already? at least none starting with integers
TXT2IMG_DATED_DIR = "D:/_Storage/Magmus/SD/SD/outputs/txt2img-images/{}/".format(datetime.today().strftime('%Y-%m-%d'))
IMGS_DIRNAME = '123 sets - dmg - parse n delete'
IMGS_DIR_PATH = TXT2IMG_DATED_DIR + IMGS_DIRNAME
# todo: sets that i haven't split yet: 38 27
# STEP_SIZE = 5
FILE_EXTS = [".png", ".jpg", ".jpeg", ".gif", ".webm", ".mp4"]  # tentative; mostly just .png
DEFAULT_MATRIXIFY = 'matrixify1_input.txt'


@click.group()
def cli():
    """todo"""
    pass


# matrixify ############################################################################################################
def process_input(input_str):
    sections = input_str.strip().split('x')
    return [section.strip().split('\n') for section in sections if section.strip()]


def generate_combinations(sections):
    if not sections:
        return []
    if len(sections) == 1:
        return [[item] for item in sections[0]]

    result = []
    for item in sections[0]:
        for combination in generate_combinations(sections[1:]):
            result.append([item] + combination)
    return result


def format_output(combinations):
    return [', '.join(combination) for combination in combinations]


@cli.command()
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


def _read_file_lines(file_path: Union[str, Path]) -> List[str]:
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]


# TODO: by default, instead of having a 4th prompt with 1 line, have the last (or first) one have 1 more prompt
@cli.command()
@click.option('-p', '--paths', type=click.Path(exists=True, dir_okay=False, readable=True), multiple=True)
@click.option('-P', '--paths-glob', type=click.Path(readable=True), default='data/input/prompts*.txt',
    help='Glob pattern for files to select. if a glob pattern is not present and a directory is passed instead, will '
         'glob everything in the immediate directory (not subfolders).')
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

    :param reverse: this way, if i primarily want to sort by the first file, and the first file e.g. has 2 prompts, the
     first half of file will be 1 prompt, 2nd half the other.
    :param and_split: if > 0, then, in addition to output_file, will create multiple promptsN.txt files, the resulting
     number of lines being the number of lines in the first file divided by and_split.
    :param paths: input files
    :param paths_glob: a glob pattern to select files. defaults to input/prompts*.txt
    :param output_file: output file

    I want help making a Python script that can make arbitrary combinations of strings of text.

    Inputs:
    - n files: This will be a list of paths to files. Each file will have 1 or more lines.

    Outputs:
    - 1 file: which is a "multiplication" of all of the lines in all of the files

    For example, if I pass 3 files, and file 1 has 10 lines, file 2 has 1 line, and file 3 has 5 lines, the resulting
    file should have 10 x 1 x 5 = 50 lines.

    Remember, there can be any number of files, and the files can have any number of lines.

    Example 1:
    Input:
    - file 1:
    ```
    abc, 123, xxx
    111, 222,
    ```

    - file 2:
    ```
    boy, tiger,
    cat, elephant,
    ```

    - file 3:
    ```
    a,
    b, 12345,
    website,
    ```

    Output:
    ```
    abc, 123, xxxboy, tiger,a,
    111, 222,boy, tiger,a,
    abc, 123, xxxcat, elephant,a,
    111, 222,cat, elephant,a,
    abc, 123, xxxboy, tiger,b, 12345,
    111, 222,boy, tiger,b, 12345,
    abc, 123, xxxcat, elephant,b, 12345,
    111, 222,cat, elephant,b, 12345,
    abc, 123, xxxboy, tiger,website,
    111, 222,boy, tiger,website,
    abc, 123, xxxcat, elephant,website,
    111, 222,cat, elephant,website,
    ```

    Example 2:
    Input:
    - file 1:
    ```
    dog cat, rope, hat,
    hello there
    ```

    - file 2:
    ```
    dolphin flying,
    ```

    - file 3:
    ```
    usagi, sailor moon,
    jinx,
    ahri, girl,
    ```

    - file 4:
    ```
    apartment,
    bedroom, bed,
    ```

    Output:
    ```
    dog cat, rope, hat,dolphin flying,usagi, sailor moon,apartment,
    hello theredolphin flying,usagi, sailor moon,apartment,
    dog cat, rope, hat,dolphin flying,jinx,apartment,
    hello theredolphin flying,jinx,apartment,
    dog cat, rope, hat,dolphin flying,ahri, girl,apartment,
    hello theredolphin flying,ahri, girl,apartment,
    dog cat, rope, hat,dolphin flying,usagi, sailor moon,bedroom, bed,
    hello theredolphin flying,usagi, sailor moon,bedroom, bed,
    dog cat, rope, hat,dolphin flying,jinx,bedroom, bed,
    hello theredolphin flying,jinx,bedroom, bed,
    dog cat, rope, hat,dolphin flying,ahri, girl,bedroom, bed,
    hello theredolphin flying,ahri, girl,bedroom, bed,
    ```
    """
    # Read files
    if not (paths or paths_glob):
        raise click.UsageError("Error: At least one input file is required.")
    elif paths and paths_glob:
        raise click.UsageError("Error: Only one of 'paths' or 'paths_glob' can be used at a time.")
    elif paths_glob:
        paths: List[str] = glob.glob(os.path.join(paths_glob, '*')) if os.path.isdir(paths_glob) \
            else glob.glob(paths_glob)
        paths = [path for path in paths if os.path.isfile(path)]
    if reverse:
        paths.reverse()
    all_lines = [_read_file_lines(file_path) for file_path in paths]
    if not all_lines:
        return

    # Combine lines
    combined_lines = [''.join(combination) for combination in product(*all_lines)]
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


# process outputs ######################################################################################################
# - utils
def _media_files_in_dir(d) -> List[str]:
    """Get files"""
    return [f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))
      and f.endswith(tuple(FILE_EXTS))]


# - label outputs
def label_outputs_via_filenames(source_dir, step_count):
    """todo"""
    print(source_dir, step_count)


def label_outputs_via_folders(source_dir: str, step_count: int):
    """todo"""
    files = _media_files_in_dir(source_dir)
    total_files = len(files)
    # Calculate the number of directories needed
    num_directories = (total_files + step_count - 1) // step_count
    for i in range(num_directories):
        # Create numbered directory
        dir_name = str(i + 1)
        os.makedirs(os.path.join(source_dir, dir_name), exist_ok=True)
        # Move files to the new directory
        start_index = i * step_count
        end_index = min((i + 1) * step_count, total_files)
        for file in files[start_index:end_index]:
            shutil.move(os.path.join(source_dir, file), os.path.join(source_dir, dir_name, file))
    print(f"Moved {total_files} files into {num_directories} directories.")


# - process outputs: main command
@cli.command()
@click.option('-s', '--step-size', type=int,  # default=STEP_SIZE,
    help='Number of images per set (batch count x batch size). If missing, will read prompts.txt in the folder, and '
    'determine the size by dividing the number of media files in the folder by the number of prompts.')
@click.option('-p', '--path', type=click.Path(exists=True), default=IMGS_DIR_PATH)
@click.option('-m', '--method', default='folders', type=click.Choice(['folders', 'files']))
def process_outputs(step_size, path, method):
    """todo"""
    # Determine step size
    if not step_size:
        prompts_file = os.path.join(path, 'prompts.txt')
        with open(prompts_file, 'r') as f:
            prompts: List[str] = f.readlines()
        files: List[str] = _media_files_in_dir(path)
        step_size = int(len(files) / len(prompts))
    # Execute
    if method == 'folders':
        label_outputs_via_folders(path, step_size)
    elif method == 'files':
        label_outputs_via_filenames(path, step_size)


if __name__ == '__main__':
    cli()
