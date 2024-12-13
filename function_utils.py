import sqlite3
import time
from copy import deepcopy

import cdd
import numpy as np

from sqlite_utils import read_from_sqlite


def generate_constraints(n, var_min, var_max):
    """
    Generate constraints for an n-dimensional space with var_min and var_max.
    Returns a list of tuples in the format (coe1, coe2, ..., coen, constant).
    # Define inequalities in the form A x + b > 0
    """
    constraints = []

    for i in range(n):
        # Lower bound: x_i >= var_min -> x_i - var_min >= 0
        lower_bound = [0] * n
        lower_bound[i] = 1
        constraints.append((*lower_bound, -var_min))

        # Upper bound: x_i <= var_max -> -x_i + var_max >= 0
        upper_bound = [0] * n
        upper_bound[i] = -1
        constraints.append((*upper_bound, var_max))

    return constraints
#
# def compute_vertices(constraints):
#     # Define inequalities in the form A x + b > 0
#
#     """
#     Compute vertices for the initial domain from a list of constraints.
#     Constraints are in the format (coe1, coe2, ..., constant).
#     """
#     try:
#         rows = []
#         for constraint in constraints:
#             # Split the tuple into coefficients (A[i]) and the constant (b[i])
#             *coefficients, constant = constraint
#             row = [constant] + coefficients  # Include constant as the first element
#             rows.append(row)
#
#         # Convert to cdd matrix
#         mat = cdd.matrix_from_array(rows, rep_type=cdd.RepType.INEQUALITY)
#
#         # Check for redundant rows
#         # redundant_rows = cdd.redundant_rows(mat)
#         # print(f"Redundant rows: {redundant_rows}")
#
#         # Create polyhedron from the matrix
#         poly = cdd.polyhedron_from_matrix(mat)
#         ext = cdd.copy_generators(poly)
#
#         vertices = []
#         for row in ext.array:
#             if row[0] == 1.0:  # This indicates a vertex
#                 # vertex = [round(coord, 2) for coord in row[1:]]
#                 vertex = [coord for coord in row[1:]]
#                 vertices.append(vertex)
#
#         return vertices
#     except Exception as e:
#         print(f"Error in compute_vertices: {e}")
#         return []
#

def check_function(func, vertices, atol=0.0001) -> bool:
    """
    Checks if the function AX = b has vertices that satisfy both AX < b and AX > b.

    Parameters:
        func (tuple): A tuple in the format (coefficient1, coefficient2, ..., coefficientd, constant).
        vertices (list): List of vertices (each an iterable of coordinates).
        atol (float): Tolerance for considering a vertex close to the plane AX = b.

    Returns:
        bool: True if there exist vertices with AX < b and AX > b; False otherwise.
    """

    start_time = time.time()  # Start timer
    *coefficients, constant = func

    # Convert input to NumPy arrays
    coefficients_array = np.array(coefficients)
    vertices_array = np.array(vertices)  # shape: (num_vertices, d)

    # Compute AX - b for all vertices in one go
    values = vertices_array.dot(coefficients_array) - constant

    # Filter out values close to zero
    mask = ~np.isclose(values, 0, atol=atol)
    filtered_values = values[mask]

    if filtered_values.size == 0:
        # All values are close to zero, no positive or negative strictly found
        return False

    # Check if there's at least one positive and one negative
    has_positive = np.any(filtered_values > 0)
    has_negative = np.any(filtered_values < 0)


    return has_positive and has_negative


def merge_constraints(node_constraints, init_constraints, m, n, db_name, conn):
    """
    Merge node.constraints with init_constraints by fetching records from the database.
    Parameters:
        node_constraints (list): Constraints for the current node.
        init_constraints (list): Global initial constraints.
        m (int): Number of functions.
        n (int): Dimension of functions.
        db_name (str): Database file name.
        conn: SQLite database connection.
    Returns:
        list of tuples: Merged constraints.
    """
    # Deep-copy init_constraints to avoid modifying the original
    merged_constraints = deepcopy(init_constraints)


    for record_id in node_constraints:
        # Fetch record from the database
        if record_id < 0:
            record = read_from_sqlite(m=m, n=n, db_name=db_name, record_id=-record_id, conn=conn)
            # Negate coefficients, keep constant unchanged
            record = tuple(-coeff for coeff in record[:-1]) + (record[-1],)  # Convert to a tuple
        else:
            record = read_from_sqlite(m=m, n=n, db_name=db_name, record_id=record_id, conn=conn)
            # Keep coefficients, negate constant
            record = tuple(record[:-1]) + (-record[-1],)  # Convert to a tuple

        # Append the modified record as a tuple to merged_constraints
        merged_constraints.append(record)

    return merged_constraints


def check_function_tight(func, vertices, atol=0.0001) -> bool:
    *coefficients, constant = func  # Unpack coefficients and constant

    # Convert coefficients to a NumPy array for vectorized operations
    coefficients_array = np.array(coefficients)
    # print("coefficients_array: ", coefficients_array)
    # print("vertices: ", vertices)
    counter = 0

    for vertex in vertices:
        # Convert vertex to a NumPy array
        vertex_array = np.array(vertex)

        # Evaluate AX - b for the current vertex
        value = np.dot(coefficients_array, vertex_array) - constant

        # Use np.isclose to check if the value is close to zero
        if np.isclose(value, 0, atol=atol):
            counter += 1

        if counter == 2:
            return True

    # If no crossing is found, return False
    return False

