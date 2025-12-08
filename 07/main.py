#!/usr/bin/env python3
import sys
import os

def parse_input(input_file):
    """Parse input file into a grid."""
    grid = []
    for line in input_file:
        grid.append(line.rstrip('\n'))
    return grid

def part1(grid):
    """Count how many times the beam is split."""
    # Find starting position S in the first row
    start_col = -1
    if grid:
        start_col = grid[0].find('S')

    if start_col == -1:
        print("No starting position 'S' found!")
        return 0

    print(f"Starting position: row=0, col={start_col}")

    split_count = 0
    beams = {start_col}  # Set of column positions where beams are currently

    for row in grid[1:]:
        for beam in beams.copy():
            if row[beam] == '.':
                continue  # Beam continues straight
            elif row[beam] == '^':
                split_count += 1
                beams.add(beam - 1)  # New beam to the left
                beams.add(beam + 1)  # New beam to the right
                beams.remove(beam)    # Original beam is split
    return split_count

def part2(grid):
    """Count unique paths from S to the bottom row."""
    # Find starting position S in the first row
    start_col = -1
    if grid:
        start_col = grid[0].find('S')

    if start_col == -1:
        return 0

    # Use dynamic programming: paths[row][col] = number of paths to reach (row, col)
    # We'll build this row by row from top to bottom

    # Initialize: one path to the starting position
    current_paths = {start_col: 1}

    for row_idx, row in enumerate(grid[1:], start=1):
        next_paths = {}

        for col, path_count in current_paths.items():
            if col >= len(row):
                continue

            cell = row[col]

            if cell == '.':
                # Beam continues straight down
                next_paths[col] = next_paths.get(col, 0) + path_count
            elif cell == '^':
                # Beam splits into left and right
                left_col = col - 1
                right_col = col + 1

                if left_col >= 0:
                    next_paths[left_col] = next_paths.get(left_col, 0) + path_count
                if right_col < len(row):
                    next_paths[right_col] = next_paths.get(right_col, 0) + path_count

        current_paths = next_paths

    # Sum all paths that reached the bottom row
    total_paths = sum(current_paths.values())
    return total_paths

# Use example.txt as default if no stdin provided
script_dir = os.path.dirname(os.path.abspath(__file__))

if sys.stdin.isatty():
    input_file = open(os.path.join(script_dir, 'example.txt'), 'r')
else:
    input_file = sys.stdin

grid = parse_input(input_file)
print(f"Grid loaded: {len(grid)} rows")
if grid:
    print(f"First row: '{grid[0]}'")

print(f"Part 1: {part1(grid)}")
print(f"Part 2: {part2(grid)}")
