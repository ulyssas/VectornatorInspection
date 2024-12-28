"""
Vectornator Inspection (2024/12/7)

description: Linearity Curve file reader(5.18.0) with tons of ChatGPT code

what works (2024/12/28): pathGeometry -> SVG path, very primitive svg export
"""

import logging
import traceback
import zipfile

# Vectornator Inspection
import decoders as d
import exporters as exp
import extractors as ext


# main
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

            print(f"Unit: {units}") # * will be used later
            print(f"Version: {version}") # * file format is different between 4.x and 5.x (4.13.7 vs 5.18.0)

            if not artboard_paths:
                logging.warning("No artboard paths found in the document.")
                return

            # Step 5: Read the first Artboard (GUID JSON)
            # * Only the first one for now
            gid_json = ext.extract_gid_json(archive, artboard_paths[0])

            # I don't know what other artboards are
            artboard = gid_json.get("artboards")[0]

            layers = d.read_gid_json(gid_json)
            #print(json.dumps(gid_json, indent=4))

            exp.create_svg(artboard, layers)

    except zipfile.BadZipFile:
        logging.error("The provided file is not a valid ZIP archive.")
    except KeyError as e:
        logging.error(f"Required file missing in the archive: {e}")
    except Exception as e:
        logging.error(
            f"An unexpected error occurred: {traceback.format_exc()}")


if __name__ == "__main__":
    open_vectornator(
        "/Users/nozblue/Pictures/VECTORNATOR - for inspection/IlluminasMENU.vectornator")
