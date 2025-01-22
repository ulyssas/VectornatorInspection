"""
VI path tools

functions to manipulate localTransform
"""


import math


def apply_transform(data, transform):
    """Applies the given transform to the pathGeometry."""
    translation = transform.get("translation")
    data = apply_translation(data, translation)
    data = apply_shear(data, transform.get("shear"), translation)
    data = apply_scale(data, transform.get("scale"), translation)
    data = apply_rotation(data, transform.get("rotation"), translation)

    return data


def apply_translation(data, translation):
    """Applies translation to pathGeometry nodes."""
    tx, ty = translation
    transformed_nodes = []
    for node in data["nodes"]:
        transformed_node = {
            "nodeType": node["nodeType"], "cornerRadius": node["cornerRadius"]}
        for point in ["anchorPoint", "inPoint", "outPoint"]:
            x, y = node[point]
            transformed_node[point] = [x + tx, y + ty]
        transformed_nodes.append(transformed_node)
    # returns new geometry data.
    return {
        "closed": data["closed"],
        "nodes": transformed_nodes
    }


def apply_rotation(data, angle, origin=(0, 0)):
    """Applies rotation to pathGeometry nodes."""
    ox, oy = origin
    transformed_nodes = []
    for node in data["nodes"]:
        transformed_node = {
            "nodeType": node["nodeType"], "cornerRadius": node["cornerRadius"]}
        for point in ["anchorPoint", "inPoint", "outPoint"]:
            x, y = node[point]
            x -= ox
            y -= oy
            rotated_x = x * math.cos(angle) - y * math.sin(angle)
            rotated_y = x * math.sin(angle) + y * math.cos(angle)
            transformed_node[point] = [rotated_x + ox, rotated_y + oy]
        transformed_nodes.append(transformed_node)
    return {
        "closed": data["closed"],
        "nodes": transformed_nodes
    }


def apply_scale(data, scale, origin=(0, 0)):
    """Applies scale to pathGeometry nodes."""
    sx, sy = scale
    ox, oy = origin
    transformed_nodes = []

    for node in data["nodes"]:
        transformed_node = {
            "nodeType": node["nodeType"], "cornerRadius": node["cornerRadius"]}
        for point in ["anchorPoint", "inPoint", "outPoint"]:
            x, y = node[point]
            x -= ox
            y -= oy
            scaled_x = x * sx
            scaled_y = y * sy
            transformed_node[point] = [scaled_x + ox, scaled_y + oy]
        transformed_nodes.append(transformed_node)

    return {
        "closed": data["closed"],
        "nodes": transformed_nodes
    }


def apply_shear(data, shear, origin=(0, 0)):
    """Applies shear (skewX) to pathGeometry nodes."""
    ox, oy = origin
    transformed_nodes = []

    for node in data["nodes"]:
        transformed_node = {
            "nodeType": node["nodeType"], "cornerRadius": node["cornerRadius"]}
        for point in ["anchorPoint", "inPoint", "outPoint"]:
            x, y = node[point]
            x -= ox
            y -= oy
            sheared_x = x + y * shear
            transformed_node[point] = [sheared_x + ox, y + oy]
        transformed_nodes.append(transformed_node)

    return {
        "closed": data["closed"],
        "nodes": transformed_nodes
    }


def calculate_bbox_center(data):
    """Calculates the center of the bounding box for given nodes."""
    nodes = data["nodes"]

    min_x = min(node["anchorPoint"][0] for node in nodes)
    max_x = max(node["anchorPoint"][0] for node in nodes)
    min_y = min(node["anchorPoint"][1] for node in nodes)
    max_y = max(node["anchorPoint"][1] for node in nodes)

    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    print(f"center: {center_x}, {center_y}")

    len_x = max_x - min_x
    len_y = max_y - min_y
    print(f"length: {len_x}, {len_y}")

    return center_x, center_y


def calculate_origin(nodes, translation):
    """Return origin by combining translation and center of bounding box."""
    ox, oy = calculate_bbox_center(nodes)
    tx, ty = translation
    return ox+tx, oy+ty


def create_group_transform(local_transform, keep_proportion=False):
    """
    Creates a transform string for the `g` element in SVG format.

    Args:
        localTransform (dict): A dictionary containing rotation, shear, scale, and translation.

    Returns:
        str: A transform string with separate transformations (e.g., rotate, translate, skewX, scale).
    """
    rotation = local_transform.get("rotation", 0)  # radian
    scale = local_transform.get("scale", [1, 1])
    shear = local_transform.get("shear", 0)
    translation = local_transform.get("translation", [0, 0])

    # Extract values
    rotation_deg = math.degrees(rotation)
    sx, sy = scale
    shear_deg = math.degrees(math.atan(shear))  # Shear is given in radians
    tx, ty = translation

    # Create transform components
    # The order matters
    transform_parts = []
    if tx != 0 or ty != 0:
        # Translate by (tx, ty)
        transform_parts.append(f"translate({tx:.6f} {ty:.6f})")

    if rotation != 0:
        # Rotate around origin (adjust if a specific pivot is needed)
        transform_parts.append(f"rotate({rotation_deg:.6f})")

    if sx != 1 or sy != 1:
        # Scale by (sx, sy)
        if keep_proportion == True:
            transform_parts.append(f"scale({sx:.6f})")
        else:
            transform_parts.append(f"scale({sx:.6f} {sy:.6f})")

    if shear != 0:
        # Skew in the X direction
        transform_parts.append(f"skewX({shear_deg:.6f})")

    # Join components with spaces
    return " ".join(transform_parts)
