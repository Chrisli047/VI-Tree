import subprocess

def test_vi_tree(m, n, db_name="test_intersections.db"):
    """
    Test the vi_tree_main.py script to ensure it processes IDs and records correctly.
    """
    print(f"Testing with m={m}, n={n}, db_name={db_name}...")

    try:
        # Run the vi_tree_main.py script with the specified arguments
        result = subprocess.run(
            ["python", "vi_tree_main.py", str(m), str(n), "--db", db_name],
            capture_output=True,
            text=True,
            check=True
        )
        print("Test Output:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Test Failed with Error:")
        print(e.stderr)


if __name__ == "__main__":
    # Define test cases with different m and n values
    test_cases = [
        (100, 2)  # Example with m=5, n=3
        # (10, 3),  # Example with m=10, n=2
    ]

    # Run the test cases
    for m, n in test_cases:
        test_vi_tree(m, n)
        print("=" * 50)
