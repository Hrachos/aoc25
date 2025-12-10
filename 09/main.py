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
    

    def get_rectangle_edge_points(self):
        x1, y1 = self.p1
        x2, y2 = self.p2
        edges = [
            ((x1, y1), (x2, y1)),  
            ((x2, y1), (x2, y2)),  
            ((x2, y2), (x1, y2)),  
            ((x1, y2), (x1, y1)),  
        ]
        edges_points = []
        for edge in edges:
            (ex1, ey1), (ex2, ey2) = edge
            if ex1 == ex2:  # Vertical edge
                for y in range(min(ey1, ey2), max(ey1, ey2) + 1):
                    edges_points.append((ex1, y))
            else:  # Horizontal edge
                for x in range(min(ex1, ex2), max(ex1, ex2) + 1):
                    edges_points.append((x, ey1))   
        return edges_points


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
            # Width and height include both endpoints: |x2 - x1| + 1
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

def build_rectangles(points):
    rectangles = set()
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            rect = Rectangle(points[i], points[j])
            rectangles.add(rect)
    rectangles = sorted(rectangles, key=lambda r: r.area, reverse=True)
    return rectangles


def part2(points):
    """Part 2 solution with point caching."""

    # Build polygon from points
    polygon_edges = build_polygon(points)
    rectangles = build_rectangles(points)

    # Cache for point-in-polygon test results
    invalid_points = set()  # Points known to be outside polygon
    valid_points = set()    # Points known to be inside polygon

    # Pre-populate valid_points with input points (they're on polygon boundary)
    for p in points:
        valid_points.add(p)

    print(f"Total rectangles: {len(rectangles)}")

    for i, rect in enumerate(rectangles):
        # Progress update every 100 rectangles
        # if i % 10 == 0:
        print(f"Checked {i}/{len(rectangles)} rectangles... (cache: {len(valid_points)} valid, {len(invalid_points)} invalid)")

        rect_edge_points = rect.get_rectangle_edge_points()
        valid = True

        for rp in rect_edge_points:
            # Quick rejection if we know it's invalid
            if rp in invalid_points:
                valid = False
                continue

            # Skip check if we know it's valid
            if rp in valid_points:
                continue

            # Need to test this point
            if is_point_inside_polygon(rp, polygon_edges):
                valid_points.add(rp)
            else:
                invalid_points.add(rp)
                valid = False
                continue

        # Check interior points (only if edges passed)
        for rp in rect.get_rectangle_points():
            if rp in invalid_points:
                valid = False
                continue

            if rp in valid_points:
                continue

            if is_point_inside_polygon(rp, polygon_edges):
                valid_points.add(rp)
            else:
                invalid_points.add(rp)
                valid = False

        if valid:
            print(f"Found valid rectangle with area {rect.area} using corners {rect.p1} and {rect.p2}")
            return rect.area

    return -1

script_dir = os.path.dirname(os.path.abspath(__file__))

if sys.stdin.isatty():
    input_file = open(os.path.join(script_dir, 'example.txt'), 'r')
else:
    input_file = sys.stdin

points = parse_input(input_file)

print(f"Part 1: {part1(points)}")
print(f"Part 2: {part2(points)}")
