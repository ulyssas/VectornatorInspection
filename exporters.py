"""
VI exporters

outputs svg file.
"""


import base64
import os
import xml.etree.ElementTree as ET
from io import BytesIO
from xml.dom import minidom

from PIL import Image

import styles_path as sp
import tools_path as tp


def create_svg(artboard, layers, file):
    """Exports svg file. (WIP)"""

    # SVG header
    svg = create_svg_header(artboard)

    # Add <defs> element
    defs = ET.Element("defs", {
        "id": "defs1",
    })
    svg.append(defs)

    # comment
    comment = ET.Comment("Generated with Vectornator Inspection")
    svg.append(comment)

    # layer as g
    for layer in layers:
        svg_layer = create_svg_layer(layer, defs)
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

    # Custom declaration
    xml_declaration = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
    modified_svg = xml_declaration + '\n'.join(pretty_svg.splitlines()[1:])

    # output prettified svg
    with open(output, "w", encoding="utf-8") as output_file:
        output_file.write(modified_svg)

    # construct the tree and save svg file (unformatted svg)
    # tree = ET.ElementTree(svg)
    # tree.write(output, encoding="UTF-8", xml_declaration=True)


def create_svg_layer(layer, defs):
    """
    Converts a layer defined in VI Decoders.traverse_layer() to an SVG group.
    """

    # Inkscape only supports style tag (Opacity/Visibility DID NOT work)
    style_parts = [
        f"display:{'inline' if layer.get('isVisible') else 'none'}",
        f"opacity:{layer.get('opacity')}"
    ]
    style_layer = ";".join(style_parts)

    svg_layer = ET.Element("g", {
        "id": layer.get("name"),
        "style": style_layer,
    })
    elements = layer.get("elements", [])
    for element in elements:
        # if the element is a group
        if element.get("groupElements", []):
            # Process groups recursively
            svg_group = create_svg_group(element, defs)
            svg_layer.append(svg_group)

        # if it is not a group
        else:
            # Process individual elements
            print(f"ELEMENT: {element}")
            print(f"ELEMENTNAME: {element.get('name')}")
            svg_element, gradient = create_svg_element(element)
            svg_layer.append(svg_element)
            if gradient is not None:  # went through svg_path and got gradient
                defs.append(gradient)  # add gradient to defs

    return svg_layer


def create_svg_group(group_element, defs):
    """
    Recursively creates an SVG group element and its child elements.

    Args:
        group_element (dict): A dictionary representing a group element.
        defs: An svg defs to define gradients.

    Returns:
        ET.Element: An SVG group element with nested child elements.
    """
    root_transform = group_element.get("localTransform", {})
    style_parts = [
        f"display:{'none' if group_element.get('isHidden') else 'inline'}",
        f"opacity:{group_element.get('opacity', 1)}",
        f"mix-blend-mode:{sp.blend_mode_to_svg(group_element.get('blendMode', 1))}"
    ]
    style_group = ";".join(style_parts)

    svg_group = ET.Element("g", {
        "id": group_element.get("name"),
        "style": style_group,
        "transform": tp.create_group_transform(root_transform)
    })

    # Recursively process group elements
    group_elements = group_element.get("groupElements", [])
    for child in group_elements:
        if child.get("groupElements", []):
            # Recursively process nested groups
            nested_group = create_svg_group(child, defs)
            svg_group.append(nested_group)
        else:
            # Process individual elements
            svg_group_element, gradient = create_svg_element(child)
            if gradient is not None:  # went through svg_path and got gradient
                defs.append(gradient)  # add gradient to defs

            svg_group.append(svg_group_element)

    return svg_group


def create_svg_element(element):
    """
    Converts an element defined in VI Decoders.traverse_element() to an SVG element.
    """
    if element.get("imageData"):
        # convert to image element
        return create_svg_image(element)
    elif element.get("styledText"):
        # convert to text element
        return create_svg_text(element)
    elif element.get("pathGeometry"):
        # convert to path element
        return create_svg_path(element)


def create_svg_path(path_element):
    """
    Converts an element defined in VI Decoders.traverse_element() to an SVG path.
    """

    stroke_style = path_element.get("strokeStyle", None)
    fill_style = path_element.get("fill")
    fill_id = path_element.get("fillId")

    # Decode stroke style only if it exists
    if stroke_style:
        decoded_stroke_style = sp.decode_stroke_style(stroke_style)
        stroke = decoded_stroke_style.get("stroke", "none")
        stroke_width = decoded_stroke_style.get("stroke-width")
        stroke_opacity = decoded_stroke_style.get("stroke-opacity")
        stroke_linecap = decoded_stroke_style.get("stroke-linecap")
        stroke_dasharray = decoded_stroke_style.get("stroke-dasharray")
        stroke_linejoin = decoded_stroke_style.get("stroke-linejoin")
    else:
        stroke = "none"
        stroke_width = "0"
        stroke_opacity = "1"
        stroke_linecap = "butt"
        stroke_dasharray = ""
        stroke_linejoin = "miter"

    # Decode fill only if it exists
    if fill_style:
        decoded_fill = sp.decode_fill(fill_style)
        gradient = decoded_fill.get("gradient")
        if gradient:
            svg_gradient_element = sp.create_gradient_element(
                decoded_fill, path_element.get("localTransform"), fill_id)
            gradient_name = f"gradient{fill_id}"
            gradient_url = f"url(#{gradient_name})"
            fill_opacity = "1"
        else:
            svg_gradient_element = None
            gradient_url = None
            fill = decoded_fill.get("fill")
            fill_opacity = decoded_fill.get("fill-opacity")
    else:
        svg_gradient_element = None
        gradient_url = None
        fill = "none"
        fill_opacity = "1"

    # Create style attribute
    style_parts = [
        f"display:{'none' if path_element.get('isHidden') else 'inline'}",
        f"mix-blend-mode:{sp.blend_mode_to_svg(path_element.get('blendMode', 1))}",
        f"opacity:{path_element.get('opacity', 1)}",
        f"fill:{gradient_url or fill or 'none'}",
        f"fill-opacity:{fill_opacity}",
        f"fill-rule:{'nonzero'}",  # ? nonzero or evenodd ?
        f"stroke:{stroke}",
        f"stroke-width:{stroke_width}",
        f"stroke-opacity:{stroke_opacity}",
        f"stroke-linecap:{stroke_linecap}",
        f"stroke-dasharray:{stroke_dasharray}",
        f"stroke-linejoin:{stroke_linejoin}"
    ]
    style = ";".join(style_parts)

    geometries = path_element.get("pathGeometry")
    transformed = []

    for path in geometries:
        print(path)
        transformed.append(tp.apply_transform(
            path, path_element.get("localTransform")))

    attributes = {
        "id": path_element.get("name"),
        "style": style,
        "d": path_geometry_to_svg_path(transformed)
    }

    # add gradient to defs if exists
    return ET.Element("path", attributes), svg_gradient_element


