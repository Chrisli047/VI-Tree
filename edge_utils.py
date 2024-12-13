from scipy.spatial import ConvexHull
import numpy as np

def get_edges_from_hull(vertices):
    """
    Get all unique edges from the convex hull of the given vertices.
    If there are only two vertices, return the edge between them directly.

    :param vertices: A list of vertices (each vertex is a list or tuple of coordinates).
    :return: A tuple containing:
             - A list of unique edges, each represented by a pair of points (coordinates).
             - A list of convex hull vertices (coordinates).
    """
    # Convert the input to a NumPy array
    vertices = np.array(vertices)

    # Handle the case where only two vertices are provided
    if len(vertices) == 1:
        return [], [tuple(vertices[0])]

    if len(vertices) == 2:
        edges = [(tuple(vertices[0]), tuple(vertices[1]))]
        convex_hull_vertices = [tuple(vertices[0]), tuple(vertices[1])]
        return edges, convex_hull_vertices

    # Compute the convex hull
    hull = ConvexHull(vertices)
    edges = set()

    # Extract convex hull vertices
    convex_hull_vertices = [tuple(vertices[i]) for i in hull.vertices]

    # Loop through the simplices to get all edges
    for simplex in hull.simplices:
        for i in range(len(simplex)):
            for j in range(i + 1, len(simplex)):
                # Extract the pair of vertices that form an edge
                edge = tuple(sorted([tuple(vertices[simplex[i]]), tuple(vertices[simplex[j]])]))
                edges.add(edge)

    # Convert the set of edges to a sorted list for consistent output
    return list(edges), convex_hull_vertices


def compute_intersection_points(coefficients, segments):
    """
    Compute the unique intersection points of the linear equation Ax = b with a set of line segments,
    classify segments into segment_larger and segment_less based on their relation to Ax = b,
    classify vertices into vertex_larger and vertex_less, and split segments as needed.

    Parameters:
        coefficients: tuple, coefficients of the linear function (a1, a2, ..., an, b)
                      where the last element is b (the constant term)
        segments: list of tuples, each tuple contains two points defining a segment
        get_edges_from_hull: function to process intersection points into edges and hull vertices

    Returns:
        tuple: (segment_larger, segment_less, vertex_larger, vertex_less)
            - segment_larger: list of segments where points satisfy Ax > b
            - segment_less: list of segments where points satisfy Ax < b
            - vertex_larger: list of vertices where points satisfy Ax > b
            - vertex_less: list of vertices where points satisfy Ax < b
    """
    # Separate the coefficients for Ax and the constant term b
    a = np.array(coefficients[:-1], dtype=np.float64)  # Coefficients of the variables
    b = np.float64(coefficients[-1])  # Constant term

    segment_larger = []
    segment_less = []
    vertex_larger = set()
    vertex_less = set()
    intersection_points = []

    for segment in segments:
        v1, v2 = np.array(segment[0]), np.array(segment[1])
        # print("v1:", v1)
        # print("v2:", v2)
        f_v1 = np.dot(a, v1) - b
        f_v2 = np.dot(a, v2) - b

        # Classify v1 and v2 directly
        if f_v1 > 0:
            vertex_larger.add(tuple(v1))
        elif f_v1 < 0:
            vertex_less.add(tuple(v1))

        if f_v2 > 0:
            vertex_larger.add(tuple(v2))
        elif f_v2 < 0:
            vertex_less.add(tuple(v2))

        # Check if v1 or v2 lies on the hyperplane
        if f_v1 == 0:
            intersection_points.append(v1)
        if f_v2 == 0:
            intersection_points.append(v2)

        # Check where the segment endpoints lie relative to the hyperplane
        if (f_v1 > 0 and f_v2 >= 0) or (f_v1 >= 0 and f_v2 > 0):
            segment_larger.append(segment)
        elif (f_v1 < 0 and f_v2 <= 0) or (f_v1 <= 0 and f_v2 < 0):
            segment_less.append(segment)
        else:
            # Segment crosses the hyperplane, compute intersection
            c1 = np.dot(a, v1) - b
            c2 = np.dot(a, v2 - v1)
            if c2 != 0:  # Ensure the segment is not parallel to the hyperplane
                t = -c1 / c2
                if 0 <= t <= 1:
                    intersection = v1 + t * (v2 - v1)
                    intersection_points.append(intersection)
                    # Split the segment
                    if f_v1 > 0:
                        segment_larger.append((tuple(v1), tuple(intersection)))
                        segment_less.append((tuple(v2), tuple(intersection)))
                    else:
                        segment_larger.append((tuple(v2), tuple(intersection)))
                        segment_less.append((tuple(v1), tuple(intersection)))

    # Remove duplicate intersection points
    unique_points = list(set(map(tuple, intersection_points)))

    # Add edges and vertices from the convex hull of the intersection points
    edges_from_hull, vertices_from_hull = get_edges_from_hull(unique_points)

    # Append vertices from hull to larger/less sets
    for vertex in vertices_from_hull:
        if vertex not in vertex_larger and vertex not in vertex_less:
            f_vertex = np.dot(a, vertex) - b
            if f_vertex > 0:
                vertex_larger.add(vertex)
            elif f_vertex < 0:
                vertex_less.add(vertex)

    # Extend segments with hull edges
    segment_larger.extend(edges_from_hull)
    segment_less.extend(edges_from_hull)

    # Append vertices from hull to larger/less sets
    for vertex in vertices_from_hull:
        vertex_larger.add(vertex)
        vertex_less.add(vertex)


    return segment_larger, segment_less, vertex_larger, vertex_less


def print_segments(segment_larger, segment_less):
    """
    Pretty-print the segment lists for better readability.
    """
    def format_segment(segment):
        return f"({segment[0]}, {segment[1]})"

    print("Segment Larger:")
    for segment in segment_larger:
        print(f"  {format_segment(segment)}")

    print("\nSegment Less:")
    for segment in segment_less:
        print(f"  {format_segment(segment)}")