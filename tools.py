"""
VI tools

miscellaneous functions
"""


import math


def apply_transform(data, transform):
    """Applies localTransform to pathGeometry data."""
    #transformed = apply_scale(data, transform.get("scale"))
    transformed = apply_rotation(data, transform.get("rotation"))
    #transformed = apply_shear(transformed, transform.get("shear"))
    transformed = apply_translation(data, transform.get("translation"))

    return transformed

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


def apply_rotation(data, rotation):
    """Applies rotation (around center) to pathGeometry nodes."""
    # rotation is in radians
    cos_theta = math.cos(rotation)
    sin_theta = math.sin(rotation)
    transformed_nodes = []

    # Calculate the center of the bounding box
    center_x, center_y = calculate_bbox_center(data["nodes"])

    for node in data["nodes"]:
        # Move to origin
        anchor_x, anchor_y = node["anchorPoint"]
        in_x, in_y = node["inPoint"]
        out_x, out_y = node["outPoint"]

        anchor_x -= center_x
        anchor_y -= center_y
        in_x -= center_x
        in_y -= center_y
        out_x -= center_x
        out_y -= center_y

        # Apply rotation
        new_anchor = [
            cos_theta * anchor_x - sin_theta * anchor_y,
            sin_theta * anchor_x + cos_theta * anchor_y,
        ]
        new_in = [
            cos_theta * in_x - sin_theta * in_y,
            sin_theta * in_x + cos_theta * in_y,
        ]
        new_out = [
            cos_theta * out_x - sin_theta * out_y,
            sin_theta * out_x + cos_theta * out_y,
        ]

        # Move back from origin
        new_anchor[0] += center_x
        new_anchor[1] += center_y
        new_in[0] += center_x
        new_in[1] += center_y
        new_out[0] += center_x
        new_out[1] += center_y

        # Create transformed node
        transformed_node = {
            "anchorPoint": new_anchor,
            "inPoint": new_in,
            "outPoint": new_out,
            "nodeType": node["nodeType"],
            "cornerRadius": node["cornerRadius"],
        }
        transformed_nodes.append(transformed_node)

    return {
        "closed": data["closed"],
        "nodes": transformed_nodes
    }


def apply_scale(data, scale):
    """Applies scaling (around center) to pathGeometry nodes."""
    sx, sy = scale  # scale coefficients
    transformed_nodes = []

    # Calculate the center of the bounding box
    center_x, center_y = calculate_bbox_center(data["nodes"])

    for node in data["nodes"]:
        # Move to origin
        anchor_x, anchor_y = node["anchorPoint"]
        in_x, in_y = node["inPoint"]
        out_x, out_y = node["outPoint"]

        anchor_x -= center_x
        anchor_y -= center_y
        in_x -= center_x
        in_y -= center_y
        out_x -= center_x
        out_y -= center_y

        # Apply scaling
        new_anchor = [anchor_x * sx, anchor_y * sy]
        new_in = [in_x * sx, in_y * sy]
        new_out = [out_x * sx, out_y * sy]

        # Move back from origin
        new_anchor[0] += center_x
        new_anchor[1] += center_y
        new_in[0] += center_x
        new_in[1] += center_y
        new_out[0] += center_x
        new_out[1] += center_y

        # Create transformed node
        transformed_node = {
            "anchorPoint": new_anchor,
            "inPoint": new_in,
            "outPoint": new_out,
            "nodeType": node["nodeType"],
            "cornerRadius": node["cornerRadius"] * max(abs(sx), abs(sy)),  # Adapt corner radius
        }
        transformed_nodes.append(transformed_node)

    return {
        "closed": data["closed"],
        "nodes": transformed_nodes
    }


def apply_shear(data, shear):
    """
    Applies a SkewX (shear along the X-axis) transformation to pathGeometry nodes.
    The transformation is applied around the center of the bounding box.

    Args:
        data (dict): A dictionary containing pathGeometry data with nodes.
        shear (float): The shear factor in radians to be applied along the X-axis.

    Returns:
        dict: A new pathGeometry dictionary with sheared nodes.
    """
    # Calculate the center of the bounding box
    nodes = data["nodes"]
    min_x = min(node["anchorPoint"][0] for node in nodes)
    max_x = max(node["anchorPoint"][0] for node in nodes)
    min_y = min(node["anchorPoint"][1] for node in nodes)
    max_y = max(node["anchorPoint"][1] for node in nodes)

    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    transformed_nodes = []

    for node in nodes:
        # Extract original coordinates
        anchor_x, anchor_y = node["anchorPoint"]
        in_x, in_y = node["inPoint"]
        out_x, out_y = node["outPoint"]

        # Translate to origin (center of bounding box)
        anchor_x -= center_x
        anchor_y -= center_y
        in_x -= center_x
        in_y -= center_y
        out_x -= center_x
        out_y -= center_y

        # Apply shear transformation: x' = x + shear * y
        new_anchor = [anchor_x + shear * anchor_y, anchor_y]
        new_in = [in_x + shear * in_y, in_y]
        new_out = [out_x + shear * out_y, out_y]

        # Translate back to original center
        new_anchor[0] += center_x
        new_anchor[1] += center_y
        new_in[0] += center_x
        new_in[1] += center_y
        new_out[0] += center_x
        new_out[1] += center_y

        # Create transformed node
        transformed_node = {
            "anchorPoint": new_anchor,
            "inPoint": new_in,
            "outPoint": new_out,
            "nodeType": node["nodeType"],
            "cornerRadius": node["cornerRadius"],
        }
        transformed_nodes.append(transformed_node)

    # Return updated geometry data
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
    print(f"center: {center_x}, {center_y}")

    len_x = max_x - min_x
    len_y = max_y - min_y
    print(f"length: {len_x}, {len_y}")

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
    shear = localTransform.get("shear", 0)
    translation = localTransform.get("translation", [0, 0])

    # Extract values
    rotation_deg = math.degrees(rotation)
    sx, sy = scale
    shear_deg = math.degrees(math.atan(shear))  # Shear is given in radians
    tx, ty = translation
    #cx, cy = center # bound_center = t.calculate_bbox_center(element.get("pathGeometry")["nodes"])

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
        transform_parts.append(f"scale({sx:.6f} {sy:.6f})")

    if shear != 0:
        # Skew in the X direction
        transform_parts.append(f"skewX({shear_deg:.6f})")


    # Join components with spaces
    return " ".join(transform_parts)


