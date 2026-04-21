"""CLI entry point for manifest_creator.

Usage:
    python -m manifest_creator --board foo.kicad_pcb --out foo.manifest.zip --version 1.0.0

When kiutils is installed (pip install kiutils), full BOM and footprint geometry
are exported from the .kicad_pcb file directly — no live KiCad session required.
Without kiutils, only SVG layers are exported.
"""

from __future__ import annotations

import argparse
import sys

from manifest_creator.packager import create_manifest_zip


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="manifest_creator",
        description=(
            "Export a KiCad board as a .manifest.zip (SVG layers only). "
            "For full BOM export, use the KiCad IPC plugin."
        ),
    )
    parser.add_argument(
        "--board",
        required=True,
        metavar="PATH",
        help="Path to the .kicad_pcb file",
    )
    parser.add_argument(
        "--out",
        required=True,
        metavar="PATH",
        help="Output path for the .manifest.zip file",
    )
    parser.add_argument(
        "--version",
        required=True,
        metavar="VERSION",
        help="Board version string, e.g. 1.0.0",
    )
    parser.add_argument(
        "--display-name",
        default=None,
        metavar="NAME",
        help="Human-readable board name (defaults to board file stem)",
    )
    parser.add_argument(
        "--kicad-cli",
        default=None,
        metavar="PATH",
        help="Explicit path to kicad-cli (auto-detected if omitted)",
    )
    args = parser.parse_args(argv)

    def _log(msg: str) -> None:
        print(msg, file=sys.stderr)

    # Use KiutilsBoardAdapter for full headless export when kiutils is available.
    _adapter = None
    try:
        from kicad_pedal_common.kiutils_board_adapter import KiutilsBoardAdapter
        _adapter = KiutilsBoardAdapter(args.board)
        _log("Using kiutils adapter for full BOM export")
    except ImportError:
        _log("kiutils not available — exporting SVG layers only")
    except Exception as exc:
        _log("WARNING: kiutils adapter failed ({}); SVG-only mode".format(exc))

    try:
        out = create_manifest_zip(
            board=None,
            board_path=args.board,
            output_path=args.out,
            version=args.version,
            display_name=args.display_name,
            kicad_cli=args.kicad_cli,
            log=_log,
            adapter=_adapter,
        )
        print(out)
    except Exception as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
