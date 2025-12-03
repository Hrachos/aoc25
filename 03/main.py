#!/usr/bin/env python3
import sys
from typing import assert_type

def find_highest_n_digits(line: str, remaining_digits: int, start: int = 0) -> str:
    """
    Find the highest remaining_digits-digit number from line[start:] while keeping order.
    Ensures we never run out of digits to choose from.
    """
    if remaining_digits == 0:
        return ""

    # Calculate the search space: we need at least remaining_digits digits remaining
    # So we can search from start to (len(line) - remaining_digits)
    search_end = len(line) - remaining_digits + 1

    if start >= search_end:
        return ""

    # Find the highest digit in the valid search space
    highest_digit = -1
    highest_index = -1

    for i in range(start, search_end):
        if line[i].isdigit():
            digit = int(line[i])
            if digit > highest_digit:
                highest_digit = digit
                highest_index = i

    if highest_index == -1:
        return ""

    # Recursively find the remaining (remaining_digits-1) digits starting after this position
    return str(highest_digit) + find_highest_n_digits(line, remaining_digits - 1, highest_index + 1)


def part1(lines: list[str]) -> int:
    res = 0
    for line in lines:
        highest_digit = max((int(char) for char in line[0:len(line)-1] if char.isdigit()), default=-1)
        highest_digit_index = max((i for i, char in enumerate(line[0:len(line)-1]) if char.isdigit()), key=lambda i: int(line[i]), default=-1)
        highest_digit_in_the_rest = max((int(char) for char in line[highest_digit_index+1:len(line)] if char.isdigit()), default=-1)
        res += highest_digit*10 + highest_digit_in_the_rest
    return res

def part2(lines: list[str]) -> int:
    res = 0
    for line in lines:
        highest_12_digit = find_highest_n_digits(line, 12)
        if highest_12_digit:
            res += int(highest_12_digit)
    return res


if sys.stdin.isatty():
    input_file = open('example.txt', 'r')
else:
    input_file = sys.stdin

lines = [line.strip() for line in input_file]
res = 0


res1 = part1(lines)
res2 = part2(lines)
print(f"Final result part 1: {res1}")
print(f"Final result part 2: {res2}")
