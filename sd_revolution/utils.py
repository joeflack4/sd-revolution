"""Utility functions for SD Revolution"""
from pathlib import Path
from typing import List, Union


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


def read_file_lines(file_path: Union[str, Path]) -> List[str]:
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]
