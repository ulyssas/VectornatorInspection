"""
VI tools

miscellaneous functions
"""


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
