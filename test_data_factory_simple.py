from sqlite_utils import save_to_sqlite, read_from_sqlite, get_all_ids
from data_factory import generate_functions, compute_differences_with_constants
import sqlite3
import os

def run_simple_test(m, n, low, high, constant_low, constant_high, db_name="test_intersections.db"):
    """Run a simple test to verify functionality for a specific m and n."""

    # Cleanup
    # if os.path.exists(db_name):
    #     os.remove(db_name)
    #     print(f"\nCleaned up test database: {db_name}")


    # Generate functions
    functions = generate_functions(m, n, low, high)
    print(f"Generated {len(functions)} functions:")
    for func in functions:
        print(func)

    # Compute differences and constants
    records = compute_differences_with_constants(functions, constant_low, constant_high)
    print(f"\nComputed {len(records)} records (differences + constants):")
    for record in records[:5]:  # Show first 5 records for brevity
        print(record)

    # Save to SQLite
    save_to_sqlite(records, m, n, db_name=db_name)

    # Establish a single connection for reading
    conn = sqlite3.connect(db_name)

    # Fetch all IDs from the table
    ids = get_all_ids(m, n, db_name=db_name)
    print(f"\nFetched {len(ids)} IDs from SQLite table intersections_m{m}_n{n}: {ids[:5]}")

    # Fetch records one by one using the connection
    print("\nFetching records by ID:")
    for record_id in ids[:5]:  # Show first 5 records for brevity
        record = read_from_sqlite(m, n, conn=conn, record_id=record_id)
        print(f"Record with ID {record_id}: {record}")

    # Fetch all records at once
    print("\nFetching all records:")
    all_records = read_from_sqlite(m, n, conn=conn)
    print(f"Read {len(all_records)} records from SQLite table intersections_m{m}_n{n}:")
    for record in all_records[:5]:  # Show first 5 records for brevity
        print(record)

    # Close the connection
    conn.close()

    # # Cleanup
    # if os.path.exists(db_name):
    #     os.remove(db_name)
    #     print(f"\nCleaned up test database: {db_name}")


if __name__ == "__main__":
    # Test cases for different values of m and n
    test_cases = [
        (2000, 2, 0, 100, 0, 0)
    ]

    for m, n, low, high, constant_low, constant_high in test_cases:
        run_simple_test(m, n, low, high, constant_low, constant_high)
        print("\n" + "=" * 50 + "\n")
