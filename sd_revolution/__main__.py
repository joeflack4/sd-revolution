# :) Stable Diffusion Revolution CLI
"""Stable Diffusion Revolution"""
import os
import shutil

import click

# TODO: add these dirs to each set dir created: 1best, etc
# TODO: get these via config, calling dir, and/or CLI
# TODO: auto detect highest num folder
#  - assuming no folders in there already? at least none starting with integers
TXT2IMG_DATED_DIR = "D:/_Storage/Magmus/SD/SD/outputs/txt2img-images/2024-07-26/"
IMGS_DIRNAME = 'frieren 1 powder125.iter15rep frieren - parse'
IMGS_DIR = TXT2IMG_DATED_DIR + IMGS_DIRNAME
# todo: sets that i haven't split yet: 38 27
STEP_SIZE = 5
FILE_EXTS = [".png", ".jpg", ".jpeg", ".gif", ".webm", ".mp4"]  # tentative; mostly just .png


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
@click.argument('path', type=click.Path(exists=True))
def matrixify(path):
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
    print('matrixify')
    INPUT_FILE = 'matrixify_input.txt'
    try:
        with open(INPUT_FILE, 'r') as f:
            input_str = f.read().strip()
    except FileNotFoundError:
        with open('../' + INPUT_FILE, 'r') as f:
            input_str = f.read().strip()
    inputs = [input_str]
    # for i, input_str in enumerate(inputs, 1):
    #     print(f"Batch {i}:")
    #     print("Input:")
    #     print(input_str.strip())
    #     print("\nOutput:")
    #     sections = process_input(input_str)
    #     combinations = generate_combinations(sections)
    #     output = format_output(combinations)
    #     for line in output:
    #         print(line)
    #     print()


# process outputs ######################################################################################################
# - label outputs
def label_outputs_via_filenames(source_dir, step_count):
    """todo"""
    pass

def label_outputs_via_folders(source_dir, step_count):
    # Get all files in the source directory
    # todo: would this tuple thing have worked?
    # files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))
    #   and f.endswith(tuple(FILE_EXTS))]
    files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f)) and
        any([f.endswith(ext) for ext in FILE_EXTS])]
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
@click.option('--step-size', type=int, required=True, help='Number of images per set (batch count x batch size')
@click.argument('path', type=click.Path(exists=True))
def process_outputs(step_size, path):
    """todo"""
    print('process outputs')
    # batch_move_files(IMGS_DIR, STEP_SIZE)


if __name__ == '__main__':
    cli()