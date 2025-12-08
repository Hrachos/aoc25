#!/usr/bin/env python3
import sys
import os
from math import sqrt

MAX_CONNECTIONS = 1000

class UnionFind:
    """Disjoint-set data structure with path compression and union by rank."""
    def __init__(self, n):
        self.parent = list(range(n))  # Each element is its own parent initially
        self.rank = [0] * n            # Track tree depth for balancing
        self.size = [1] * n            # Track component sizes

    def find(self, x):
        """Find root with path compression."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]

    def union(self, x, y):
        """Union by rank. Returns True if union happened, False if already connected."""
        root_x, root_y = self.find(x), self.find(y)

        if root_x == root_y:
            return False  # Already in same set

        # Union by rank
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
            self.size[root_y] += self.size[root_x]
        else:
            self.parent[root_y] = root_x
            self.size[root_x] += self.size[root_y]
            if self.rank[root_x] == self.rank[root_y]:
                self.rank[root_x] += 1

        return True

    def get_circuit_sizes(self):
        """Get sizes of all circuits (only counting roots)."""
        sizes = []
        for i in range(len(self.parent)):
            if self.parent[i] == i:  # Is a root
                sizes.append(self.size[i])
        return sizes

    def print_sets(self):
        """Debugging function to print all sets."""
        sets = {}
        for i in range(len(self.parent)):
            root = self.find(i)
            if root not in sets:
                sets[root] = []
            sets[root].append(i)
        for root, members in sets.items():
            print(f"Root {root}: Members {members}")

def parse_input(input_file):
    """Parse input file into list of 3D coordinates."""
    boxes = []
    for line in input_file:
        line = line.strip()
        if line:
            x, y, z = map(int, line.split(','))
            boxes.append((x, y, z))
    return boxes

def euclidean_distance(box1, box2):
    """Calculate Euclidean distance between two 3D points."""
    x1, y1, z1 = box1
    x2, y2, z2 = box2
    return sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

def part1(boxes, distances):
    """Connect 1000 closest pairs and find product of 3 largest circuits."""
    # Step 3: Initialize Union-Find
    uf = UnionFind(len(boxes))

    # Step 4: Try to connect the 1000 closest pairs
    for i, (_, box1, box2) in enumerate(distances):
        if i >= MAX_CONNECTIONS:
            break
        # Attempt union (may be redundant if already connected)
        uf.union(box1, box2)

    # Step 5: Get circuit sizes and find product of 3 largest
    circuit_sizes = uf.get_circuit_sizes()
    print(f"Number of circuits: {len(circuit_sizes)}")
    print(f"Circuit sizes: {sorted(circuit_sizes, reverse=True)[:10]}")  # Show top 10
    circuit_sizes.sort(reverse=True)

    # Product of 3 largest
    if len(circuit_sizes) < 3:
        print(f"ERROR: Only {len(circuit_sizes)} circuits found, need at least 3")
        return 0

    result = circuit_sizes[0] * circuit_sizes[1] * circuit_sizes[2]
    return result

def part2(boxes, distances):
    """Part 2 solution - to be implemented."""
    uf = UnionFind(len(boxes))

    # Step 4: Try to connect the 1000 closest pairs
    last_x_axis = -1
    second_last_x_axis = -1
    for i, (_, box1, box2) in enumerate(distances):
        if uf.union(box1, box2):
            second_last_x_axis = boxes[box1][0]
            last_x_axis = boxes[box2][0]
        if len(uf.get_circuit_sizes()) == 1:
            break
    print(f"All boxes connected at x={last_x_axis}, previous x={second_last_x_axis} ")
    return last_x_axis * second_last_x_axis

# Use example.txt as default if no stdin provided
script_dir = os.path.dirname(os.path.abspath(__file__))

if sys.stdin.isatty():
    input_file = open(os.path.join(script_dir, 'example.txt'), 'r')
else:
    input_file = sys.stdin

boxes = parse_input(input_file)
distances = []
for i in range(len(boxes)):
    for j in range(i + 1, len(boxes)):
        dist = euclidean_distance(boxes[i], boxes[j])
        distances.append((dist, i, j))

# Step 2: Sort by distance (smallest first)
distances.sort()
res1 = part1(boxes, distances)
print(f"Part 1: {res1}")

res2 = part2(boxes, distances)
print(f"Part 2: {res2}")
