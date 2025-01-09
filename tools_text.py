"""
VI text tools

Decodes Linearity Curve texts and turn them into SVG Text.
"""


import base64
import plistlib


def decode_b64_plist(encoded_string):
    """Decodes Vectornator Text data (Binary plist encoded in base64)."""
    decoded_bplist = plistlib.loads(base64.b64decode(encoded_string))
    return decoded_bplist
