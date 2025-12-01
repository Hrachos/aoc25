#!/usr/bin/env python3
import sys

STARTING_VALUE = 50
MODULO_VALUE = 100

# Use example.txt as default if no stdin provided
if sys.stdin.isatty():
    input_file = open('example.txt', 'r')
else:
    input_file = sys.stdin

dial = STARTING_VALUE
result = 0

for line in input_file:
    line = line.strip()
    if not line:
        continue

    if line.startswith('L'):
        value = int(line[1:])
        # Count how many full rotations (wraps around 0)
        result += value // MODULO_VALUE
        # Reduce value to single rotation
        value = value % MODULO_VALUE
        # Check if this operation crosses 0
        if dial != 0 and value >= dial:
            result += 1
        dial = (dial - value) % MODULO_VALUE

    elif line.startswith('R'):
        value = int(line[1:])
        # Count how many times we pass 0 going right
        result += (dial + value) // MODULO_VALUE
        dial = (dial + value) % MODULO_VALUE

print(f"Final dial value: {dial}")
print(f"Final result: {result}")
