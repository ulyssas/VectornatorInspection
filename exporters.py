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
import tools_text as tt


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
    Converts an element defined in VI Decoders.traverse_element() to an SVG text with multiple tspans for styled text.
    """
    styled_text = text_element.get("styledText", {})
    transform = text_element.get("localTransform", {})
    string = styled_text.get("string", "")

    style_properties = {
        "fontName": {"values": styled_text.get("fontName", {}).get("values", []), "default": "sans-serif"},
        "fontSize": {"values": styled_text.get("fontSize", {}).get("values", []), "default": 16},
        "fillColor": {"values": styled_text.get("fillColor", {}).get("values", []), "default": None},
        "alignment": {"values": styled_text.get("alignment", {}).get("values", []), "default": 0},
    }

    attributes = {
        "id": text_element.get("name", ""),
        "transform": tp.create_group_transform(transform, keep_proportion=True),
        "y": "0"
    }
    text_svg_element = ET.Element("text", attributes)

    current_index = 0
    last_upper_bound = 0
    current_styles = {}
    current_x = 0 # 現在の x 座標を追跡
    previous_tspan_length = 0 # 直前の tspan の文字数を追跡

    while current_index < len(string):
        next_upper_bound = len(string)
        segment_styles = {}

		# check the range of style
        for style_name, style_data in style_properties.items():
            current_value = style_data["default"] # set the default value
            for range_item in style_data["values"]:
                if last_upper_bound < range_item["upperBound"]:
                    current_value = range_item["value"]
                    next_upper_bound = min(next_upper_bound, range_item["upperBound"])
                    break
            segment_styles[style_name] = current_value

        segment_text = string[current_index:next_upper_bound]

        lines = segment_text.split('\n')
        for i, line in enumerate(lines):
            if not line and i < len(lines) -1 :
                tspan = create_svg_tspan("", segment_styles, is_new_line=True) # 空行の場合はテキストなしで tspan 生成
                text_svg_element.append(tspan)
                current_x = 0
                continue

            is_new_line = i > 0 # 2行目以降は改行後の行
            tspan = create_svg_tspan(line, segment_styles, is_new_line=is_new_line)
            text_svg_element.append(tspan)

            # 次の tspan の x 座標を更新 (簡易的な幅計算)
            # ここではフォントサイズを基準に概算で幅を計算 (調整が必要な場合があります)
             # **修正点:** 次の tspan の x 座標を文字数とフォントサイズから計算
            current_x += segment_styles["fontSize"] * 0.5 * len(line) # 係数を 0.5 に調整 (微調整が必要な場合あり)
            previous_tspan_length = len(line)

        current_index = next_upper_bound
        last_upper_bound = next_upper_bound
        if "\n" in segment_text: # 改行があったら x 座標をリセット
            current_x = 0

    return text_svg_element, None


def create_svg_tspan(text, styles, is_new_line=False):
    """
    Generates tspan data from text and its style.

    Args:
        text (str): text data.
        styles (dict): style data (fillColor, fontName, fontSize, alignment).
        is_new_line (bool): new line or not.

    Returns:
        xml.etree.ElementTree.Element: generated tspan.
    """
    tspan_style_str = ""
    if styles.get("fillColor"):
        fill_color_data = styles["fillColor"]
        fill_color_hex = sp.rgba_to_hex(sp.color_to_rgb_tuple(fill_color_data))
        fill_opacity = str(sp.color_to_rgb_tuple(fill_color_data)[3])
        tspan_style_str += f"fill:{fill_color_hex};fill-opacity:{fill_opacity};"
    tspan_style_str += f"font-family:{styles['fontName']};font-size:{styles['fontSize']}px;text-anchor:{tt.get_text_anchor(styles['alignment'])};"

    tspan_attributes = {"style": tspan_style_str, "x": "1em"}
    if is_new_line:
        tspan_attributes["dy"] = "1em" # potential issue
    tspan = ET.Element("tspan", tspan_attributes)
    tspan.text = text
    return tspan


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
