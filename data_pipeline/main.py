#!/usr/bin/env python3
"""
Load the Manufacturing demo CSV into MotherDuck for GoodData Cloud.

Default behavior:
- Reads the public CSV from GitHub
- Creates/Replaces `main.production_line` in a MotherDuck database
- Validates the resulting schema + row count

Required env vars:
- MOTHERDUCK_TOKEN
- MOTHERDUCK_DATABASE

Optional env vars:
- CSV_URL
- MOTHERDUCK_SCHEMA (default: main)
- MOTHERDUCK_TABLE (default: production_line)
"""

from __future__ import annotations

import argparse
import logging
import os
import pathlib
import sys
from typing import Final

# Allow running as a script (`python data_pipeline/main.py`) while
# importing project-root utilities.
_PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from utils.motherduck import (  # noqa: E402
    ConfigError,
    Settings,
    get_motherduck_dsn,
    get_motherduck_database,
    get_motherduck_token,
    load_to_motherduck,
)

logger = logging.getLogger(__name__)

DEFAULT_CSV_URL: Final[str] = (
    "https://raw.githubusercontent.com/kubow/Data_playground/main/output/production_line.csv"
)

EXPECTED_COLUMNS: Final[tuple[str, ...]] = (
    "timestamp",
    "prod_line",
    "voltage",
    "current",
    "event",
    "checked_by",
)

def _setup_logging() -> None:
    level_name = (os.getenv("LOG_LEVEL") or "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def parse_args(argv: list[str]) -> Settings:
    parser = argparse.ArgumentParser(
        description="Load production_line.csv into MotherDuck (GoodData demo)."
    )
    parser.add_argument(
        "--csv-url",
        default=os.getenv("CSV_URL") or DEFAULT_CSV_URL,
        help=f"Source CSV URL (default: {DEFAULT_CSV_URL})",
    )
    parser.add_argument(
        "--database",
        "--motherduck-database",
        default=os.getenv("MOTHERDUCK_DATABASE"),
        help="MotherDuck database name (e.g. production_line).",
    )
    parser.add_argument(
        "--schema",
        default=os.getenv("MOTHERDUCK_SCHEMA") or "main",
        help="Target schema (default: main)",
    )
    parser.add_argument(
        "--table",
        default=os.getenv("MOTHERDUCK_TABLE") or "production_line",
        help="Target table (default: production_line)",
    )

    ns = parser.parse_args(argv)
    if not ns.database:
        raise ConfigError("Missing database. Provide --database or set MOTHERDUCK_DATABASE.")
    if ns.database:
        os.environ["MOTHERDUCK_DATABASE"] = str(ns.database)
    if ns.schema:
        os.environ["MOTHERDUCK_SCHEMA"] = str(ns.schema)
    if ns.table:
        os.environ["MOTHERDUCK_TABLE"] = str(ns.table)

    database = get_motherduck_database()
    dsn = get_motherduck_dsn()

    return Settings(
        csv_url=str(ns.csv_url),
        database=str(database),
        motherduck_dsn=str(dsn),
        schema=str(ns.schema),
        table=str(ns.table),
    )


def main() -> int:
    _setup_logging()
    try:
        settings = parse_args(sys.argv[1:])
        # Ensure env-based validation message is actionable.
        get_motherduck_token()
        get_motherduck_database()
        load_to_motherduck(settings, expected_columns=EXPECTED_COLUMNS)
        return 0
    except ConfigError as e:
        logger.error("Config error: %s", e)
        return 2
    except Exception as e:
        logger.exception("Pipeline failed: %s", e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

