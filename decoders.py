"""
VI decoders

converts Vectornator JSON data to usable data.
"""


import base64
import json
import plistlib
import xml.etree.ElementTree as ET


def decode_b64_plist(encoded_string):
    """Decodes Vectornator Text data (Binary plist encoded in base64)."""
    decoded_bplist = plistlib.loads(base64.b64decode(encoded_string))
    return decoded_bplist


def path_geometry_to_svg_path(data):
    """Converts pathGeometry data to svg path (d={path})."""
    nodes = data["nodes"]
    closed = data.get("closed", False)
    svg_path = ""

    # start from initial anchor point
    first_node = nodes[0]
    svg_path += f"M {first_node['anchorPoint'][0]} {first_node['anchorPoint'][1]} "

    # process each nodes in order
    for i, node in enumerate(nodes[1:], start=1):
        anchor = node["anchorPoint"]
        in_point = node.get("inPoint", anchor)
        out_point = nodes[i - 1].get("outPoint", nodes[i - 1]["anchorPoint"])

        # bezier curve
        svg_path += f"C {out_point[0]} {out_point[1]} {in_point[0]} {in_point[1]} {anchor[0]} {anchor[1]} "

    # close path option
    if closed:
        # adds a curve which connects last node and first node
        last_node = nodes[-1]
        out_point = last_node.get("outPoint", last_node["anchorPoint"])
        in_point = first_node.get("inPoint", first_node["anchorPoint"])
        svg_path += f"C {out_point[0]} {out_point[1]} {in_point[0]} {in_point[1]} {first_node['anchorPoint'][0]} {first_node['anchorPoint'][1]} "
        svg_path += "Z"

    return svg_path


def create_svg_header(artboard):
    """
    Converts an artboard JSON object to an SVG element.

    Args:
        artboard (dict): A dictionary containing artboard data.

    Returns:
        ET.Element: An SVG root element with attributes based on the artboard data.
    """
    # Extract frame information
    frame = artboard["frame"]
    width = frame["width"]
    height = frame["height"]
    x = frame["x"]
    y = frame["y"]

    # Create the SVG element
    svg_header = ET.Element("svg", {
        "width": str(width),
        "height": str(height),
        "viewBox": f"{x} {y} {width} {height}",
        "xmlns": "http://www.w3.org/2000/svg"
    })

    return svg_header



def read_gid_json(gid_json):
    # List up all layers and elements
    layer_ids = gid_json.get("artboards", [])[0].get("layerIds", [])
    layers = gid_json.get("layers", [])
    elements = gid_json.get("elements", [])

    #print(json.dumps(layer_ids, indent=4))
    #print(json.dumps(layers, indent=4))
    #print(json.dumps(elements, indent=4))

    # Locate elements in layers.elementIds
    for layer_id in layer_ids:
        layer = layers[layer_id]
        layer_name = layer.get("name", "Unnamed Layer")
        layer_element_ids = layer.get("elementIds", [])

        print(f"Layer Name: {layer_name}")
        print("  Elements in Layer:")

        # process each elements
        for element_id in layer_element_ids:
            element = elements[element_id]
            if element:
                element_name = element.get("name", "Unnamed Element")
                print(f"    - Element Name: {element_name}")

#    artboards = gid_json["artboards"]
#    layers = gid_json["layers"]
#    elements = gid_json["elements"]
#    local_transforms = gid_json["localTransforms"]
#    stylables = gid_json["stylables"]
#    abstract_paths = gid_json["abstractPaths"]
#    path_stroke_styles = gid_json["pathStrokeStyles"]
#    paths = gid_json["paths"]
#    path_geometries = gid_json["pathGeometries"]

#    return gid_json["artboards"]
#    #return gid_json["artboards"]
