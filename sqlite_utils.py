import sqlite3


def save_to_sqlite(records, m, n, db_name="test_intersections.db"):
    """
    Save records to an SQLite database in a table named dynamically based on m and n.
    Create an index on the ID column for each table.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Define the dynamic table name
    table_name = f"intersections_m{m}_n{n}"

    # Create table
    num_coefficients = len(records[0]) - 2  # Number of coefficients in each record
    columns = ", ".join([f"coe{i} INTEGER" for i in range(1, num_coefficients + 1)])
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            {columns},
            constant INTEGER
        )
    """)

    # Insert records
    placeholders = ", ".join(["?"] * len(records[0]))
    cursor.executemany(f"INSERT INTO {table_name} VALUES ({placeholders})", records)

    # Create an index on the ID column
    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_id_{m}_{n} ON {table_name} (id)")

    conn.commit()
    conn.close()
    print(f"Data saved to table {table_name} in {db_name} with an index on the ID column.")


def read_from_sqlite(m, n, db_name="test_intersections.db", record_id=None, conn=None):
    """
    Read records from a dynamically named SQLite table based on m and n.
    Optionally filter by ID. Use an existing connection if provided.
    Returns a single record (without the index) as a tuple or a list of tuples.
    """
    # Use the provided connection, or create a new one
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

    return result



def get_all_ids(m, n, db_name="test_intersections.db"):
    """
    Fetch all IDs from the specified table.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    table_name = f"intersections_m{m}_n{n}"
    try:
        cursor.execute(f"SELECT id FROM {table_name}")
        ids = [row[0] for row in cursor.fetchall()]
        return ids
    except sqlite3.OperationalError as e:
        print(f"Error fetching IDs from table {table_name}: {e}")
        return []
    finally:
        conn.close()