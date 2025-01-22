"""
VI text tools

Decodes Linearity Curve texts and turn them into SVG Text.

I realized that this Base64&Bplist data is not used in latest format(44).

This is great because I don't have to decode the data.

But, I must work on this at some point, because Vectornator uses this data format.
"""


import base64
import copy
import datetime
import plistlib
from typing import Any, Dict

#import inkex


def decode_b64_plist(encoded_string):
    """
    Decodes Vectornator Text data (Binary plist encoded in base64).
    """
    decoded_bplist = plistlib.loads(base64.b64decode(encoded_string))
    return decoded_bplist


def get_text_anchor(alignment_value):
    """
    alignment to SVG text-anchor

    0: Left
    1: Right
    2: Right
    3: Justify
    """
    return {
        0: "start",
        1: "middle",
        2: "end"
    }.get(alignment_value, "start")


# add vectornator / curve import by @joneuhauser
#def parse_text(self, obj: Dict[str, Any]) -> inkex.TextElement:
#    result = inkex.TextElement()
#    # Parse binary-encoded text
#    text_data = unserializeNSKeyedArchiver(
#        base64.b64decode(obj["attributedText"])
#    )
#    result.text = text_data["NSString"]
#    print(
#        repr(text_data["NSString"]),
#        text_data.get("NSAttributeInfo"),
#        len(text_data["NSAttributes"]),
#    )
#    result.transform = inkex.Transform(obj["transform"])
#    result.set("xml:space", "preserve")
#    # TODO: It is unclear what NSAttributeInfo contains.
#    # The first 2 bytes seem to encode the number of characters that the first style
#    # is applied to, LE encoded
#    # For now we just set the first style to the entire text
#    style = (
#        text_data["NSAttributes"][0]
#        if isinstance(text_data["NSAttributes"], list)
#        else text_data["NSAttributes"]
#    )
#    result.style["font"] = style["NSFont"]["NSName"]
#    result.style["font-size"] = f"{style['NSFont']['NSSize']}px"

#    return result


# This file is copied from
# https://github.com/avibrazil/NSKeyedUnArchiver
# LGPL3

def _unserialize(o: dict, serialized: dict, removeClassName: bool, start: bool = True):
    if start:
        reassembled = copy.deepcopy(o)
    else:
        reassembled = o

    finished = False
    while not finished:
        finished = True

        cursor = None
        if isinstance(reassembled, bytes):
            try:
                return unserializeNSKeyedArchiver(reassembled)
            except:
                # Not plist data, just plain binary
                return reassembled
        elif isinstance(reassembled, dict):
            cursor = reassembled.keys()
        elif isinstance(reassembled, list):
            cursor = range(len(reassembled))
        else:  # str, int etc
            print("reassembled is a " +
                  str(type(reassembled)) + ":" + str(reassembled))
            return reassembled

        for k in cursor:
            #             print(f"cursor={k}")
            if isinstance(reassembled[k], plistlib.UID):
                reassembled[k] = copy.deepcopy(serialized[reassembled[k].data])

                if str(reassembled[k]) == "$null":
                    reassembled[k] = None

                finished = False
            elif isinstance(reassembled[k], dict) or isinstance(reassembled[k], list):
                reassembled[k] = _unserialize(
                    reassembled[k], serialized, removeClassName, start=False
                )

                if (
                    "$class" in reassembled[k]
                    and "$classes" in reassembled[k]["$class"]
                ):
                    # Specialized handler for common class types

                    if "NSArray" in reassembled[k]["$class"]["$classes"]:
                        reassembled[k] = reassembled[k]["NS.objects"]

                    elif any(
                        c in reassembled[k]["$class"]["$classes"]
                        for c in ["NSMutableDictionary", "NSDictionary"]
                    ):
                        reassembled[k] = dict(
                            zip(reassembled[k]["NS.keys"],
                                reassembled[k]["NS.objects"])
                        )

                    elif any(
                        c in reassembled[k]["$class"]["$classes"]
                        for c in ["NSMutableString", "NSString"]
                    ):
                        reassembled[k] = reassembled[k]["NS.string"]

                    elif any(
                        c in reassembled[k]["$class"]["$classes"]
                        for c in ["NSMutableData", "NSData"]
                    ):
                        reassembled[k] = reassembled[k]["NS.data"]

                    elif "NSDate" in reassembled[k]["$class"]["$classes"]:
                        apple2001reference = datetime.datetime(
                            2001, 1, 1, tzinfo=datetime.timezone.utc
                        )
                        reassembled[k] = datetime.datetime.fromtimestamp(
                            reassembled[k]["NS.time"] +
                            apple2001reference.timestamp(),
                            datetime.timezone.utc,
                        )

                    if removeClassName:
                        # Remove visual polution
                        del reassembled[k]["$class"]

                finished = True

    return reassembled


def unserializeNSKeyedArchiver(plist, removeClassName=True):
    """
    plist can be:
    • PurePath   ⟹ open the file and plistlib.loads()
    • string     ⟹ check if its a file name, open it and plistlib.loads()
    • string     ⟹ try to read it as XML with plistlib.loads()
    • bytes      ⟹ pass it through plistlib.loads()
    • dict       ⟹ unserialize
    """

    if isinstance(plist, bytes):
        plistdata = plistlib.loads(plist)
    elif isinstance(plist, dict):
        # plist is already a plistlib-parsed dict
        plistdata = plist
    else:
        raise TypeError(
            "Trying to plist-parse something that is neither a PurePath, file name, XML text, plist bytes stream nor a dict."
        )

    if "$top" in plistdata:
        o = copy.deepcopy(plistdata["$top"])
        unserialized = _unserialize(o, plistdata["$objects"], removeClassName)
    else:
        raise TypeError("Passed object is not an NSKeyedArchiver")

    if len(unserialized) == 1 and "root" in unserialized:
        # Unserialized data contains only 1 object, so no need to nest it under 'root'
        unserialized = unserialized["root"]

    return unserialized
