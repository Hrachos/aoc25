#!/usr/bin/env python3
import sys

def parse_input(input_file):
    """Parse input file into ranges and IDs to check."""
    ranges = []
    ids_to_check = []
    reading_ranges = True

    for line in input_file:
        line = line.strip()

        if not line:
            reading_ranges = False
            continue

        if reading_ranges:
            # Parse range like "3-5"
            start, end = map(int, line.split('-'))
            ranges.append((start, end))
        else:
            # Parse individual IDs
            ids_to_check.append(int(line))

    return ranges, ids_to_check

def part1(ranges, ids_to_check):
    """Count how many IDs fall within any of the fresh ranges."""
    fresh_count = 0
    for id_num in ids_to_check:
        is_fresh = False
        for start, end in ranges:
            if start <= id_num <= end:
                is_fresh = True
                break
        if is_fresh:
            fresh_count += 1

    return fresh_count

def part2(ranges):
    """Calculate total coverage by merging overlapping ranges."""
    if not ranges:
        return 0

    # Merge overlapping or adjacent ranges
    merged = [ranges[0]]

    for current_start, current_end in ranges[1:]:
        last_start, last_end = merged[-1]

        # Check if current range overlaps or is adjacent to last merged range
        if current_start <= last_end + 1:
            # Merge by extending the end if needed
            merged[-1] = (last_start, max(last_end, current_end))
        else:
            # No overlap, add as new range
            merged.append((current_start, current_end))

    # Calculate total coverage
    total = 0
    for start, end in merged:
        total += end - start + 1  # +1 because ranges are inclusive

    return total

# Use example.txt as default if no stdin provided
if sys.stdin.isatty():
    input_file = open('example.txt', 'r')
else:
    input_file = sys.stdin

ranges, ids_to_check = parse_input(input_file)
ranges.sort(
    key=lambda x: x[0]
)

print(f"Part 1: {part1(ranges, ids_to_check)}")
print(f"Part 2: {part2(ranges)}")
