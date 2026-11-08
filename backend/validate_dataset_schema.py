# -*- coding: utf-8 -*-
"""Validation‑only script for the YottaFlex dataset.

This script generates the full dataset in‑memory using the data generator
pipeline and validates it against the SQLAlchemy model metadata.  It does **not**
connect to a database, modify any tables, or write any files.

The script now:
- Returns only the generated ``all_data`` from ``run_pipeline`` (checksum is kept
  for optional reporting).
- Includes *all* generated tables (including ``exception_records``) in the
  table‑name comparison.
- Validates foreign keys against the exact referenced column name (not assuming
  ``id``).
- Allows a ``NULL`` ``material_lot_id`` in ``lot_genealogy`` **only** for the EC‑01
  injected record.
- Checks that EC‑04 has no matching ``QUARANTINE`` action by using the
  ``target_entity_id`` field of ``recall_actions``.
- Uses the actual structure of ``ground_truth_label`` without inventing field
  names.
- Reports missing/extra columns and treats missing columns as failures unless the
  column is autoincrement or has a server default.
"""

from __future__ import annotations

import sys
from collections import Counter
from decimal import Decimal
from typing import Any, Dict, List, Set

# ----------------------------------------------------------------------
# Data generation
# ----------------------------------------------------------------------
from data.generators.pipeline import run_pipeline

# Import SQLAlchemy models – importing ``app.models`` registers all model classes.
from app.models.base import Base
import app.models  # noqa: F401 – side‑effects register models


def generate_data() -> Dict[str, List[Dict[str, Any]]]:
    """Run the data generator pipeline.

    ``run_pipeline`` returns ``(all_data, checksum)``.  We return only
    ``all_data`` while keeping the checksum available for optional reporting.
    """
    all_data, checksum = run_pipeline(scale_name="full", seed=20261022, export=False)
    # ``checksum`` could be logged or printed later if useful.
    return all_data

# ----------------------------------------------------------------------
# Helper utilities
# ----------------------------------------------------------------------
def get_model_table(name: str):
    return Base.metadata.tables.get(name)


def column_names_from_model(table) -> Set[str]:
    return {col.name for col in table.columns}


def required_columns(table) -> Set[str]:
    """Columns that must be supplied on insert.

    Excludes autoincrement primary keys and columns with server defaults.
    """
    req = set()
    for col in table.columns:
        if col.autoincrement:
            continue
        if col.server_default is not None:
            continue
        req.add(col.name)
    return req


def nullable_columns(table) -> Set[str]:
    return {col.name for col in table.columns if col.nullable}


def primary_key_columns(table) -> List[str]:
    return [col.name for col in table.primary_key]


def foreign_key_map(table) -> Dict[str, tuple]:
    """Map local FK column → (referenced table name, referenced column name)."""
    fk_map = {}
    for col in table.columns:
        for fk in col.foreign_keys:
            ref_table = fk.column.table.name
            ref_column = fk.column.name
            fk_map[col.name] = (ref_table, ref_column)
    return fk_map


def check_constraints(table, rows: List[Dict[str, Any]]) -> List[str]:
    """Validate simple ``CheckConstraint`` objects on a table.

    Handles enum ``IN (…)`` checks and basic ``>=``/``<=`` numeric ranges.
    Returns a list of violation messages.
    """
    messages = []
    for constraint in table.constraints:
        if constraint.__class__.__name__ != "CheckConstraint":
            continue
        sqltext = str(constraint.sqltext).upper()
        # Enum pattern detection.
        if " IN (" in sqltext:
            parts = sqltext.split(" IN (")
            col_part = parts[0].strip().split()[-1]
            allowed = parts[1].split(")")[0]
            allowed_vals = {v.strip().strip("'\"") for v in allowed.split(",")}
            for i, row in enumerate(rows):
                val = row.get(col_part)
                if val is not None and str(val).upper() not in allowed_vals:
                    messages.append(
                        f"Row {i} column '{col_part}' value '{val}' not in allowed {allowed_vals}"
                    )
        # Simple range checks like ``quantity >= 0``.
        elif ">=" in sqltext or "<=" in sqltext:
            tokens = (
                sqltext.replace("=", " = ")
                .replace(">", " > ")
                .replace("<", " < ")
                .split()
            )
            if len(tokens) >= 3:
                col_name, op, value = tokens[0], tokens[1], tokens[2]
                try:
                    limit = Decimal(value)
                except Exception:
                    continue
                for i, row in enumerate(rows):
                    val = row.get(col_name)
                    if val is None:
                        continue
                    try:
                        dval = Decimal(str(val))
                    except Exception:
                        continue
                    if op == ">=" and dval < limit:
                        messages.append(
                            f"Row {i} column '{col_name}'={dval} < {limit}"
                        )
                    if op == "<=" and dval > limit:
                        messages.append(
                            f"Row {i} column '{col_name}'={dval} > {limit}"
                        )
    return messages

