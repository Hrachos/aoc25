#!/usr/bin/env python3
import sys

def nearest8(grid: list[list[str]], coordinates: tuple[int, int]) -> bool:
    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),          (0, 1),
              (1, -1),  (1, 0), (1, 1)]
    # neighbors = []
    r, c = coordinates
    rolls = 0
    for dr, dc in deltas:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            if grid[nr][nc] == '@':
                rolls += 1
    return rolls <= 3 

def part1(grid: list[list[str]]) -> int:
    res = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '.':
                continue
            if nearest8(grid, (r, c)):
                # print(f"Cell ({r}, {c}) is accessible")
                res += 1
    return res

def part2(grid: list[list[str]]):
    one_accessible = True
    res = 0
    while one_accessible:
        one_accessible = False
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == '.':
                    continue
                if nearest8(grid, (r, c)):
                    one_accessible = True
                    res += 1
                    grid[r][c] = '.'
    return res



if sys.stdin.isatty():
    input_file = open('example.txt', 'r')
else:
    input_file = sys.stdin

# Read as a 2D grid for easy traversal
grid = [list(line.strip()) for line in input_file]
# Grid dimensions
rows = len(grid)
cols = len(grid[0]) if rows > 0 else 0

print(f"Grid size: {rows}x{cols}")
res1 = part1(grid)
print(f"Final result part 1: {res1}")
res2 = part2(grid)
print(f"Final result part 2: {res2}")

