import os

# Define the range of d values and fixed m value
d_values = range(3, 11)  # d = 2, 3, 4, 5
m = 100

# Output file for performance data
output_file = "performance_data/performance_d_1210_01.txt"

# Run vi_tree_main.py for each d value
for d in d_values:
    command = f"python vi_tree_main.py {m} {d}"
    print(f"Running: {command}")

    # Run the command and capture the output
    result = os.popen(command).read()

    # Extract relevant performance data from the output
    lines = result.splitlines()
    time_taken = next((line for line in lines if "Time taken" in line), "Time taken: N/A")
    tree_height = next((line for line in lines if "Height of the VI Tree" in line), "Height: N/A")
    leaf_count = next((line for line in lines if "Number of leaf nodes" in line), "Leaf nodes: N/A")

    # Append the performance data to the output file
    with open(output_file, "a") as file:
        file.write(f"m={m}, n={d}, {time_taken}, {tree_height}, {leaf_count}\n")

print(f"Performance results saved to {output_file}")
