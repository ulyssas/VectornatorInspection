"""
VI exporters

outputs svg file.
"""


import xml.etree.ElementTree as ET


def create_svg(svg_path, second_svg_path):
    # SVG header
    svg = ET.Element("svg", {
        "width": "3024",
        "height": "1964",
        "viewBox": "0 0 3024 1964",
        "version" : "1.1",
        "xmlns": "http://www.w3.org/2000/svg"
    })

    # comment
    comment = ET.Comment("Generated with Vectornator Inspection")
    svg.append(comment)

    # 最初のパス
    path1 = ET.Element("path", {
        "id": "Path",
        "fill": "none",
        "stroke": "#ff8585",
        "stroke-width": "3",
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
        "d": svg_path
    })
    svg.append(path1)

    # 2番目のパス
    path2 = ET.Element("path", {
        "id": "Path",
        "fill": "none",
        "stroke": "#ff8585",
        "stroke-width": "3",
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
        "d": second_svg_path
    })
    svg.append(path2)

    # ツリーを構築して保存
    file_path = "/Users/nozblue/Pictures/VECTORNATOR - for inspection/tuning.svg"
    tree = ET.ElementTree(svg)
    tree.write(file_path, encoding="UTF-8", xml_declaration=True)
