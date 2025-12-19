"""Stable Diffusion Revolution"""
import os
import shutil
from datetime import datetime
from typing import List

import click

from .matrixify import matrixify, matrixify_1
from .image_metadata import extract_metadata

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


@click.group()
def cli():
    """todo"""
    pass


# Register matrixify commands
cli.add_command(matrixify)
cli.add_command(matrixify_1)

# Register image metadata command
cli.add_command(extract_metadata)


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
