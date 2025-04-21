import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
import tkinter as tk
from tkinter import messagebox

def format_label(a1, a2, b=None, is_objective=False):
    """
    Format the label dynamically based on coefficients.
    """
    terms = []
    if a1 != 0:
        terms.append(f"{'' if a1 == 1 else a1}x₁")
    if a2 != 0:
        terms.append(f"{'' if a2 == 1 else a2}x₂")
    if is_objective:
        return f"{' + '.join(terms)}"
    return f"{' + '.join(terms)} ≤ {b}"


def find_intersection(constraint1, constraint2):
    """
    Find the intersection point of two constraints.
    """
    a1, a2, b1 = constraint1
    c1, c2, b2 = constraint2

    determinant = a1 * c2 - a2 * c1
    if determinant == 0:
        return None  # Parallel lines, no intersection

    x_1 = (b1 * c2 - b2 * a2) / determinant
    x_2 = (a1 * b2 - c1 * b1) / determinant
    return (x_1, x_2)


def is_feasible(point, constraints):
    """
    Check if a point satisfies all constraints.
    """
    x_1, x_2 = point
    if x_1 < 0 or x_2 < 0:  # Ensure the point is in the first quadrant
        return False
    for a1, a2, b in constraints:
        if a1 * x_1 + a2 * x_2 > b:
            return False
    return True


def calculate_dynamic_range(intersection_points):
    """
    Calculate dynamic x_range and y_range based on intersection points.
    """
    x_1_values = [p[0] for p in intersection_points if p[0] >= 0]
    x_2_values = [p[1] for p in intersection_points if p[1] >= 0]

    x_min, x_max = 0, max(x_1_values) * 1.2 if x_1_values else 10
    y_min, y_max = 0, max(x_2_values) * 1.2 if x_2_values else 10

    return (x_min, x_max), (y_min, y_max)


def is_unbounded(feasible_polygon, constraints, objective, maximize):
    """
    Check if the problem is unbounded by examining the feasible region and objective direction.
    """
    if not feasible_polygon:
        return False

    c1, c2 = objective
    if not maximize:
        c1, c2 = -c1, -c2

    # Check each constraint's ability to bound the objective direction
    can_grow_indefinitely = True
    for a1, a2, b in constraints:
        # Calculate dot product between constraint normal and objective direction
        dot_product = a1 * c1 + a2 * c2
        if dot_product > 0:
            can_grow_indefinitely = False
            break

    return can_grow_indefinitely

