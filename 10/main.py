#!/usr/bin/env python3

import sys
import os
import heapq
import numpy as np
import scipy.optimize

from collections import deque

class Machine:
    def __init__(self):
        self.lights: list[bool] = []
        self.buttons: list[list[int]] = []
        self.joltage: list[int] = []

    def print_machine(self):
        print("Lights:")
        for i, light in enumerate(self.lights):
            print(f"  Light {i}: {'#' if light else '.'}")
        print("Buttons:")
        for i, button in enumerate(self.buttons):
            print(f"  Button {i}: {button}")
        print("Joltage:")
        print(f"  {self.joltage}")


def parse_input(input_data) -> list[Machine]:
    machines: list[Machine] = []
    for i, line in enumerate(input_data.strip().splitlines()):
        machine = Machine()
        for element in line.split(' '):
            if element[0] == '[' and element[-1] == ']':
                for char in element[1:-1]:
                    machine.lights.append(char == '#')
            elif element[0] == '(' and element[-1] == ')':
                button_values = list(map(int, element[1:-1].split(',')))
                machine.buttons.append(button_values)
            elif element[0] == '{' and element[-1] == '}':
                machine.joltage = list(map(int, element[1:-1].split(',')))
        machines.append(machine)
    return machines

def calculate_light_score(lights: list[bool], machine: Machine) -> int:
    score = 0
    for i, light in enumerate(machine.lights):
        if lights[i] == light:
            score += 1
    return score

def apply_button_lights(lights: list[bool], button: list[int]) -> list[bool]:
    """Apply a button press to the lights state."""
    new_lights = lights.copy()
    for index in button:
        new_lights[index] = not new_lights[index]
    return new_lights

def apply_button_joltage(joltage: list[int], button: list[int]) -> list[int]:
    """Apply a button press to the joltage state."""
    new_joltage = joltage.copy()
    for index in button:
        new_joltage[index] += 1
    return new_joltage

def solve_lights(machine: Machine) -> int:
    """Find minimum button presses using BFS."""

    target = tuple(machine.lights)
    start = tuple([False] * len(machine.lights))

    if start == target:
        return 0

    # BFS to find shortest path
    queue = deque([(start, 0)])  # (state, presses)
    visited = {start}

    while queue:
        current_state, presses = queue.popleft()

        # Try pressing each button
        for button in machine.buttons:
            new_state = tuple(apply_button_lights(list(current_state), button))

            if new_state == target:
                return presses + 1

            if new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, presses + 1))

    # No solution found
    return -1

def a_star_manhattan(current: tuple[int,...], target: tuple[int,...]) -> int:
    """Heuristic for A* search: sum of differences."""
    return sum(abs(c - t) for c, t in zip(current, target))

def a_star_button_presses(current: tuple[int,...], target: tuple[int,...], buttons: list[list[int]]) -> int:
    """Heuristic for A* search: minimum button presses needed (not admissible)."""
    diff = [t - c for c, t in zip(current, target)]
    presses = 0
    for button in buttons:
        min_increase = min(diff[i] for i in button)
        if min_increase > 0:
            presses += min_increase
            for i in button:
                diff[i] -= min_increase
    return presses

def solve_joltage_bfs_pruned(machine: Machine) -> int:
    """BFS with aggressive pruning - only keep states on the Pareto frontier."""
    target = tuple(machine.joltage)
    start = tuple([0] * len(machine.joltage))

    if start == target:
        return 0

    # Use deque for BFS
    from collections import deque
    queue = deque([(start, 0)])  # (state, presses)

    # Track best cost to reach each state
    best_cost = {start: 0}

    while queue:
        current_state, presses = queue.popleft()

        # Skip if we've found a better path to this state
        if presses > best_cost.get(current_state, float('inf')):
            continue

        # Check if we reached target
        if current_state == target:
            return presses

        # Try each button
        for button in machine.buttons:
            new_state = list(current_state)

            # Apply button (increment indices)
            for idx in button:
                new_state[idx] += 1

            new_state = tuple(new_state)

            # Aggressive pruning: skip if any index overshoots
            if any(s > t for s, t in zip(new_state, target)):
                continue

            new_presses = presses + 1

            # Only explore if we found a better path
            if new_presses < best_cost.get(new_state, float('inf')):
                best_cost[new_state] = new_presses
                queue.append((new_state, new_presses))

    return -1

def solve_joltage_scipy(machine: Machine) -> int:
    """Solve joltage problem using integer linear programming.

    This is a system of linear equations:
    - Variables: x[i] = number of times to press button i
    - Constraints: Sum of button presses must equal target joltage for each index
    - Objective: Minimize total button presses (sum of all x[i])
    """
    target = np.array(machine.joltage)
    num_buttons = len(machine.buttons)
    num_indices = len(target)

    # Build constraint matrix A where A[i][j] = 1 if button j affects index i
    A_eq = np.zeros((num_indices, num_buttons))
    for button_idx, button in enumerate(machine.buttons):
        for affected_idx in button:
            A_eq[affected_idx][button_idx] = 1

    # Objective: minimize sum of button presses (all coefficients are 1)
    c = np.ones(num_buttons)

    # Bounds: each button press count must be >= 0
    bounds = [(0, None) for _ in range(num_buttons)]

    # Solve using linear programming
    result = scipy.optimize.linprog(
        c=c,              # Minimize sum of button presses
        A_eq=A_eq,        # Equality constraints matrix
        b_eq=target,      # Target joltage values
        bounds=bounds,    # Non-negative button presses
        method='highs'    # Use HiGHS solver (fastest)
    )

    if not result.success:
        return -1

    # Round solution to nearest integer (LP gives float solutions)
    # For integer solutions, we should use integer programming, but rounding works if solution is close
    button_presses = np.round(result.x).astype(int)

    # Verify the solution is correct
    achieved = np.zeros(num_indices, dtype=int)
    for button_idx, presses in enumerate(button_presses):
        for affected_idx in machine.buttons[button_idx]:
            achieved[affected_idx] += presses

    if not np.array_equal(achieved, target):
        # LP solution didn't round correctly, need integer programming
        # Fall back to MILP (Mixed Integer Linear Programming)
        result = scipy.optimize.milp(
            c=c,
            constraints=scipy.optimize.LinearConstraint(A_eq, target, target),
            bounds=scipy.optimize.Bounds(0, np.inf),
            integrality=np.ones(num_buttons)  # All variables must be integers
        )

        if not result.success:
            return -1

        button_presses = result.x.astype(int)

    return int(np.sum(button_presses))


def part1(machines: list[Machine]) -> int:
    res = 0
    for machine in machines:
        res += solve_lights(machine)
    return res
    
def part2(machines: list[Machine]) -> int:
    res = 0
    for i, machine in enumerate(machines):
        result = solve_joltage_scipy(machine)
        res += result
        print(f"Joltage for machine {i} solved with result {res}")
    return res

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    if sys.stdin.isatty():
        input_file = open(os.path.join(script_dir, 'example.txt'), 'r')
    else:
        input_file = sys.stdin

    input_data = input_file.read()
    machines = parse_input(input_data)
    # for i, machine in enumerate(machines):
    #     print(f"Machine {i}:")
    #     machine.print_machine()

    print(f"Part 1: {part1(machines)}")
    print(f"Part 2: {part2(machines)}")


if __name__ == "__main__":
    main()
