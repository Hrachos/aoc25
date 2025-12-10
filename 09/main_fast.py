#!/usr/bin/env python3

import sys
import os

class Rectangle:
    def __init__(self, p1, p2):
        self.p1 = p1  # (x1, y1)
        self.p2 = p2  # (x2, y2)

    @property
    def area(self):
        width = abs(self.p2[0] - self.p1[0]) + 1
        height = abs(self.p2[1] - self.p1[1]) + 1
        return width * height

    def get_rectangle_points(self):
        x1, y1 = self.p1
        x2, y2 = self.p2
        points = []
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                points.append((x, y))
        return points

def parse_input(input_file):
    """Parse input file into list of 2D coordinates."""
    points = []
    for line in input_file:
        line = line.strip()
        if line:
            x, y = map(int, line.split(','))
            points.append((x, y))
    return points

def part1(points):
    """Find the largest rectangle using given points as opposite corners."""
    max_area = 0
    best_corners = None

    # Try all pairs of points as opposite corners
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            x1, y1 = points[i]
            x2, y2 = points[j]

            # Calculate rectangle area (inclusive of corner points)
            width = abs(x2 - x1) + 1
            height = abs(y2 - y1) + 1
            area = width * height

            if area > max_area:
                max_area = area
                best_corners = (points[i], points[j])

    print(f"Largest rectangle area: {max_area}")
    if best_corners:
        print(f"Opposite corners: {best_corners[0]} and {best_corners[1]}")

    return max_area

def build_polygon(points):
    edges = []
    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)]  # Wrap around
        edges.append((p1, p2))
    return edges

def is_point_on_edge(point, edges):
    for edge in edges:
        if is_point_on_line_segment(point, edge):
            return True
    return False

def is_point_on_line_segment(point, line_segment):
    (x1, y1), (x2, y2) = line_segment
    (px, py) = point

    # Check if point is within bounding box of edge
    if min(x1, x2) <= px <= max(x1, x2) and min(y1, y2) <= py <= max(y1, y2):
        # Check collinearity using cross product
        return (y2 - y1) * (px - x1) == (x2 - x1) * (py - y1)
    return False

def is_point_inside_polygon(point, polygon_edges):
    if is_point_on_edge(point, polygon_edges):
        return True  # On edge is considered inside

    # Ray-casting algorithm to check if point is inside polygon
    x_intersections = 0
    for edge in polygon_edges:
        if does_ray_intersect_segment(point, edge):
            x_intersections += 1

    return x_intersections % 2 == 1  # Inside if odd number of intersections

def does_ray_intersect_segment(point, line_segment):
    (x1, y1), (x2, y2) = line_segment
    (px, py) = point

    if y1 > y2:
        x1, y1, x2, y2 = x2, y2, x1, y1

    if py == y1 or py == y2:
        py += 0.1  # Slightly adjust point to avoid ambiguity

    if py < y1 or py > y2:
        return False

    if x1 == x2:  # Vertical line
        return px <= x1

    # Calculate intersection point
    slope = (y2 - y1) / (x2 - x1)
    x_intersect = x1 + (py - y1) / slope

    return px <= x_intersect