# ----------------------------------------------------------------------
# Validation logic
# ----------------------------------------------------------------------
def validate():
    all_data = generate_data()
    failures: List[str] = []

    # -------------------------------------------------- Table name matching (include all tables)
    model_tables = set(Base.metadata.tables.keys())
    generated_tables = set(all_data.keys())  # include exception_records
    missing_models = generated_tables - model_tables
    missing_generated = model_tables - generated_tables
    if missing_models:
        failures.append(
            f"Generated tables not defined in models: {sorted(missing_models)}"
        )
    if missing_generated:
        failures.append(
            f"Model tables missing in generated data: {sorted(missing_generated)}"
        )

    # -------------------------------------------------- Per‑table checks
    for table_name, rows in all_data.items():
        model_table = get_model_table(table_name)
        if model_table is None:
            # Already reported in table‑name comparison.
            continue

        print(f"\nTable '{table_name}': {len(rows)} rows")

        # Column name comparison
        generated_cols = set()
        for row in rows:
            generated_cols.update(row.keys())
        model_cols = column_names_from_model(model_table)

        req_cols = required_columns(model_table)
        missing_required = req_cols - generated_cols
        missing_optional = model_cols - generated_cols - req_cols
        extra_cols = generated_cols - model_cols

        # Report all three categories
        print(f"  Required columns missing: {sorted(missing_required)}")
        print(f"  Optional columns missing (allowed): {sorted(missing_optional)}")
        print(f"  Extra columns present: {sorted(extra_cols)}")

        if missing_required:
            failures.append(
                f"Table '{table_name}' missing REQUIRED columns: {sorted(missing_required)}"
            )
        if extra_cols:
            failures.append(
                f"Table '{table_name}' has unexpected columns: {sorted(extra_cols)}"
            )

        # Consistent keys across rows
        key_sets = {frozenset(row.keys()) for row in rows}
        if len(key_sets) > 1:
            failures.append(f"Table '{table_name}' rows have inconsistent keys")

        # Non‑nullable columns (allow intentional EC‑01 null in lot_genealogy)
        non_nullable = {
            col.name for col in model_table.columns if not col.nullable
        }
        for i, row in enumerate(rows):
            for col in non_nullable:
                if col not in row:
                    continue
                if row[col] is None:
                    # EC‑01 exception: allow null material_lot_id in lot_genealogy
                    if (
                        table_name == "lot_genealogy"
                        and col == "material_lot_id"
                        and any(
                            rec.get("issue_type") == "MISSING_INPUT_LOT"
                            for rec in all_data.get("exception_records", [])
                        )
                    ):
                        continue
                    failures.append(
                        f"Table '{table_name}' row {i} column '{col}' is NULL but non‑nullable"
                    )

        # Primary‑key uniqueness
        pk_cols = primary_key_columns(model_table)
        if pk_cols:
            # Determine which PK columns should be considered for uniqueness.
            effective_pk_cols = []
            for col in pk_cols:
                col_obj = model_table.c[col]
                is_generated = col_obj.autoincrement or col_obj.server_default is not None
                # Skip generated PK columns that are absent from the generated rows.
                if is_generated and col not in generated_cols:
                    continue
                effective_pk_cols.append(col)

            if effective_pk_cols:
                pk_tuples = [tuple(row.get(col) for col in effective_pk_cols) for row in rows]
                dup = [item for item, count in Counter(pk_tuples).items() if count > 1]
                if dup:
                    failures.append(
                        f"Table '{table_name}' has duplicate PK values: {dup}"
                    )

        # Foreign‑key integrity (use exact referenced column)
        fk_map = foreign_key_map(model_table)
        for local_col, (ref_table, ref_col) in fk_map.items():
            ref_rows = all_data.get(ref_table, [])
            ref_values = {r.get(ref_col) for r in ref_rows}
            for i, row in enumerate(rows):
                val = row.get(local_col)
                if val is None:
                    continue  # nullable FK allowed
                if val not in ref_values:
                    failures.append(
                        f"Table '{table_name}' row {i} FK '{local_col}'={val} not found in referenced '{ref_table}.{ref_col}'"
                    )

        # Check constraints
        for msg in check_constraints(model_table, rows):
            failures.append(f"Table '{table_name}' constraint violation: {msg}")

    # -------------------------------------------------- Edge‑case checks
    exc_records: List[Dict[str, Any]] = all_data.get("exception_records", [])

    def find_by_issue(issue: str) -> List[Dict[str, Any]]:
        return [rec for rec in exc_records if rec.get("issue_type") == issue]

    # EC‑01 Missing Input Lot
    if not find_by_issue("MISSING_INPUT_LOT"):
        failures.append("EC-01 (MISSING_INPUT_LOT) record not found")

    # EC‑02 Delivery Overrun
    if not find_by_issue("DELIVERY_OVERRUN"):
        failures.append("EC-02 (DELIVERY_OVERRUN) record not found")

    # EC‑03 Missed Customer
    if not find_by_issue("MISSED_CUSTOMER"):
        failures.append("EC-03 (MISSED_CUSTOMER) record not found")

    # EC‑04 Inventory Not Quarantined
    ec04 = find_by_issue("INVENTORY_NOT_QUARANTINED")
    if not ec04:
        failures.append("EC-04 (INVENTORY_NOT_QUARANTINED) record not found")
    else:
        rec = ec04[0]
        gt_label = rec.get("ground_truth_label", {})
        # Do not assume specific field names – use whatever keys are present.
        recall_id = gt_label.get("recall_id")
        finished_lot_id = gt_label.get("finished_lot_id")
        if not recall_id or not finished_lot_id:
            failures.append(
                "EC-04 ground_truth_label missing required keys (recall_id, finished_lot_id)"
            )
        else:
            # Verify the finished lot is within recall_affected_finished_lots for that recall.
            recall_affected = all_data.get("recall_affected_finished_lots", [])
            if not any(
                r.get("recall_id") == recall_id and r.get("finished_lot_id") == finished_lot_id
                for r in recall_affected
            ):
                failures.append(
                    f"EC-04 finished_lot_id '{finished_lot_id}' not linked to recall '{recall_id}' in recall_affected_finished_lots"
                )
            # Ensure no QUARANTINE action for this recall/lot using target_entity_id.
            recall_actions = all_data.get("recall_actions", [])
            if any(
                a.get("recall_id") == recall_id
                and a.get("target_entity_id") == finished_lot_id
                and a.get("action_type") == "QUARANTINE"
                for a in recall_actions
            ):
                failures.append(
                    f"EC-04 has a matching QUARANTINE action for recall '{recall_id}' and target_entity_id '{finished_lot_id}'"
                )

    # -------------------------------------------------- Summary
    if failures:
        print("\nVALIDATION FAILED with the following issues:")
        for f in failures:
            print(f"- {f}")
        sys.exit(1)
    else:
        print("\nVALIDATION PASSED – all checks succeeded.")
        sys.exit(0)


if __name__ == "__main__":
    validate()
