import os

# Define the range of m values and fixed d value
m_values = range(1000, 11000, 1000)  # m = 10, 20, 30, 40
d = 2

# Output file for performance data
output_file = "performance_data/performance_m_1210_0001_large.txt"

# Run vi_tree_main.py for each m value
for m in m_values:
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
