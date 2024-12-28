"""
Vectornator Inspection (2024/12/7)

description: Linearity Curve file reader(5.18.0) with tons of ChatGPT code

usage: python open_vectornator.py file.curve

what works (2024/12/28): pathGeometry -> SVG path, very primitive svg export
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
    """Open and process a Vectornator file."""
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

            print(f"Unit: {units}")  # * will be used later
            # * file format is different between 4.x and 5.x (e.g. 4.13.7 vs 5.18.0)
            check_version(version)

            if not artboard_paths:
                logging.warning("No artboard paths found in the document.")
                return

            # Step 5: Read the first Artboard (GUID JSON)
            # * Only the first one for now
            gid_json = ext.extract_gid_json(archive, artboard_paths[0])

            # I don't know what other artboards are
            artboard = gid_json.get("artboards")[0]

            layers = d.read_gid_json(gid_json)
            # print(json.dumps(gid_json, indent=4))

            exp.create_svg(artboard, layers, file)

    except zipfile.BadZipFile:
        logging.error("The provided file is not a valid ZIP archive.")
    except KeyError as e:
        logging.error(f"Required file missing in the archive: {e}")
    except ValueError as e:
        logging.error(f"Vectornator file is not supported. {e}")
    except Exception as e:
        logging.error(
            f"An unexpected error occurred: {traceback.format_exc()}")


def check_version(input_version: str):
    """check if the file version is 5.x"""
    required_version = version.parse("5.0.0")  # Linearity Curve 5.x
    current_version = version.parse(input_version)

    if current_version < required_version:
        raise ValueError(
            f"Unsupported version: {input_version}. Version 5.0.0 or up is required.")
    else:
        print(f"Supported version: {input_version}.")


if __name__ == "__main__":
    args = parser.parse_args()
    open_vectornator(args.input_file)
