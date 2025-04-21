import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

def format_label(a1, a2, b=None, is_objective=False):
    """
    Format the label dynamically based on coefficients.
    """
    terms = []
    if a1 != 0:
        terms.append(f"{'' if a1 == 1 else a1}x")
    if a2 != 0:
        terms.append(f"{'' if a2 == 1 else a2}y")
    if is_objective:
        return f"{' + '.join(terms)}"
    return f"{' + '.join(terms)} <= {b}"


def find_intersection(constraint1, constraint2):
    """
    Find the intersection point of two constraints.
    """
    a1, a2, b1 = constraint1
    c1, c2, b2 = constraint2

    determinant = a1 * c2 - a2 * c1
    if determinant == 0:
        return None  # Parallel lines, no intersection

    x = (b1 * c2 - b2 * a2) / determinant
    y = (a1 * b2 - c1 * b1) / determinant
    return (x, y)


def is_feasible(point, constraints):
    """
    Check if a point satisfies all constraints.
    """
    x, y = point
    if x < 0 or y < 0:  # Ensure the point is in the first quadrant
        return False
    for a1, a2, b in constraints:
        if a1 * x + a2 * y > b:
            return False
    return True


def calculate_dynamic_range(intersection_points):
    """
    Calculate dynamic x_range and y_range based on intersection points.
    """
    x_values = [p[0] for p in intersection_points if p[0] >= 0]
    y_values = [p[1] for p in intersection_points if p[1] >= 0]

    x_min, x_max = 0, max(x_values) * 1.2 if x_values else 10
    y_min, y_max = 0, max(y_values) * 1.2 if y_values else 10

    return (x_min, x_max), (y_min, y_max)


def solve_graphically(objective, constraints):
    """
    Solve a 2-variable linear programming problem graphically.
    """
    # Find all intersection points
    intersection_points = []
    for constraint1, constraint2 in combinations(constraints, 2):
        point = find_intersection(constraint1, constraint2)
        if point is not None and is_feasible(point, constraints):
            intersection_points.append(point)

    # Add boundary points (x=0 and y=0 intersections)
    for a1, a2, b in constraints:
        if a1 != 0:  # Intersection with y-axis (x=0)
            y = b / a2 if a2 != 0 else None
            if y is not None and y >= 0:
                intersection_points.append((0, y))
        if a2 != 0:  # Intersection with x-axis (y=0)
            x = b / a1 if a1 != 0 else None
            if x is not None and x >= 0:
                intersection_points.append((x, 0))

    # Calculate dynamic range
    x_range, y_range = calculate_dynamic_range(intersection_points)
    x = np.linspace(x_range[0], x_range[1], 400)

    plt.figure(figsize=(8, 8))

    # Plot constraints
    for a1, a2, b in constraints:
        label = format_label(a1, a2, b)
        if a2 != 0:
            y = (b - a1 * x) / a2
            plt.plot(x, y, label=label)
        else:
            plt.axvline(x=b / a1, label=label)

    # Sort intersection points to form a polygon for the feasible region
    feasible_polygon = [point for point in intersection_points if is_feasible(point, constraints)]
    feasible_polygon = sorted(feasible_polygon, key=lambda p: (p[0], p[1]))

    # Shade feasible region
    if len(feasible_polygon) > 2:
        polygon_x, polygon_y = zip(*feasible_polygon)
        plt.fill(polygon_x, polygon_y, color='gray', alpha=0.3, label="Feasible Region")

    # Find the optimal point
    c1, c2 = objective
    optimal_point = None
    optimal_value = float('-inf')
    for point in feasible_polygon:
        x, y = point
        value = c1 * x + c2 * y
        if value > optimal_value:
            optimal_value = value
            optimal_point = point

    # Highlight the optimal point
    if optimal_point:
        plt.scatter(*optimal_point, color='red', zorder=5, label=f"Optimal Point: {optimal_point}")

    # Plot objective function
    objective_label = format_label(c1, c2, is_objective=True)
    if c2 != 0:
        y_obj = (c1 * x) / c2
        plt.plot(x, y_obj, 'r--', label=f"Objective: {objective_label}")
    else:
        x_obj = np.full_like(np.linspace(y_range[0], y_range[1], 400), -0 / c1)
        plt.plot(x_obj, np.linspace(y_range[0], y_range[1], 400), 'r--', label=f"Objective: {objective_label}")

    # Labels and legend
    plt.xlim(x_range)
    plt.ylim(y_range)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.legend()
    plt.title("Graphical Solution of Linear Programming Problem")
    plt.grid()
    plt.show()
