"""Export BOM data from a kipy board as a list of component dicts."""

from __future__ import annotations

from typing import Dict, List, Optional

from kicad_pedal_common.footprint import get_bounding_box, get_footprints


def export_bom(board) -> List[Dict]:
    """Extract all components from a kipy board and return them as a list of
    dicts matching the manifest bom-entry schema.

    Calls get_footprints() from kicad_pedal_common.footprint, enriches each
    entry with a bounding-box outline, and returns the full list.
    Components with dnp=True are omitted; exclude_from_bom get installed=True.
    """
    fp_dicts = get_footprints(board)

    # Build a mapping from ref -> raw footprint object so we can call
    # get_bounding_box on the original kipy object.
    fp_by_ref: Dict[str, object] = {}
    try:
        for fp in board.get_footprints():
            try:
                ref = fp.reference_field.text.value
                if ref and not ref.startswith("~") and ref not in ("REF**", ""):
                    fp_by_ref[ref] = fp
            except Exception:
                pass
    except Exception:
        pass

    result: List[Dict] = []
    for fp_dict in fp_dicts:
        if fp_dict["dnp"]:
            continue

        ref = fp_dict["ref"]
        fp_obj = fp_by_ref.get(ref)
        bbox_dict = get_bounding_box(fp_obj) if fp_obj is not None else {"w": 5.0, "h": 5.0}

        entry: Dict = {
            "ref": ref,
            "value": fp_dict["value"],
            "footprint": fp_dict["footprint_id"],
            "description": "",
            "notes": "",
            "layer": fp_dict["layer"],
            "pos_x": fp_dict["pos_x"],
            "pos_y": fp_dict["pos_y"],
            "rotation": fp_dict["rotation"],
            "do_not_populate": fp_dict["dnp"],
            "exclude_from_bom": fp_dict["exclude_from_bom"],
            "outline": {"type": "bbox", "bbox": bbox_dict},
        }
        if fp_dict["exclude_from_bom"]:
            entry["installed"] = True
        result.append(entry)

    return result


def export_bom_from_adapter(adapter) -> List[Dict]:
    """Like export_bom but accepts a BoardAdapter instead of a raw kipy board.

    Used by the standalone CLI (KiutilsBoardAdapter) and any caller that already
    has a BoardAdapter instance.
    """
    fp_list = adapter.get_footprints()

    # Use adapter's bounding-box size method when available; fall back to 5×5.
    def _bbox(fp_data) -> Dict[str, float]:
        if hasattr(adapter, "get_bounding_box_size"):
            return adapter.get_bounding_box_size(fp_data)
        return {"w": 5.0, "h": 5.0}

    result: List[Dict] = []
    for fp_data in fp_list:
        if fp_data.dnp:
            continue
        if fp_data.layer != "F":
            continue

        bbox_dict = _bbox(fp_data)
        entry: Dict = {
            "ref": fp_data.ref,
            "value": fp_data.value,
            "footprint": fp_data.footprint_id,
            "description": "",
            "notes": "",
            "layer": fp_data.layer,
            "pos_x": fp_data.pos_x,
            "pos_y": fp_data.pos_y,
            "rotation": fp_data.rotation,
            "do_not_populate": fp_data.dnp,
            "exclude_from_bom": fp_data.exclude_from_bom,
            "outline": {"type": "bbox", "bbox": bbox_dict},
        }
        if fp_data.exclude_from_bom:
            entry["installed"] = True
        result.append(entry)

    return result
