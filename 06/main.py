#!/usr/bin/env python3
from encodings.punycode import digits
import sys

def parse_input1(input_file):
    """Parse input file, keeping lines as strings to preserve spacing."""
    lines = []
    for line in input_file:
        # Don't strip - we need to preserve spacing
        lines.append(line.rstrip('\n'))

    if not lines:
        return [], []

    # Last line contains operators
    operator_line = lines[-1]
    operators = operator_line.split()

    # All other lines are numbers
    number_lines = lines[:-1]
    numbers = [line.rstrip().split() for line in number_lines]

    return numbers, operators

def parse_input2(input_file):
    """Parse input file for part 2, respecting exact column positions."""
    lines = []
    for line in input_file:
        # Don't strip - we need to preserve spacing
        lines.append(line.rstrip('\n'))

    if not lines:
        return [], []

    # Last line contains operators at specific positions
    operator_line = lines[-1]
    number_lines = lines[:-1]
    final_numbers = []

    # Find positions of operators (non-space characters in operator line)
    operator_positions = []
    operators = []
    for i, char in enumerate(operator_line):
        if char != ' ':
            operator_positions.append(i)
            operators.append(char)
    operations = list(zip(operator_positions, operators))

    # For each operator position, read vertically to get the number
    for i in range(len(operations)):
        number_end, op = operations[i]
        next_number_end, _ = operations[i + 1] if i + 1 < len(operations) else (len(operator_line), None)
        number_start = next_number_end - 1 if i + 1 < len(operations) else len(operator_line)
        # print(f"Operator '{op}' at column {number_end}, reading numbers from column {number_start} to {number_end}")
        # Read numbers from this column range (pos to number_end), going right-to-left
        numbers = []
        for index in range(number_start -1, number_end - 1, -1):
            # print(f"Reading numbers from column {index}")
            digits = []
            column_numbers = []
            for i in range(len(number_lines)):
                line = number_lines[i]
                # Read the range backwards (right to left) to build the number
                if line[index] != ' ':
                    digits.append(line[index])
                else:
                    continue
            for i in range(len(digits) - 1, -1, -1):
                print(f"Digit found: {digits[i]} at position {i}")
                column_numbers.append(int(digits[i]) * (10 ** (len(digits) - 1 - i)))
            numbers.append(sum(column_numbers))
        final_numbers.append(numbers)
    print(f"Final numbers: {final_numbers}, operators: {operators}")
    return final_numbers, operators

def part1(numbers, operators):
    """Parse vertical math problems and calculate grand total."""
    grand_total = 0

    # numbers is a list of rows, we need to transpose to get columns
    # Each column is one problem
    num_problems = len(operators)

    for col_idx in range(num_problems):
        # Extract all numbers in this column (going down the rows)
        column_numbers = []
        for row in numbers:
            if col_idx < len(row):
                column_numbers.append(int(row[col_idx]))

        # Apply the operator for this column
        operator = operators[col_idx]

        if operator == '+':
            result = sum(column_numbers)
        elif operator == '*':
            result = 1
            for num in column_numbers:
                result *= num
        else:
            result = 0

        print(f"Problem {col_idx + 1}: {' '.join(map(str, column_numbers))} {operator} = {result}")
        grand_total += result

    return grand_total

def part2(problems):
    """Calculate result treating each operator position as a single multi-digit number."""
    if not problems:
        return 0


    grand_total = 0
    for column_numbers, operator in problems:
        if operator == '+':
            result = sum(column_numbers)
        elif operator == '*':
            result = 1
            for num in column_numbers:
                result *= num
        else:
            result = 0

        print(f"Problem: {' '.join(map(str, column_numbers))} {operator} = {result}")
        grand_total += result

    return grand_total

# Use example.txt as default if no stdin provided
import os
script_dir = os.path.dirname(os.path.abspath(__file__))

if sys.stdin.isatty():
    input_file = open(os.path.join(script_dir, 'example.txt'), 'r')
else:
    input_file = sys.stdin

# numbers, operators = parse_input1(input_file)
# print(f"Part 1: {part1(numbers, operators)}")

# Re-open file for part 2 since we already consumed it
if sys.stdin.isatty():
    input_file2 = open(os.path.join(script_dir, 'example.txt'), 'r')
else:
    # For stdin, we'd need to store the content or re-read
    input_file2 = input_file

# numbers, operators = parse_input1(input_file)
# print(f"Part 1: {part1(numbers, operators)}")
numbers, operators = parse_input2(input_file2)
print(f"Part 2: {part2(zip(numbers, operators))}")
