"""
VI path styles

Converts non-text styles into svg styles.
"""


import colorsys


def decode_stroke_style(stroke_style):
    """
    Returns processed pathStrokeStyle.

    fillRule/strokeType?
    "basicStrokeStyle": {
        "cap": 0,  # ! 0: butt,  1: round, 2: square
        "join": 1, # ! 0: miter, 1: round, 2: bevel
        "position": 0 # ! -1: inner, 0: center, 1: outside not possible in SVG 1.1?

        "dashPattern": [ # ??????????????????
            26, # Dash
            9,  # Dash
            16, # Gap
            5   # Gap
        ],
    },
    """
    basic_style = stroke_style.get("basicStrokeStyle")
    color = stroke_style.get("color")
    width = stroke_style.get("width")

    stroke_style_result = {
        "stroke": color_to_rgb_tuple(color),
        "stroke-width": str(width),
        "stroke-linecap": cap_to_svg(basic_style.get("cap",  0)),
        "stroke-dasharray": None,
        "stroke-linejoin": join_to_svg(basic_style.get("join",  1))
    }

    return stroke_style_result


def cap_to_svg(cap):
    """Returns value for stroke-linecap attribute."""
    match cap:
        case 0:
            return "butt"
        case 1:
            return "round"
        case 2:
            return "square"
        case _:
            return "butt"


def join_to_svg(join):
    """Returns value for stroke-linejoin attribute."""
    match join:
        case 0:
            return "miter"
        case 1:
            return "round"
        case 2:
            return "bevel"
        case _:
            return "miter"


def color_to_rgb_tuple(color):
    """Converts color into string."""
    rgba = color.get("rgba")
    hsba = color.get("hsba")

    if rgba is not None:
        return rgba_to_tuple(rgba)

    elif hsba is not None:
        return hsba_to_rgba(hsba)


def hsba_to_rgba(hsba):
    """
    Converts an HSBA color to RGBA format.

    Args:
        hsba (dict): A dictionary with the keys "hue", "saturation", "brightness", and "alpha".
            - "hue" (float): Hue value (0.0 to 1.0).
            - "saturation" (float): Saturation value (0.0 to 1.0).
            - "brightness" (float): Brightness value (0.0 to 1.0).
            - "alpha" (float): Alpha value (0.0 to 1.0).

    Returns:
        tuple: A tuple of (red, green, blue, alpha), each as a float between 0.0 and 1.0.
    """
    hue = hsba.get("hue", 0)
    saturation = hsba.get("saturation", 0)
    brightness = hsba.get("brightness", 0)
    alpha = hsba.get("alpha", 1)

    # Convert HSB to RGB
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, brightness)

    # Return RGBA as formatted string (Example: rgba(255, 0, 0, 0.5))
    return f"rgba({r*255}, {g*255}, {b*255}, {alpha})"


def rgba_to_tuple(rgba):
    """
    Converts an RGBA color to Tuple format.

    Args:
        hsba (dict): A dictionary with the keys "red", "green", "blue", and "alpha".
            - "red" (float): Red value (0.0 to 1.0).
            - "green" (float): Green value (0.0 to 1.0).
            - "blue" (float): Blue value (0.0 to 1.0).
            - "alpha" (float): Alpha value (0.0 to 1.0).

    Returns:
        tuple: A tuple of (red, green, blue, alpha), each as a float between 0.0 and 1.0.
    """
    red = rgba.get("red", 0)
    green = rgba.get("green", 0)
    blue = rgba.get("blue", 0)
    alpha = rgba.get("alpha", 1)

    # Return RGBA as formatted string (Example: rgba(255, 0, 0, 0.5))
    return f"rgba({red*255}, {green*255}, {blue*255}, {alpha})"
