"""
Vectornator Inspection (2024/12/7)

description: Linearity Curve file reader(5.18.x) with tons of AI code

usage: python open_vectornator.py file.curve

what works (2025/01/09): limited SVG export (no text, other units)
"""

import argparse
import logging
import traceback
import zipfile

from packaging import version

# Vectornator Inspection
import decoders as d
import exporters as exp
import extractors as ext

parser = argparse.ArgumentParser(description='Linearity Curve file reader')

parser.add_argument('input_file', help='Linearity Curve file')


def open_vectornator(file):
    """
    Open and process a Linearity Curve (.curve) file.

    Vectornator (.vectornator) file is not supported.

    You can upgrade file format by opening vectornator file in Linearity Curve, then export as .curve.
    """
    try:
        with zipfile.ZipFile(file, 'r') as archive:
            # Step 1: Read Manifest
            manifest = ext.extract_manifest(archive)

            # Step 2: Read Document
            document = ext.extract_document(archive, manifest)

            # Step 3: Extract Drawing Data
            drawing_data = ext.extract_drawing_data(document)

            # Step 4: Process Units and Artboards
            units = drawing_data.get("settings", {}).get("units", "Pixels")
            version = document.get("appVersion", "unknown app version")
            artboard_paths = drawing_data.get("artboardPaths", [])

            # will be used later (as Inkscape attribute)
            print(f"Unit: {units}")

            if not artboard_paths:
                logging.warning("No artboard paths found in the document.")
                return

            # Step 5: Read Artboard (GUID JSON)
            # If there's multiple artboards, only the first will be exported.
            gid_json = ext.extract_gid_json(archive, artboard_paths[0])

            # if the file is Linearity Curve
            if check_if_curve(version):
                print(f"Supported version: {version}.")
                artboard = gid_json.get("artboards")[0]
                layers = d.read_gid_json(archive, gid_json)
                ext.read_dat_from_zip

            # if the file is Vectornator
            else:
                # Does not work yet
                # artboard = d.vectornator_to_artboard(gid_json)
                # layers = gid_json.get("layers", [])
                raise ValueError(
                    f"Unsupported version: {version}. Version 5.0.0 or up is required.")

            # print(json.dumps(gid_json, indent=4))

            exp.create_svg(artboard, layers, file)

    except zipfile.BadZipFile:
        logging.error("The provided file is not a valid ZIP archive.")
    except KeyError as e:
        logging.error(f"Required file missing in the archive: {e}")
    except ValueError as e:
        logging.error(
            f"An error occurred while reading file. {traceback.format_exc()}")
    except NotImplementedError as e:
        logging.error(f"File contains unsupported feature. {e}")
    except Exception as e:
        logging.error(
            f"An unexpected error occurred: {traceback.format_exc()}")


def check_if_curve(input_version: str):
    """check if the file version is 5.x or not"""
    required_version = version.parse("5.0.0")
    current_version = version.parse(input_version)

    if current_version < required_version:
        return False
    else:
        return True


if __name__ == "__main__":
    args = parser.parse_args()
    open_vectornator(args.input_file)
