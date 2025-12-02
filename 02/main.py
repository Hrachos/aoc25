#!/usr/bin/env python3
import sys
from typing import assert_type

def isRepeating(s: str, n: str) -> bool:
    assert_type(s, str)
    assert_type(n, str)
    if len(s) == 0:
        return False
    if len(n) % len(s) != 0:
        return False

    for i in range(0, len(n), len(s)):
        if n[i:i+len(s)] != s:
            return False
    return True


def find_occurences(n: int) -> int:
    s = str(n)
    mid = len(s) // 2
    for i in range(1, mid + 1):
        if isRepeating(s[:i], s):
            return n
    return 0
            

def find_duplicates(n: int) -> int:
    s = str(n)
    mid = len(s) // 2
    if s[:mid] == s[mid:]:
        return n
    else:
        return 0


if sys.stdin.isatty():
    input_file = open('example.txt', 'r')
else:
    input_file = sys.stdin

line = input_file.read().strip()
ranges = []

for range_str in line.split(','):
    start, end = range_str.split('-')
    ranges.append((int(start), int(end)))

res = 0
for start, end in ranges:
    for i in range(start, end + 1):
        # if len(str(i)) % 2 != 0:
        #     continue
        # res += find_duplicates(i)
        res += find_occurences(i)

print(f"Final result: {res}")
