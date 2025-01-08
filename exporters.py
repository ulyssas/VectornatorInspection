"""
VI exporters

outputs svg file.

! Major work has to be done in this and tools.py
"""


import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

import tools_path as tp
import styles_path as sp


def create_svg(artboard, layers, file):
    """Exports svg file. Under construction."""

    # TODO if there's something inside groupElements, VI has to ignore stylables~pathGeometry
    # ! cannot handle groups inside groups, or compoundPath(What?)

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
        for element in elements:
            # if the element is a group
            if element.get("groupElements", []):
                root_transform = element.get("localTransform")
                svg_group = ET.Element("g", {
                    "id": layer.get("name"),
                    "transform": tp.create_group_transform(root_transform)
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
    """

    stroke_style = element.get("strokeStyle", None)
    fill_style = element.get("fill")

    # Decode stroke style only if it exists
    if stroke_style:
        decoded_stroke_style = sp.decode_stroke_style(stroke_style)
        stroke = decoded_stroke_style.get("stroke", "none")
        stroke_width = decoded_stroke_style.get("stroke-width")
        stroke_opacity = decoded_stroke_style.get("stroke-opacity")
        stroke_linecap = decoded_stroke_style.get("stroke-linecap")
        stroke_linejoin = decoded_stroke_style.get("stroke-linejoin")
    else:
        stroke = "none"
        stroke_width = "0"
        stroke_opacity = "1"
        stroke_linecap = "butt"
        stroke_linejoin = "miter"

    # Decode fill only if it exists
    if fill_style:
        decoded_fill = sp.decode_fill(fill_style)
        fill = decoded_fill.get("fill")
        fill_opacity = decoded_fill.get("fill-opacity")
    else:
        fill = "none"
        fill_opacity = "1"

    # Create style attribute
    style_parts = [
        f"display:{'none' if element.get('isHidden') else 'inline'}",
        f"fill:{fill or 'none'}",
        f"fill-opacity:{fill_opacity}",
        f"stroke:{stroke}",
        f"stroke-width:{stroke_width}",
        f"stroke-opacity:{stroke_opacity}",
        f"stroke-linecap:{stroke_linecap}",
        f"stroke-linejoin:{stroke_linejoin}"
    ]
    style = ";".join(style_parts)

    attributes = {
        "id": element.get("name"),
        #"style": "fill:#565656;fill-opacity:0.000000;stroke:#000000;stroke-width:10;stroke-opacity:1;stroke-linecap:butt;stroke-linejoin:round",
        "style": style,
        "d": path_geometry_to_svg_path(
            tp.apply_transform(element.get("pathGeometry"), element.get("localTransform"))
        )
    }

    return ET.Element("path", attributes)


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
