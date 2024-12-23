"""
Vectornator Inspection (2024/12/7)

! lets crack the code of Vectornator files!
* with great help from ChatGPT
"""

import logging
import traceback
import zipfile

# Vectornator Inspection
import decoders as d
import exporters as exp
import extractors as ext
import tools as t


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
            artboard_paths = drawing_data.get("artboardPaths", [])
            print(f"Unit: {units}") # * will be used later

            if not artboard_paths:
                logging.warning("No artboard paths found in the document.")
                return

            # Step 5: Read the first Artboard (GUID JSON)
            # * Only the first one for now
            gid_json = ext.extract_gid_json(archive, artboard_paths[0]) # the THING!!!!

            d.read_gid_json(gid_json)

            #translation = gid_json["localTransforms"][0].get("translation")
            #converted_pathdata = t.apply_translation(
            #    gid_json["pathGeometries"][0], translation)
            #pathdata = d.path_geometry_to_svg_path(
            #    converted_pathdata)  # specify as many

            #translation2 = gid_json["localTransforms"][1].get("translation")
            #converted_pathdata2 = t.apply_translation(
            #    gid_json["pathGeometries"][1], translation2)
            #pathdata2 = d.path_geometry_to_svg_path(
            #    converted_pathdata2)  # specify as many
            #exp.create_svg(pathdata, pathdata2)

            # print(json.dumps(gid_json, indent=4))  # Pretty-print the first artboard JSON

    except zipfile.BadZipFile:
        logging.error("The provided file is not a valid ZIP archive.")
    except KeyError as e:
        logging.error(f"Required file missing in the archive: {e}")
    except Exception as e:
        logging.error(
            f"An unexpected error occurred: {traceback.format_exc()}")


if __name__ == "__main__":
    open_vectornator(
        "/Users/nozblue/Pictures/VECTORNATOR - for inspection/Pyh.curve")