def solve_graphically(objective, constraints, maximize=True):
    """
    Solve a 2-variable linear programming problem graphically.

    Args:
        objective (tuple): Coefficients of the objective function (e.g., (c1, c2) for c1*x₁ + c2*x₂).
        constraints (list): List of constraints in the form [(a1, a2, b, operator), ...],
                            where operator is either "<=" or ">=".
        maximize (bool): Whether to maximize or minimize the objective function.
    """
    # Unpack objective coefficients at the start
    c1, c2 = objective

    # Normalize constraints to handle both "<=" and ">="
    normalized_constraints = []
    for constraint in constraints:
        a1, a2, b, operator = constraint
        if operator == ">=":
            # Flip the inequality
            a1, a2, b = -a1, -a2, -b
        normalized_constraints.append((a1, a2, b))

    # Find all intersection points
    intersection_points = []
    for constraint1, constraint2 in combinations(normalized_constraints, 2):
        point = find_intersection(constraint1, constraint2)
        if point is not None and is_feasible(point, normalized_constraints):
            intersection_points.append(point)

    # Add boundary points (x_1=0 and x_2=0 intersections)
    for a1, a2, b in normalized_constraints:
        if a1 != 0:  # Intersection with x_2-axis (x_1=0)
            x_2 = b / a2 if a2 != 0 else None
            if x_2 is not None and x_2 >= 0:
                intersection_points.append((0, x_2))
        if a2 != 0:  # Intersection with x_1-axis (x_2=0)
            x_1 = b / a1 if a1 != 0 else None
            if x_1 is not None and x_1 >= 0:
                intersection_points.append((x_1, 0))

    # Calculate dynamic range
    x_range, y_range = calculate_dynamic_range(intersection_points)
    x_1 = np.linspace(x_range[0], x_range[1], 400)

    plt.figure(figsize=(8, 8))

    # Plot constraints
    for a1, a2, b in normalized_constraints:
        label = format_label(a1, a2, b)
        if a1 == 0 and a2 == 0:
            # Skip constraints with both coefficients zero
            continue
        elif a1 == 0:
            # Horizontal line x₂ = b/a2
            plt.axhline(y=b / a2, label=label)
        elif a2 == 0:
            # Vertical line x₁ = b/a1
            plt.axvline(x=b / a1, label=label)
        else:
            # Regular line
            x_2 = (b - a1 * x_1) / a2
            plt.plot(x_1, x_2, label=label)

    # Sort intersection points to form a polygon for the feasible region
    feasible_polygon = [point for point in intersection_points if is_feasible(point, normalized_constraints)]

    # If no feasible points, show a popup and exit
    if not feasible_polygon:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Not Feasible", "The problem is not feasible!\nThere is no region that satisfies all constraints.")
        root.destroy()
        plt.title("Graphical Solution of Linear Programming Problem (Not Feasible)")
        plt.grid()
        plt.show()
        print("\nThe problem is not feasible!")
        return

    # Ensure the points are sorted in a way that forms a closed polygon
    if len(feasible_polygon) > 2:
        # Sort points to form a closed polygon
        feasible_polygon = sorted(feasible_polygon, key=lambda p: (p[0], p[1]))
        polygon_x, polygon_y = zip(*feasible_polygon)

        # Shade the feasible region in grey
        plt.fill(polygon_x, polygon_y, color='gray', alpha=0.3, label="Feasible Region")

    # Highlight all critical points in green and add to the legend
    if feasible_polygon:
        critical_points_x, critical_points_y = zip(*feasible_polygon)
        plt.scatter(critical_points_x, critical_points_y, color='green', zorder=5, label="Critical Points")
        for point in feasible_polygon:
            plt.text(point[0], point[1], f"({point[0]:.2f}, {point[1]:.2f})", fontsize=8, color='green')

    # Check for unboundedness before finding optimal points
    normalized_constraints = [(a1, a2, b) for a1, a2, b, _ in constraints]
    if is_unbounded(feasible_polygon, normalized_constraints, objective, maximize):
        # Show popup message
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("Unbounded Solution", 
            "The problem is unbounded!\nThe objective function can increase indefinitely.")
        root.destroy()

        # Draw multiple arrows to show unboundedness
        arrow_base_x = center_x
        arrow_base_y = center_y
        arrow_scale = 0.5
        
        for i in range(3):
            dx = c1 * arrow_scale * (i + 1)
            dy = c2 * arrow_scale * (i + 1)
            plt.arrow(arrow_base_x, arrow_base_y, dx, dy,
                     head_width=0.2, head_length=0.3, fc='red', ec='red',
                     label='Direction of Unboundedness' if i == 0 else "")
            arrow_base_x += dx
            arrow_base_y += dy

        plt.text(0.5, 0.95, "UNBOUNDED SOLUTION",
                fontsize=16, color='red',
                transform=plt.gca().transAxes,
                horizontalalignment='center',
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='red'))
        
        # Finish plotting
        plt.legend()
        plt.title("Graphical Solution of Linear Programming Problem (Unbounded)")
        plt.grid()
        plt.show()
        print("\nThe problem is unbounded!")
        return

    # Only proceed if the problem is not unbounded and there are feasible points
    if feasible_polygon and not is_unbounded(feasible_polygon, normalized_constraints, objective, maximize):
        optimal_point = None
        optimal_value = float('-inf') if maximize else float('inf')

        print("\nAll feasible points:")
        for point in feasible_polygon:
            x_1, x_2 = point
            value = c1 * x_1 + c2 * x_2
            print(f"Point: ({x_1:.2f}, {x_2:.2f}), Objective value: {value:.2f}")
            if (maximize and value > optimal_value) or (not maximize and value < optimal_value):
                optimal_value = value
                optimal_point = point

        if optimal_point is not None:
            print(f"\nSelected optimal point: ({optimal_point[0]:.2f}, {optimal_point[1]:.2f}) with value: {optimal_value:.2f}")
        else:
            print("\nNo optimal point found.")

    # Find the optimal point
    optimal_point = None
    optimal_value = float('-inf') if maximize else float('inf')

    # Debug print to verify feasible points
    print("\nAll feasible points:")
    for point in feasible_polygon:
        x_1, x_2 = point
        value = c1 * x_1 + c2 * x_2
        print(f"Point: ({x_1:.1f}, {x_2:.1f}), Objective value: {value:.1f}")
        if (maximize and value > optimal_value) or (not maximize and value < optimal_value):
            optimal_value = value
            optimal_point = point

    if optimal_point is not None:
        print(f"\nSelected optimal point: ({optimal_point[0]:.1f}, {optimal_point[1]:.1f}) with value: {optimal_value:.1f}")
    else:
        print("\nNo optimal point found.")

    # Find all optimal points
    optimal_value = float('-inf') if maximize else float('inf')
    optimal_points = []

    # First pass: find the optimal objective value
    for point in feasible_polygon:
        x_1, x_2 = point
        value = c1 * x_1 + c2 * x_2
        if (maximize and value > optimal_value) or (not maximize and value < optimal_value):
            optimal_value = value

    # Second pass: find all points that achieve the optimal value
    for point in feasible_polygon:
        x_1, x_2 = point
        value = c1 * x_1 + c2 * x_2
        if abs(value - optimal_value) < 1e-10:  # Use small epsilon for float comparison
            optimal_points.append(point)

    print(f"\nOptimal value: {optimal_value:.1f}")
    print("Optimal points:")
    for point in optimal_points:
        print(f"({point[0]:.2f}, {point[1]:.2f})")

    # Highlight all optimal points
    if optimal_points:
        optimal_x, optimal_y = zip(*optimal_points)
        if len(optimal_points) > 1:
            # For multiple optimal points, format each point's coordinates separately
            pt1_x, pt1_y = optimal_points[0]
            pt2_x, pt2_y = optimal_points[1]
            plt.scatter(optimal_x, optimal_y, color='red', zorder=5, 
                       label=f"Multiple Optimal Points: ({pt1_x:.2f}, {pt1_y:.2f}) and ({pt2_x:.2f}, {pt2_y:.2f})")
        else:
            # For a single optimal point, format coordinates
            pt_x, pt_y = optimal_points[0]
            plt.scatter(optimal_x, optimal_y, color='red', zorder=5,
                       label=f"Optimal Point: ({pt_x:.2f}, {pt_y:.2f})")

    # Plot objective function
    objective_label = format_label(c1, c2, is_objective=True)
    if c2 != 0:
        x_2_obj = (c1 * x_1) / c2
        plt.plot(x_1, x_2_obj, 'r--', label=f"Objective: {objective_label}")
    else:
        x_1_obj = np.full_like(np.linspace(y_range[0], y_range[1], 400), -0 / c1)
        plt.plot(x_1_obj, np.linspace(y_range[0], y_range[1], 400), 'r--', 
                label=f"Objective: {objective_label}")

    # Labels and legend
    plt.xlim(x_range)
    plt.ylim(y_range)
    plt.xlabel("$x_1$")
    plt.ylabel("$x_2$")
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.legend()
    plt.title("Graphical Solution of Linear Programming Problem")
    plt.grid()
    plt.show()
