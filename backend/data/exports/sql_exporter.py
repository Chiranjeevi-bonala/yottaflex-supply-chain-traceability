import os
import json
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Any

def _json_default(obj):
    """JSON serializer for Decimal and datetime/date objects."""
    if isinstance(obj, (Decimal,)):
        # Convert Decimal to float; using float preserves numeric literal
        return float(obj) if obj == obj.to_integral() else float(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def escape_sql_value(val):
    """Escape a Python value for safe insertion into an SQL literal.
    Handles None, booleans, numbers, dates, dicts/lists, and strings.
    """
    # NULL
    if val is None:
        return "NULL"
    # Booleans (must be before int because bool is subclass of int)
    if isinstance(val, bool):
        return "TRUE" if val else "FALSE"
    # Integers
    if isinstance(val, int) and not isinstance(val, bool):
        return str(val)
    # Decimals
    if isinstance(val, Decimal):
        return str(val)
    # Floats – ensure finite
    if isinstance(val, float):
        if not (val == val and abs(val) != float('inf')):
            raise ValueError(f"Non-finite float value {val} cannot be exported to SQL")
        return str(val)
    # Dates / datetimes
    if isinstance(val, (date, datetime)):
        return f"'{val.isoformat()}'"
    # Dictionaries or lists – serialize to JSON then quote
    if isinstance(val, (dict, list)):
        json_str = json.dumps(val, default=_json_default)
        escaped = json_str.replace("'", "''")
        return f"'{escaped}'"
    # Strings – escape apostrophes and quote
    clean = str(val).replace("'", "''")
    return f"'{clean}'"

def export_to_sql_seed(data_dict: Dict[str, List[Dict[str, Any]]], output_file: str):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("-- ============================================================\n")
        f.write("-- YottaFlex Supply Chain Traceability - SQL Seed Data\n")
        f.write("-- Generated with fixed seed: 20261022\n")
        f.write("-- ============================================================\n\n")

        for table_name, rows in data_dict.items():
            if not rows:
                continue
            # Validate uniform columns across rows
            reference_keys = set(rows[0].keys())
            for idx, row in enumerate(rows[1:], start=2):
                if set(row.keys()) != reference_keys:
                    raise ValueError(
                        f"Row {idx} in table '{table_name}' has mismatched columns. "
                        f"Expected columns: {sorted(reference_keys)}; got: {sorted(row.keys())}"
                    )
            cols = list(rows[0].keys())
            f.write(f"-- Table: {table_name} ({len(rows)} rows)\n")

            for row in rows:
                vals = [escape_sql_value(row.get(c)) for c in cols]
                cols_str = ", ".join(cols)
                vals_str = ", ".join(vals)
                f.write(f"INSERT INTO {table_name} ({cols_str}) VALUES ({vals_str});\n")
            f.write("\n")
    print(f"Exported SQL seed script to {output_file}")
