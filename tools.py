"""
VI tools

miscellaneous functions
"""


import math


def apply_transform(data, local_transform):
    rotated = apply_rotation(data, local_transform.get("rotation"))
    scaled = apply_scale(rotated, local_transform.get("scale"))
    translated = apply_translation(scaled, local_transform.get("translation"))
    return translated


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
    """Applies rotation to pathGeometry nodes."""
    angle = rotation  # rotation angle(radian)
    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)
    transformed_nodes = []

    for node in data["nodes"]:
        transformed_node = {
            "anchorPoint": [
                cos_theta * node["anchorPoint"][0] - sin_theta * node["anchorPoint"][1],
                sin_theta * node["anchorPoint"][0] + cos_theta * node["anchorPoint"][1]
            ],
            "inPoint": [
                cos_theta * node["inPoint"][0] - sin_theta * node["inPoint"][1],
                sin_theta * node["inPoint"][0] + cos_theta * node["inPoint"][1]
            ],
            "outPoint": [
                cos_theta * node["outPoint"][0] - sin_theta * node["outPoint"][1],
                sin_theta * node["outPoint"][0] + cos_theta * node["outPoint"][1]
            ],
            "nodeType": node["nodeType"],
            "cornerRadius": node["cornerRadius"],
        }
        transformed_nodes.append(transformed_node)

    return {
        "closed": data["closed"],
        "nodes": transformed_nodes
    }


def apply_scale(data, scale):
    """Applies scaling to pathGeometry nodes."""
    sx, sy = scale  # scale coefficients
    transformed_nodes = []

    for node in data["nodes"]:
        transformed_node = {
            "anchorPoint": [
                node["anchorPoint"][0] * sx,
                node["anchorPoint"][1] * sy
            ],
            "inPoint": [
                node["inPoint"][0] * sx,
                node["inPoint"][1] * sy
            ],
            "outPoint": [
                node["outPoint"][0] * sx,
                node["outPoint"][1] * sy
            ],
            "nodeType": node["nodeType"],
            "cornerRadius": node["cornerRadius"] * max(abs(sx), abs(sy)),  # adapt cornerRadius
        }
        transformed_nodes.append(transformed_node)

    return {
        "closed": data["closed"],
        "nodes": transformed_nodes
    }