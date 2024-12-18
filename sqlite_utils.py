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


class SQLiteReader:
    """
    Class to read records from SQLite and store them in a class variable.
    """
    records = []  # Class variable to store all fetched records

    @classmethod
    def read_all_from_sqlite(cls, m, n, db_name="test_intersections.db", conn=None):
        """
        Fetch all records from the table and save them to the class variable.
        Skips the index column.
        """
        close_conn = False
        if conn is None:
            conn = sqlite3.connect(db_name)
            close_conn = True

        cursor = conn.cursor()
        table_name = f"intersections_m{m}_n{n}"

        try:
            cursor.execute(f"SELECT * FROM {table_name}")
            cls.records = [tuple(row[1:]) for row in cursor.fetchall()]  # Skip index column
            print(f"Records loaded from table {table_name}.")
        except sqlite3.OperationalError as e:
            print(f"Error reading table {table_name}: {e}")
            cls.records = []  # Reset records if there's an error
        finally:
            if close_conn:
                conn.close()

    @classmethod
    def get_records(cls):
        """
        Return the records stored in the class variable.
        """
        return cls.records

    @classmethod
    def get_record_by_id(cls, record_id):
        """
        Retrieve a record by ID (1-based index).
        Returns None if the ID is out of range.
        """
        if not cls.records:
            print("No records loaded. Call read_all_from_sqlite first.")
            return None

        try:
            # SQLite IDs usually start from 1, so subtract 1 for list indexing
            return cls.records[record_id - 1]
        except IndexError:
            print(f"Record with ID {record_id} does not exist.")
            return None