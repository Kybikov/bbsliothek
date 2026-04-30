from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any, Iterable


def _normalize_row(row: Any) -> dict[str, str]:
    if is_dataclass(row):
        source = asdict(row)
    elif isinstance(row, dict):
        source = row
    else:
        source = vars(row)

    normalized: dict[str, str] = {}
    for key, value in source.items():
        if isinstance(value, datetime):
            normalized[key] = value.strftime("%Y-%m-%d %H:%M:%S")
        else:
            normalized[key] = "" if value is None else str(value)
    return normalized


def render_table(rows: Iterable[Any]) -> str:
    rows = list(rows)
    if not rows:
        return "Keine Daten vorhanden."

    normalized_rows = [_normalize_row(row) for row in rows]
    columns = list(normalized_rows[0].keys())
    widths = {column: len(column) for column in columns}

    for row in normalized_rows:
        for column in columns:
            widths[column] = max(widths[column], len(row[column]))

    header = " | ".join(column.ljust(widths[column]) for column in columns)
    separator = "-+-".join("-" * widths[column] for column in columns)
    lines = [header, separator]
    for row in normalized_rows:
        lines.append(" | ".join(row[column].ljust(widths[column]) for column in columns))
    return "\n".join(lines)
