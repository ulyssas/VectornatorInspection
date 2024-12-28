"""
VI tools

miscellaneous functions
"""


import math


def apply_translation(data, translation):
    """Applies translation to pathGeometry nodes."""
    tx, ty = translation
    transformed_nodes = []

    for node in data["nodes"]:
        transformed_node = {
            "anchorPoint": [
                node["anchorPoint"][0] + tx,
                node["anchorPoint"][1] + ty
            ],
            "inPoint": [
                node["inPoint"][0] + tx,
                node["inPoint"][1] + ty
            ],
            "outPoint": [
                node["outPoint"][0] + tx,
                node["outPoint"][1] + ty
            ],
            "nodeType": node["nodeType"],
            "cornerRadius": node["cornerRadius"],
        }
        transformed_nodes.append(transformed_node)

    # returns new geometry data.
    return {
        "closed": data["closed"],
        "nodes": transformed_nodes
    }


def calculate_bbox_center(nodes):
    """Calculates the center of the bounding box for given nodes."""
    min_x = min(node["anchorPoint"][0] for node in nodes)
    max_x = max(node["anchorPoint"][0] for node in nodes)
    min_y = min(node["anchorPoint"][1] for node in nodes)
    max_y = max(node["anchorPoint"][1] for node in nodes)

    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    len_x = max_x - min_x
    len_y = max_y - min_y
    print(f"{len_x}, {len_y}")

    return center_x, center_y


def create_group_transform(localTransform):
    """
    Creates a transform string for the `g` element in SVG format.

    Args:
        localTransform (dict): A dictionary containing rotation, shear, scale, and translation.

    Returns:
        str: A transform string with separate transformations (e.g., rotate, translate, skewX, scale).
    """
    rotation = localTransform.get("rotation", 0) # radian
    scale = localTransform.get("scale", [1, 1])
    shear = localTransform.get("shear", 0) # ??? 60_deg in Curve == "shear": -1.732050807568874
    translation = localTransform.get("translation", [0, 0])

    # Extract values
    rotation_deg = math.degrees(rotation)
    sx, sy = scale
    shear_deg = math.degrees(math.atan(shear))  # Shear is given in radians
    tx, ty = translation
    #cx, cy = center # bound_center = t.calculate_bbox_center(element.get("pathGeometry")["nodes"])

    # Create transform components
    # The order is important
    transform_parts = []
    if tx != 0 or ty != 0:
        # Translate by (tx, ty)
        transform_parts.append(f"translate({tx:.6f} {ty:.6f})")

    if rotation != 0:
        # Rotate around origin (adjust if a specific pivot is needed)
        # rotation center annoyed me
        #transform_parts.append(f"rotate({rotation_deg:.6f} {cx:.6f} {cy:.6f})")
        transform_parts.append(f"rotate({rotation_deg:.6f})")

    if sx != 1 or sy != 1:
        # Scale by (sx, sy)
        transform_parts.append(f"scale({sx:.6f} {sy:.6f})")

    if shear != 0:
        # Skew in the X direction (SVG does not directly support skewY)
        transform_parts.append(f"skewX({shear_deg:.6f})")


    # Join components with spaces
    return " ".join(transform_parts)


