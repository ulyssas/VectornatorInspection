"""
VI decoders

converts Linearity Curve (5.x) JSON data to usable data.

Only tested for fileFormatVersion 44.

You can upgrade file format by opening vectornator file in Linearity Curve, then export as .curve.

Curve 5.18.0 ~ 5.18.4 use fileFormatVersion 44, while Curve 5.1.1 and 5.1.2 use 21.
"""


import extractors as ext


def read_gid_json(archive, gid_json):
    """
    Reads gid.json and returns simply-structured data.

    Argument `archive` is needed for image embedding.
    """
    # "layer_ids" contain layer indexes, while "layers" contain existing layers
    layer_ids = gid_json.get("artboards", [])[0].get("layerIds", [])
    layers = gid_json.get("layers", [])
    layers_result = []

    # Locate elements specified in layers.elementIds with traverse_layer
    for layer_id in layer_ids:
        layer = layers[layer_id]
        layers_result.append(
            traverse_layer(archive, gid_json, layer))

    return layers_result


def traverse_layer(archive, gid_json, layer):
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
                traverse_element(archive, gid_json, element))

    return layer_result


def traverse_element(archive, gid_json, element):
    """Traverse specified element and extract their attributes."""

    # easier-to-process data structure
    element_result = {
        "name": element.get("name", "Unnamed Element"),
        "isHidden": element.get("isHidden", False),
        # isLocked requires sodipodi:insensitive
        "opacity": element.get("opacity", 1),
        "blendMode": element.get("blendMode", 0),
        "blur": element.get("blur", 0),
        "localTransform": None,
        "imageData": None,  # will be base64 string
        "styledText": None,  # from styledTexts
        "textProperty": None,  # from texts
        "singleStyle": None,
        "strokeStyle": None,  # what is fillRule/strokeType?
        "fill": None,
        "fillId": None,
        "pathGeometry": [],  # array because compoundPath
        "groupElements": []  # store group elements
    }

    # localTransform
    local_transform_id = element.get("localTransformId")
    if local_transform_id is not None:
        element_result["localTransform"] = get_local_transform(
            gid_json, local_transform_id)

    # Image
    image_id = element.get("subElement", {}).get("image", {}).get("_0")
    if image_id is not None:
        # relativePath contains *.dat (bitmap data)
        # sharedFileImage doesn't exist in 5.1.1 (file version 21) document
        image = get_image(gid_json, image_id).get(
            "imageData", {}).get("sharedFileImage", {}).get("_0")
        image_data = get_image_data(gid_json, image).get("relativePath", "")
        element_result["imageData"] = ext.read_dat_from_zip(
            archive, image_data)

    # Stylable
    stylable_id = element.get("subElement", {}).get("stylable", {}).get("_0")
    if stylable_id is not None:
        stylable = get_stylable(gid_json, stylable_id)

        # Abstract Path
        abstract_path_id = stylable.get("subElement", {}).get(
            "abstractPath", {}).get("_0")
        if abstract_path_id is not None:
            abstract_path = get_abstract_path(gid_json, abstract_path_id)

            # Stroke Style
            stroke_style_id = abstract_path.get("strokeStyleId")
            if stroke_style_id is not None:
                element_result["strokeStyle"] = get_stroke_style(
                    gid_json, stroke_style_id)

            # fill
            fill_id = abstract_path.get("fillId")
            if fill_id is not None:
                element_result["fill"] = get_fill(gid_json, fill_id)
                element_result["fillId"] = fill_id

            # Path
            path_id = abstract_path.get(
                "subElement", {}).get("path", {}).get("_0")
            if path_id is not None:
                path = get_path(gid_json, path_id)

                # Path Geometry
                geometry_id = path.get("geometryId")
                if geometry_id is not None:
                    path_geometry = get_path_geometries(gid_json, geometry_id)
                    element_result["pathGeometry"].append(path_geometry)

            # compoundPath
            compound_path_id = abstract_path.get(
                "subElement", {}).get("compoundPath", {}).get("_0")
            if compound_path_id is not None:
                compound_path = get_compound_path(gid_json, compound_path_id)

                # Path Geometries (subpath)
                subpath_ids = compound_path.get("subpathIds", [])
                if subpath_ids is not None:
                    for id in subpath_ids:
                        path_geometry = get_path_geometries(gid_json, id)
                        element_result["pathGeometry"].append(path_geometry)

        # Abstract Text
        abstract_text_id = stylable.get("subElement", {}).get(
            "abstractText", {}).get("_0")
        if abstract_text_id is not None:
            abstract_text = get_abstract_text(gid_json, abstract_text_id)
            text_id = abstract_text.get("textId")
            styled_text_id = abstract_text.get(
                "subElement", {}).get("text", {}).get("_0")

            # texts(layout)
            if text_id is not None:
                element_result["textProperty"] = get_text_property(
                    gid_json, text_id)  # from texts

            # styledTexts
            if styled_text_id is not None:
                element_result["styledText"] = get_styled_text(
                    gid_json, styled_text_id)  # from styledTexts

        #! singleStyle (NON-EXISTENT in latest format, found in fileVersion 21)
        single_style_id = stylable.get("subElement", {}).get(
            "singleStyle", {}).get("_0")
        if single_style_id is not None:
            single_style = get_single_style(gid_json, single_style_id)
            element_result["singleStyle"] = single_style
            # TODO Add lines later

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
                    traverse_element(archive, gid_json, group_element))

    return element_result


def vectornator_to_artboard(gid_json):
    """Reads Vectornator gid.json and returns Curve artboard."""
    return {
        "title": gid_json.get("title", "Untitled"),
        "activeLayerIndex": gid_json.get("activeLayerIndex", 0),
        "frame": gid_json.get("frame", {}),
        "gid": gid_json.get("gid", "")
    }


# get_(name) functions
# could be incorporated into Object(will happen when inkex rewrite)


def get_element(gid_json, index):
    """Get element from gid_json."""
    elements = gid_json.get("elements", [])
    return elements[index]


def get_local_transform(gid_json, index):
    """Get localTransform from gid_json."""
    local_transforms = gid_json.get("localTransforms", [])
    return local_transforms[index]


def get_image(gid_json, index):
    """Get image from gid_json."""
    images = gid_json.get("images", [])
    return images[index]


def get_image_data(gid_json, index):
    """Get imageData from gid_json."""
    image_datas = gid_json.get("imageDatas", [])
    return image_datas[index]


def get_text_property(gid_json, index):
    """Get text(textProperty) from gid_json."""
    text_property = gid_json.get("texts", [])
    return text_property[index]


def get_styled_text(gid_json, index):
    """Get styledText from gid_json."""
    styled_text = gid_json.get("styledTexts", [])
    return styled_text[index]


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


def get_abstract_text(gid_json, index):
    """Get abstractText from gid_json."""
    abstract_texts = gid_json.get("abstractTexts", [])
    return abstract_texts[index]


def get_single_style(gid_json, index):
    """Get singleStyle from gid_json."""
    single_styles = gid_json.get("singleStyles", [])
    return single_styles[index]


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
