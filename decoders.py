"""
VI decoders

converts Vectornator JSON data to usable data.
"""


import base64
import json
import plistlib


def read_gid_json(gid_json):
    """Reads gid.json and returns simply-structured data."""
    # "layer_ids" contain layer indexes, while "layers" contain existing layers
    layer_ids = gid_json.get("artboards", [])[0].get("layerIds", [])
    layers = gid_json.get("layers", [])
    layers_result = []

    # Locate elements specified in layers.elementIds with traverse_layer
    for layer_id in layer_ids:
        layer = layers[layer_id]
        layers_result.append(
                traverse_layer(gid_json, layer))

    print(layers_result)

    return layers_result


def traverse_layer(gid_json, layer):
    """Traverse specified layer and extract their attributes."""
    layer_element_ids = layer.get("elementIds", [])
    layer_result = {
        "name": layer.get("name", "Unnamed Layer"),
        "opacity": layer.get("opacity", 1),
        "isVisible": layer.get("isVisible", True),
        "isLocked": layer.get("isLocked", False),
        "isExpanded": layer.get("isExpanded", False),
        "elements": []  # store elements inside the layer
    }
    # process each elements
    for element_id in layer_element_ids:
        element = get_element(gid_json, element_id)
        if element:
            layer_result["elements"].append(
                    traverse_element(gid_json, element))

    return layer_result


def traverse_element(gid_json, element):
    """Traverse specified element and extract their attributes."""

    # easier-to-process data structure
    element_result = {
        "name": element.get("name", "Unnamed Element"),
        "blendMode": element.get("blendMode", 0),
        "isHidden": element.get("isHidden", False),
        # isLocked requires sodipodi:insensitive
        "opacity": element.get("opacity", 1),
        "localTransform": None,
        "stylable": None,
        "abstractPath": None,
        "strokeStyle": None, # what is fillRule/strokeType?
        "fill": None,
        "pathGeometry": [],
        "groupElements": []  # store group elements
    }

    # localTransform
    local_transform_id = element.get("localTransformId")
    if local_transform_id is not None:
        element_result["localTransform"] = get_local_transform(gid_json, local_transform_id)

    # Stylable
    stylable_id = element.get("subElement", {}).get("stylable", {}).get("_0")
    if stylable_id is not None:
        stylable = get_stylable(gid_json, stylable_id)
        element_result["stylable"] = stylable

        # Abstract Path
        abstract_path_id = stylable.get("subElement", {}).get("abstractPath", {}).get("_0")
        if abstract_path_id is not None:
            abstract_path = get_abstract_path(gid_json, abstract_path_id)
            element_result["abstractPath"] = abstract_path

            # Stroke Style
            stroke_style_id = abstract_path.get("strokeStyleId")
            if stroke_style_id is not None:
                stroke_style = get_stroke_style(gid_json, stroke_style_id)
                element_result["strokeStyle"] = stroke_style

            # fill
            fill_id = abstract_path.get("fillId")
            if fill_id is not None:
                fill = get_fill(gid_json, fill_id)
                element_result["fill"] = fill

            # Path
            path_id = abstract_path.get("subElement", {}).get("path", {}).get("_0")
            if path_id is not None:
                path = get_path(gid_json, path_id)

                # Path Geometry
                geometry_id = path.get("geometryId")
                if geometry_id is not None:
                    path_geometry = get_path_geometries(gid_json, geometry_id)
                    element_result["pathGeometry"].append(path_geometry)

            # compoundPath
            compound_path_id = abstract_path.get("subElement", {}).get("compoundPath", {}).get("_0")
            if compound_path_id is not None:
                compound_path = get_compound_path(gid_json, compound_path_id)

                # Path Geometries (subpath)
                subpath_ids = compound_path.get("subpathIds", [])
                if subpath_ids is not None:
                    for id in subpath_ids:
                        path_geometry = get_path_geometries(gid_json, id)
                        element_result["pathGeometry"].append(path_geometry)

    # Group
    group_id = element.get("subElement", {}).get("group", {}).get("_0")
    if group_id is not None:
        # get elements inside group
        group = get_group(gid_json, group_id)
        group_element_ids = group.get("elementIds", [])
        for group_element_id in group_element_ids:
            group_element = get_element(gid_json, group_element_id)
            if group_element:
                # get group elements recursively
                element_result["groupElements"].append(
                    traverse_element(gid_json, group_element))

    return element_result


def decode_b64_plist(encoded_string):
    """Decodes Vectornator Text data (Binary plist encoded in base64)."""
    decoded_bplist = plistlib.loads(base64.b64decode(encoded_string))
    return decoded_bplist


def get_element(gid_json, index):
    """Get element from gid_json."""
    elements = gid_json.get("elements", [])
    return elements[index]


def get_local_transform(gid_json, index):
    """Get localTransform from gid_json."""
    local_transforms = gid_json.get("localTransforms", [])
    return local_transforms[index]


def get_stylable(gid_json, index):
    """Get stylable from gid_json."""
    stylables = gid_json.get("stylables", [])
    return stylables[index]


def get_group(gid_json, index):
    """Get group from gid_json."""
    groups = gid_json.get("groups", [])
    return groups[index]


def get_abstract_path(gid_json, index):
    """Get abstractPath from gid_json."""
    abstract_paths = gid_json.get("abstractPaths", [])
    return abstract_paths[index]


def get_stroke_style(gid_json, index):
    """Get pathStrokeStyle from gid_json."""
    stroke_styles = gid_json.get("pathStrokeStyles", [])
    return stroke_styles[index]


def get_fill(gid_json, index):
    """Get fill from gid_json."""
    fills = gid_json.get("fills", [])
    return fills[index]


def get_path(gid_json, index):
    """Get path from gid_json."""
    paths = gid_json.get("paths", [])
    return paths[index]


def get_compound_path(gid_json, index):
    """Get compoundPath from gid_json."""
    compound_paths = gid_json.get("compoundPaths", [])
    return compound_paths[index]


def get_path_geometries(gid_json, index):
    """Get pathGeometry from gid_json."""
    path_geometries = gid_json.get("pathGeometries", [])
    return path_geometries[index]
