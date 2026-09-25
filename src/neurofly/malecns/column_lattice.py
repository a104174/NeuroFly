"""Pinned MaleCNS optic-column lattice semantics and offline source parsing."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

OFFICIAL_COLUMN_WORKBOOK_SHA256 = (
    "d4af1cacb751036f7e84bfecc9bec79ca010066ac066559c29b566003ec080d3"
)
OFFICIAL_COLUMN_WORKBOOK_COMMIT = "67767d2233657983993ff6c2be48e836a935863c"
OFFICIAL_COLUMN_WORKBOOK_NAME = "optic-column-type-assignments-v1.0.xlsx"
OFFICIAL_COLUMN_WORKBOOK_URL = (
    "https://raw.githubusercontent.com/flyconnectome/2025malecns/"
    f"{OFFICIAL_COLUMN_WORKBOOK_COMMIT}/supplemental_data/"
    f"{OFFICIAL_COLUMN_WORKBOOK_NAME}"
)

_COLUMN_RE = re.compile(r"^ME_([LR])_col_(\d+)_(\d+)$")
_CELL_COLUMN_RE = re.compile(r"[A-Z]+")
_XML_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


class ColumnLatticeError(ValueError):
    """An optic-column coordinate or pinned workbook is invalid."""


def hex_distance(first: tuple[int, int], second: tuple[int, int]) -> int:
    """Return MaleCNS p/q lattice distance in six-neighbour steps.

    The project convention is ``hex1=q`` and ``hex2=p`` with neighbours
    ``±(1,0)``, ``±(0,1)``, and ``±(1,1)``. This is not Euclidean distance.
    """

    if (
        len(first) != 2
        or len(second) != 2
        or any(
            isinstance(value, bool) or not isinstance(value, int)
            for value in (*first, *second)
        )
    ):
        raise ColumnLatticeError("hex coordinates must be integer pairs.")
    delta_q = first[0] - second[0]
    delta_p = first[1] - second[1]
    return max(abs(delta_p), abs(delta_q), abs(delta_p - delta_q))


def _workbook_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise ColumnLatticeError("could not read the official column workbook") from exc
    return digest.hexdigest()


def load_official_columns(path: Path) -> dict[str, dict[tuple[int, int], str]]:
    """Load pinned bilateral medulla keys and their published column classes.

    Values are workbook labels only; coordinates missing from this medulla
    table may still be valid LO/LOP source coordinates and must be represented
    separately from this classification.
    """

    path = Path(path)
    if _workbook_sha256(path) != OFFICIAL_COLUMN_WORKBOOK_SHA256:
        raise ColumnLatticeError("official column workbook SHA-256 mismatch.")
    result: dict[str, dict[tuple[int, int], str]] = {"L": {}, "R": {}}
    try:
        with ZipFile(path) as workbook:
            strings_root = ElementTree.fromstring(workbook.read("xl/sharedStrings.xml"))
            shared = [
                "".join(text.text or "" for text in item.findall(".//m:t", _XML_NS))
                for item in strings_root.findall("m:si", _XML_NS)
            ]
            for side, sheet in (("R", "sheet1.xml"), ("L", "sheet2.xml")):
                root = ElementTree.fromstring(workbook.read(f"xl/worksheets/{sheet}"))
                rows = root.findall(".//m:row", _XML_NS)
                for row in rows[1:]:
                    cells: dict[str, str] = {}
                    for cell in row.findall("m:c", _XML_NS):
                        match = _CELL_COLUMN_RE.match(cell.attrib.get("r", ""))
                        if match is None:
                            raise ColumnLatticeError(
                                "official workbook has a malformed cell reference."
                            )
                        value = cell.find("m:v", _XML_NS)
                        text = "" if value is None or value.text is None else value.text
                        if cell.attrib.get("t") == "s" and text:
                            index = int(text)
                            if index < 0 or index >= len(shared):
                                raise ColumnLatticeError(
                                    "official workbook shared-string index is invalid."
                                )
                            text = shared[index]
                        cells[match.group()] = text
                    match = _COLUMN_RE.fullmatch(cells.get("A", ""))
                    if match is None or match.group(1) != side:
                        raise ColumnLatticeError(
                            "official workbook has an invalid column key or side."
                        )
                    coordinate = (int(match.group(2)), int(match.group(3)))
                    if coordinate in result[side]:
                        raise ColumnLatticeError(
                            "official workbook has a duplicate column coordinate."
                        )
                    result[side][coordinate] = cells.get("G", "")
    except (BadZipFile, KeyError, ElementTree.ParseError, ValueError) as exc:
        if isinstance(exc, ColumnLatticeError):
            raise
        raise ColumnLatticeError("official column workbook is malformed.") from exc
    if (len(result["L"]), len(result["R"])) != (880, 892):
        raise ColumnLatticeError("official bilateral column counts changed.")
    return result