def create_svg_image(image_element):
    """
    Converts an element defined in VI Decoders.traverse_element() to an SVG image.
    """
    image = image_element.get("imageData", "")  # b64 data
    transform = image_element.get("localTransform")
    img_format, _, _ = detect_image_format_and_size(image)

    # Create style attribute
    style_parts = [
        f"display:{'none' if image_element.get('isHidden') else 'inline'}",
        f"mix-blend-mode:{sp.blend_mode_to_svg(image_element.get('blendMode', 1))}",
        f"opacity:{image_element.get('opacity', 1)}",
    ]
    style = ";".join(style_parts)

    attributes = {
        "id": image_element.get("name"),
        "preserveAspectRatio": "none",
        "transform": tp.create_group_transform(transform),
        "style": style,
        "xlink:href": f"data:image/{str(img_format).lower()};base64,{image}"
    }

    # no gradient unlike create_svg_path
    return ET.Element("image", attributes), None


def create_svg_text(text_element):
    """
    Converts an element defined in VI Decoders.traverse_element() to an SVG text.
    """
    # Extract text properties
    text_property = text_element.get("textProperty", "")
    styled_text = text_element.get("styledText", "")
    transform = text_element.get("localTransform", {})

    # Decode font properties from styled_text
    font_family = styled_text.get("fontName", {}).get("values")[0].get("value", "sans-serif")
    font_size = styled_text.get("fontSize", {}).get("values")[0].get("value", 16)
    font_weight = styled_text.get("fontWeight", "normal")

    # Text alignment and anchor
    alignment = styled_text.get("alignment", {}).get("values", [{}])[0].get("value", 1)
    text_anchor = {
        0: "start",
        1: "middle",
        2: "end"
    }.get(alignment, "start")

    # Fill properties
    text_fill_color = styled_text.get("fillColor").get("values")[0].get("value", None)
    if text_fill_color:
        fill_color = sp.rgba_to_hex(sp.color_to_rgb_tuple(text_fill_color))
        fill_opacity = sp.color_to_rgb_tuple(text_fill_color)[3]
    else:
        fill_color = "none"
        fill_opacity = "1"

    # Style attributes
    style_parts = [
        f"display:{'none' if text_element.get('isHidden') else 'inline'}",
        f"mix-blend-mode:{sp.blend_mode_to_svg(styled_text.get('blendMode', 1))}",
        f"opacity:{styled_text.get('opacity', 1)}",
        f"fill:{fill_color}",
        f"fill-opacity:{fill_opacity}",
        f"font-family:{font_family}",
        f"font-size:{font_size}px",
        f"font-weight:{font_weight}",
        f"text-anchor:{text_anchor}"
    ]
    style = ";".join(style_parts)

    # Text content
    text_content = styled_text.get("string", "")

    # Create the text element
    attributes = {
        "id": text_element.get("name"),
        "style": style,
        "x": "0",
        "y": "0",
        "transform": tp.create_group_transform(transform)
    }
    text_svg_element = ET.Element("text", attributes)
    text_svg_element.text = text_content

    return text_svg_element, None



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
    title = artboard.get("title", "Untitled")

    # Create the SVG element
    svg_header = ET.Element("svg", {
        "width": str(width),
        "height": str(height),
        "viewBox": f"0 0 {width} {height}",
        "version": "1.1",
        "id": f"{title}",
        "xmlns:xlink": "http://www.w3.org/1999/xlink",
        "xmlns": "http://www.w3.org/2000/svg",
        "xmlns:svg": "http://www.w3.org/2000/svg",
    })

    return svg_header


def path_geometry_to_svg_path(datas):
    """Converts pathGeometry array data to svg path (d={path})."""
    svg_paths = []

    # Iterate through all path geometries
    for path_geometry in datas:
        # Convert the geometry to an SVG path and append it
        svg_paths.append(single_path_geometry_to_svg_path(path_geometry))

    # Join all path strings with spaces
    return " ".join(svg_paths)


def single_path_geometry_to_svg_path(data):
    """Converts single pathGeometry data to svg path (d={path})."""
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


def detect_image_format_and_size(base64_image):
    """Detect the image format and dimension of b64 encoded image."""
    # Decode Base64 image and convert to binary
    binary_data = base64.b64decode(base64_image)

    # Load image in Pillow
    image = Image.open(BytesIO(binary_data))

    # Get image format（JPEG, PNG） and dimension
    image_format = image.format  # 例: 'PNG'
    width, height = image.size   # 幅と高さ (ピクセル単位)

    return image_format, width, height
