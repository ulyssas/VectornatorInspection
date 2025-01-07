"""
VI exporters

outputs svg file.

! Major work has to be done in this and tools.py
"""


import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

import tools as t


def create_svg(artboard, layers, file):
    """Exports svg file. Under construction."""
    # SVG header
    svg = create_svg_header(artboard)

    # comment
    comment = ET.Comment("Generated with Vectornator Inspection")
    svg.append(comment)

    # layer as g
    for layer in layers:
        svg_layer = ET.Element("g", {
            "id": layer.get("name"),
            "opacity": str(layer.get("opacity")),
            "visibility": ("visible" if layer.get("isVisible") else "hidden")
        })
        elements = layer.get("elements")
        for element in elements: # ! cannot handle groups inside groups, or compoundPath(What?)
            # if the element is a group
            if element.get("groupElements", []):
                root_transform = element.get("localTransform")
                svg_group = ET.Element("g", {
                    "id": layer.get("name"),
                    "transform": t.create_group_transform(root_transform)
                })
                group_elements = element.get("groupElements")
                print(f"ELEMENTS {group_elements}")
                for group_element in group_elements:
                    svg_group_element = create_svg_element(group_element)
                    svg_group.append(svg_group_element)
                svg_layer.append(svg_group)

            # if it is not a group
            else:
                svg_element = create_svg_element(element)
                svg_layer.append(svg_element)
        svg.append(svg_layer)

    ET.dump(svg)

    # get input file directory
    directory = os.path.dirname(file)

    # create output file directory
    output = os.path.join(directory, "result.svg")

    # format svg tree
    rough_string = ET.tostring(svg, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_svg = reparsed.toprettyxml(indent="\t")

    # output prettified svg
    with open(output, "w", encoding="utf-8") as output_file:
        output_file.write(pretty_svg)


def create_svg_element(element):
    """
    Converts an element defined in VI Decoders.traverse_element() to an SVG path.

    Custom style does not work right now.

    path transform is not optimal, I really want apply_transform to work
    """
    return ET.Element("path", {
        "id": element.get("name"),
        "fill": "none", # TODO apply actual style
        "stroke": "#ff8585",
        "stroke-width": "3",
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
        #"transform": t.create_group_transform(element.get("localTransform")), # TODO Remove transform dependency
        "d": path_geometry_to_svg_path(
            #element.get("pathGeometry")
            t.apply_transform(element.get("pathGeometry"), element.get("localTransform"))
        )
    })


def create_svg_header(artboard):
    """
    Converts an artboard JSON object to an SVG header.

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
    title = artboard.get("title", "Untitled")

    # Create the SVG element
    svg_header = ET.Element("svg", {
        "width": str(width),
        "height": str(height),
        "viewBox": f"{x} {y} {width} {height}",
        "version": "1.1",
        "id": f"{title}",
        "xmlns": "http://www.w3.org/2000/svg"
    })

    return svg_header


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