def precompute_valid_points_scanline(points, polygon_edges):
    """Pre-compute all points using scanline algorithm (optimized for rectilinear polygons)."""
    print("Pre-computing valid points using scanline algorithm...")

    # Find bounding box
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)

    print(f"Polygon bounding box: ({min_x}, {min_y}) to ({max_x}, {max_y})")
    print(f"Scanlines to process: {max_y - min_y + 1}")

    # Pre-build edge lookup by y-coordinate for MASSIVE speedup
    # Map: y -> list of edges that intersect this y-coordinate
    from collections import defaultdict
    horizontal_edges_by_y = defaultdict(list)  # y -> [(x_start, x_end), ...]
    vertical_edges_by_y = defaultdict(list)    # y -> [x, x, x, ...]

    print("Building edge lookup maps...")
    for (x1, y1), (x2, y2) in polygon_edges:
        if y1 == y2:
            # Horizontal edge
            horizontal_edges_by_y[y1].append((min(x1, x2), max(x1, x2)))
        elif x1 == x2:
            # Vertical edge - add to all y-coordinates it spans
            y_min, y_max = min(y1, y2), max(y1, y2)
            for y in range(y_min, y_max + 1):
                # Only add as transition point if not at top endpoint
                if y == y_min or y_min < y < y_max:
                    vertical_edges_by_y[y].append(x1)

    print("Edge maps built. Processing scanlines...")
    # Store intervals instead of individual points!
    valid_intervals = {}  # y -> [(x_start, x_end), ...]

    # Process each scanline (horizontal line at y-coordinate)
    for y in range(min_y, max_y + 1):
        if (y - min_y) % 1000 == 0:
            print(f"Processing scanline {y - min_y}/{max_y - min_y + 1}...")

        # Get pre-filtered edges for this scanline (O(1) lookup!)
        horizontal_ranges = horizontal_edges_by_y.get(y, [])
        vertical_x = sorted(vertical_edges_by_y.get(y, []))

        intervals = []

        # Add horizontal ranges (these are ON the polygon boundary)
        intervals.extend(horizontal_ranges)

        # Add interior ranges between vertical edge transitions
        # Use pairs of vertical_x to determine inside/outside
        i = 0
        while i < len(vertical_x) - 1:
            x_start = vertical_x[i]
            x_end = vertical_x[i + 1]
            intervals.append((x_start, x_end))
            i += 2  # Move to next pair (outside -> inside -> outside)

        # Merge overlapping intervals for efficiency
        if intervals:
            intervals.sort()
            merged = [intervals[0]]
            for x_start, x_end in intervals[1:]:
                if x_start <= merged[-1][1] + 1:
                    # Overlapping or adjacent - merge
                    merged[-1] = (merged[-1][0], max(merged[-1][1], x_end))
                else:
                    merged.append((x_start, x_end))
            valid_intervals[y] = merged

    total_points = sum((x_end - x_start + 1) for intervals in valid_intervals.values()
                      for x_start, x_end in intervals)
    print(f"Scanline pre-computation complete! {len(valid_intervals)} y-coordinates with intervals")
    print(f"Total valid points: {total_points}")
    return valid_intervals

def build_rectangles(points):
    rectangles = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            rect = Rectangle(points[i], points[j])
            rectangles.append(rect)
    # Sort by area descending (largest first)
    rectangles.sort(key=lambda r: r.area, reverse=True)
    return rectangles

def is_point_in_intervals(x, y, valid_intervals):
    """Check if point (x,y) is in any valid interval for that y-coordinate."""
    intervals = valid_intervals.get(y)
    if not intervals:
        return False
    # Binary search would be faster, but linear is fine for small interval counts
    for x_start, x_end in intervals:
        if x_start <= x <= x_end:
            return True
    return False

def is_rectangle_valid(rect, valid_intervals):
    """Check if entire rectangle falls within valid intervals (FAST!)."""
    x1, y1 = rect.p1
    x2, y2 = rect.p2
    min_x, max_x = min(x1, x2), max(x1, x2)
    min_y, max_y = min(y1, y2), max(y1, y2)

    # Check each y-coordinate of the rectangle
    for y in range(min_y, max_y + 1):
        intervals = valid_intervals.get(y)
        if not intervals:
            return False  # This y-row has no valid intervals

        # Check if the rectangle's x-range [min_x, max_x] is fully covered
        # The rectangle is valid if its full x-range falls within valid intervals
        covered = False
        for x_start, x_end in intervals:
            if x_start <= min_x and max_x <= x_end:
                # Entire rectangle width is covered by this interval
                covered = True
                break

        if not covered:
            return False  # This row isn't fully covered

    return True

def part2(points):
    """Part 2 solution with interval-based validation (MUCH FASTER!)."""

    # Build polygon from points
    polygon_edges = build_polygon(points)

    # Pre-compute valid intervals (ONE TIME COST)
    valid_intervals = precompute_valid_points_scanline(points, polygon_edges)

    # Build rectangles sorted by area
    rectangles = build_rectangles(points)
    print(f"\nTotal rectangles to check: {len(rectangles)}")

    # Check rectangles (SUPER FAST with interval checking)
    for i, rect in enumerate(rectangles):
        if i % 1000 == 0 and i > 0:
            print(f"Checked {i}/{len(rectangles)} rectangles...")

        if is_rectangle_valid(rect, valid_intervals):
            print(f"\nFound valid rectangle with area {rect.area} using corners {rect.p1} and {rect.p2}")
            return rect.area

    return -1

script_dir = os.path.dirname(os.path.abspath(__file__))

if sys.stdin.isatty():
    input_file = open(os.path.join(script_dir, 'example.txt'), 'r')
else:
    input_file = sys.stdin

points = parse_input(input_file)

print(f"Part 1: {part1(points)}")
print(f"\n{'='*60}")
print(f"Part 2: {part2(points)}")
