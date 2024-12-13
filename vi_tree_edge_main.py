import argparse
import random

from sqlite_utils import read_from_sqlite, get_all_ids
from function_utils import generate_constraints, compute_vertices, check_function
from tqdm import tqdm  # Import the progress bar library
import time  # Import time for measuring execution
import sqlite3

from vertex_utils import create_lookup_table, VertexManager
from vi_tree_edge import VIETree

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process VI tree with given m and n.")
    parser.add_argument("m", type=int, help="Number of functions (m)")
    parser.add_argument("n", type=int, help="Dimension of functions (n)")
    parser.add_argument("--db", type=str, default="intersections.db", help="Database file (default: intersections.db)")
    parser.add_argument("--var_min", type=float, default=0, help="Minimum value for variables (default: 0)")
    parser.add_argument("--var_max", type=float, default=10, help="Maximum value for variables (default: 10)")
    args = parser.parse_args()

    m = args.m
    n = args.n
    db_name = args.db
    var_min = args.var_min
    var_max = args.var_max

    # Dynamically construct the table name
    table_name = f"intersections_m{m}_n{n}"

    # Open a single connection to the database
    conn = sqlite3.connect(db_name)

    # Get all IDs from the table
    ids = get_all_ids(m, n, db_name=db_name)
    print(f"Found {len(ids)} IDs in table {table_name}.")

    # Generate constraints using n (as dimensionality), var_min, and var_max
    constraints = generate_constraints(n, var_min, var_max)
    print("Generated constraints as tuples:")
    for constraint in constraints:
        print(constraint)

    # Compute vertices for the initial domain
    vertices = compute_vertices(constraints)
    print(f"Computed vertices of the initial domain: {vertices}")

    # Collect IDs of records that satisfy the condition
    satisfying_ids = []

    # Process records with progress tracking
    for record_id in ids:
        record = read_from_sqlite(m, n, conn=conn, record_id=record_id)
        if check_function(record, vertices):
            satisfying_ids.append(record_id)

    # Calculate the number of IDs to sample (20% of the total)
    sample_size = int(0.2 * len(ids))
    sampled_ids = satisfying_ids[:sample_size]

    # Initialize the VI Tree
    vie_tree = VIETree()

    # Fetch and process records by ID
    print("Processing records:")

    # Set a counter for the number of intersection partitions the domain
    counter = 0

    interval = 0.001

    # Start the timer
    start_time = time.time()

    # Insert records into the VI Tree with progress tracking
    for record_id in tqdm(sampled_ids, desc="Processing Records", unit="sampled_records"):
        record = read_from_sqlite(m, n, conn=conn, record_id=record_id)
        if check_function(record, vertices):
            counter += 1
            # print(f"Record with ID {record_id} satisfies the condition: {record}")
            # Insert the record into the VI Tree
            vie_tree.insert(record_id, constraints, vertices, m=m, n=n, db_name=db_name, conn=conn, var_min=var_min, var_max=var_max)
        # if counter > 4:
        #     break

    # Stop the timer
    end_time = time.time()

    # Print the number of intersection partitions
    print(f"Number of intersection partitions: {counter}")

    # Print the time taken to insert all records
    print(f"Time taken to insert all records into the VI Tree: {end_time - start_time:.2f} seconds")

    # print("\nVI Tree Structure (Layer by Layer with Records):")
    # vi_tree.print_tree_by_layer(m, n, db_name, conn)

    # Print the height of the tree
    print(f"Height of the VI Tree: {vie_tree.get_height()}")

    # Print the number of leaf nodes
    print(f"Number of leaf nodes in the VI Tree: {vie_tree.get_leaf_count()}")

    # Close the database connection
    conn.close()
    print("Database connection closed.")