def get_tight_constraints(constraints, vertices, m, n, db_name, conn):
    # print("constraints: ", constraints)
    # print("vertices: ", vertices)
    tight_constraints = []


    for record_id in constraints:
        record = read_from_sqlite(m=m, n=n, db_name=db_name, record_id=abs(record_id), conn=conn)

        if check_function_tight(record, vertices):
            tight_constraints.append(record_id)

    # print("loose_constraints: ", constraints)
    # print("tight_constraints: ", tight_constraints)

    return tight_constraints


from decimal import Decimal, getcontext


def check_smallest_intervals(vertices, precision):
    import numpy as np

    # Determine scaling factor
    scale = int(round(1 / precision))  # e.g. 1/0.01 = 100

    # Scale and convert vertices to integers
    vertices = np.array(vertices)
    scaled_vertices = np.round(vertices * scale).astype(int)

    # Exclude the origin
    non_origin_vertices = scaled_vertices[~np.all(scaled_vertices == 0, axis=1)]

    n_dims = non_origin_vertices.shape[1]

    for i in range(n_dims):
        sorted_values = np.sort(non_origin_vertices[:, i])
        differences = np.diff(sorted_values)

        # Exclude zero differences
        non_zero_differences = differences[differences > 0]

        if len(non_zero_differences) == 0:
            continue

        smallest_difference = np.min(non_zero_differences)

        # smallest_difference here is already in integer increments corresponding to 'precision'.
        # If smallest_difference > 1, it means it's more than the precision step.
        if smallest_difference > 1:
            return False

    return True


class FunctionProfiler:
    total_time_compute_vertices = 0.0
    total_time_check_function = 0.0
    total_time_read_from_sqlite = 0.0

    @classmethod
    def compute_vertices(cls, constraints):
        start_time = time.time()
        try:
            rows = []
            for constraint in constraints:
                # Split the tuple into coefficients and the constant
                *coefficients, constant = constraint
                row = [constant] + coefficients  # Include constant as the first element
                rows.append(row)

            # Convert to cdd matrix
            mat = cdd.matrix_from_array(rows, rep_type=cdd.RepType.INEQUALITY)

            # Create polyhedron from the matrix
            poly = cdd.polyhedron_from_matrix(mat)
            ext = cdd.copy_generators(poly)

            vertices = []
            for row in ext.array:
                if row[0] == 1.0:  # This indicates a vertex
                    vertex = [coord for coord in row[1:]]
                    vertices.append(vertex)

        except Exception as e:
            print(f"Error in compute_vertices: {e}")
            vertices = []

        elapsed_time = time.time() - start_time
        cls.total_time_compute_vertices += elapsed_time
        return vertices

    @classmethod
    def check_function(cls, func, vertices, atol=0.0001) -> bool:
        start_time = time.time()

        *coefficients, constant = func

        # Convert input to NumPy arrays
        coefficients_array = np.array(coefficients)
        vertices_array = np.array(vertices)  # shape: (num_vertices, d)

        # Compute AX - b for all vertices in one go
        values = vertices_array.dot(coefficients_array) - constant

        # Filter out values close to zero
        mask = ~np.isclose(values, 0, atol=atol)
        filtered_values = values[mask]

        if filtered_values.size == 0:
            result = False
        else:
            # Check if there's at least one positive and one negative
            has_positive = np.any(filtered_values > 0)
            has_negative = np.any(filtered_values < 0)
            result = has_positive and has_negative

        elapsed_time = time.time() - start_time
        cls.total_time_check_function += elapsed_time
        return result

    @classmethod
    def read_from_sqlite(cls, m, n, db_name="test_intersections.db", record_id=None, conn=None):
        """
        Read records from a dynamically named SQLite table based on m and n.
        Optionally filter by ID. Use an existing connection if provided.
        Returns a single record (without the index) as a tuple or a list of tuples.
        """
        start_time = time.time()

        close_conn = False
        if conn is None:
            conn = sqlite3.connect(db_name)
            close_conn = True

        cursor = conn.cursor()
        table_name = f"intersections_m{m}_n{n}"

        # Query records
        if record_id is not None:
            cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (record_id,))
            result = cursor.fetchone()  # Fetch a single record
            result = tuple(result[1:]) if result else None  # Skip the index (position 0)
        else:
            cursor.execute(f"SELECT * FROM {table_name}")
            result = [tuple(row[1:]) for row in cursor.fetchall()]  # Skip the index for all rows

        # Close the connection if it was created in this function
        if close_conn:
            conn.close()

        elapsed_time = time.time() - start_time
        cls.total_time_read_from_sqlite += elapsed_time
        return result


# Usage Example:
# FunctionProfiler.compute_vertices(constraints_list)
# FunctionProfiler.check_function((1, 2, 3, 4), vertices_list)
# print("Total time in compute_vertices:", FunctionProfiler.total_time_compute_vertices)
# print("Total time in check_function:", FunctionProfiler.total_time_check_function)
