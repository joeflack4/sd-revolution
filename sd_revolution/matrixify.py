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
INPUT_FILE = 'matrixify_input.txt'
try:
    with open(INPUT_FILE, 'r') as f:
        input_str = f.read().strip()
except FileNotFoundError:
    with open('../' + INPUT_FILE, 'r') as f:
        input_str = f.read().strip()
inputs = [input_str]


###


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