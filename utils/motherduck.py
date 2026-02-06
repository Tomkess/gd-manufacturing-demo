from __future__ import annotations

import base64
import logging
import os
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:  # pragma: no cover
    import duckdb

logger = logging.getLogger(__name__)


class ConfigError(RuntimeError):
    pass


_IDENT_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _require_identifier(kind: str, value: str) -> str:
    if not _IDENT_RE.fullmatch(value):
        raise ConfigError(
            f"Invalid {kind} {value!r}. Allowed pattern: {_IDENT_RE.pattern}"
        )
    return value


def get_motherduck_token() -> str:
    token = os.getenv("MOTHERDUCK_TOKEN")
    if not token:
        raise ConfigError("Missing MOTHERDUCK_TOKEN")

    # Keep it simple: caller provides raw token (JWT-like).
    return token.strip()


def encode_token_b64(token: str) -> str:
    """Encode a raw token to base64 (utf-8). Useful for GoodData datasource setup."""
    return base64.b64encode(token.encode("utf-8")).decode("utf-8")


def get_motherduck_token_b64() -> str:
    """Base64-encoded token derived from `MOTHERDUCK_TOKEN`."""
    return encode_token_b64(get_motherduck_token())


def get_motherduck_database() -> str:
    db = os.getenv("MOTHERDUCK_DATABASE")
    if not db:
        raise ConfigError("Missing MOTHERDUCK_DATABASE")
    return db.strip()


def get_motherduck_dsn() -> str:
    """Construct MotherDuck DSN from database name."""
    return f"md:{get_motherduck_database()}"


@dataclass(frozen=True)
class Settings:
    csv_url: str
    database: str
    motherduck_dsn: str
    schema: str
    table: str


def _connect_with_bootstrap(dsn: str) -> Any:
    try:
        import duckdb  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "duckdb is required for the MotherDuck backend. "
            "Install it via `pip install -r data_pipeline/requirements.txt`."
        ) from e

    try:
        return duckdb.connect(dsn)
    except Exception:
        # In ephemeral environments (e.g. fresh GitHub runners), the MotherDuck
        # extension may not be present yet. Installing it once is usually enough.
        bootstrap = duckdb.connect()
        try:
            bootstrap.execute("INSTALL motherduck;")
            bootstrap.execute("LOAD motherduck;")
        finally:
            bootstrap.close()
        return duckdb.connect(dsn)


def _ensure_database_exists(database: str) -> None:
    """
    Ensure the MotherDuck database exists.

    MotherDuck databases are created on demand, but some deployments require an
    explicit CREATE DATABASE before connecting to `md:<database>`.
    """
    database = _require_identifier("database", database)

    # Ensure token is available for any MotherDuck connection attempts.
    os.environ["MOTHERDUCK_TOKEN"] = get_motherduck_token()

    # Best-effort: try to create the database via a default MotherDuck connection.
    try:
        con = _connect_with_bootstrap("md:")
    except Exception:
        # If `md:` is not supported, just attempt connecting to the target DB.
        _connect_with_bootstrap(f"md:{database}").close()
        return

    try:
        con.execute(f'CREATE DATABASE IF NOT EXISTS "{database}";')
    finally:
        con.close()


def load_to_motherduck(settings: Settings, *, expected_columns: tuple[str, ...]) -> None:
    """
    Create/replace a MotherDuck table from a CSV URL.

    `expected_columns` is provided by the caller so different datasets/backends
    can reuse this function without hard-coding a schema here.
    """
    # DuckDB/MotherDuck picks this up automatically.
    os.environ["MOTHERDUCK_TOKEN"] = get_motherduck_token()

    database = _require_identifier("database", settings.database)
    schema = _require_identifier("schema", settings.schema)
    table = _require_identifier("table", settings.table)
    full_table = f'"{schema}"."{table}"'

    logger.info("CSV source: %s", settings.csv_url)
    logger.info("MotherDuck database: %s", database)
    logger.info("Target table: %s", full_table)

    _ensure_database_exists(database)
    con = _connect_with_bootstrap(settings.motherduck_dsn)
    try:
        # Needed to read from https:// URLs.
        con.execute("INSTALL httpfs;")
        con.execute("LOAD httpfs;")

        # Ensure schema/table exist.
        con.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}";')
        con.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {full_table} (
                row_id VARCHAR,
                timestamp TIMESTAMP,
                prod_line VARCHAR,
                voltage DOUBLE,
                current DOUBLE,
                event VARCHAR,
                checked_by VARCHAR
            );
            """
        )

        # Stage current source snapshot into a temp table, including deterministic row id.
        con.execute(
            """
            CREATE OR REPLACE TEMP TABLE staging_production_line AS
            SELECT DISTINCT
                md5(
                    concat_ws(
                        '|',
                        CAST(timestamp AS VARCHAR),
                        CAST(prod_line AS VARCHAR),
                        CAST(voltage AS VARCHAR),
                        CAST(current AS VARCHAR),
                        CAST(event AS VARCHAR),
                        CAST(checked_by AS VARCHAR)
                    )
                ) AS row_id,
                CAST(timestamp AS TIMESTAMP) AS timestamp,
                CAST(prod_line AS VARCHAR) AS prod_line,
                CAST(voltage AS DOUBLE) AS voltage,
                CAST(current AS DOUBLE) AS current,
                CAST(event AS VARCHAR) AS event,
                CAST(checked_by AS VARCHAR) AS checked_by
            FROM read_csv_auto(?, header=true);
            """,
            [settings.csv_url],
        )

        # Refresh window: last 7 days relative to the latest timestamp in the source.
        cutoff = con.execute(
            "SELECT max(timestamp) - INTERVAL 7 DAY FROM staging_production_line"
        ).fetchone()[0]
        if cutoff is None:
            raise RuntimeError("Source staging table is empty; nothing to load.")

        logger.info("Refreshing window starting at: %s", cutoff)

        con.execute("BEGIN;")
        try:
            con.execute(f"DELETE FROM {full_table} WHERE timestamp >= ?", [cutoff])
            con.execute(
                f"""
                INSERT INTO {full_table} (row_id, timestamp, prod_line, voltage, current, event, checked_by)
                SELECT row_id, timestamp, prod_line, voltage, current, event, checked_by
                FROM staging_production_line
                WHERE timestamp >= ?;
                """,
                [cutoff],
            )
        except Exception:
            con.execute("ROLLBACK;")
            raise
        else:
            con.execute("COMMIT;")

        # Validate schema & row count.
        cols = [
            row[0]
            for row in con.execute(f"DESCRIBE SELECT * FROM {full_table}").fetchall()
        ]
        logger.debug("Loaded columns: %s", cols)
        missing = [c for c in expected_columns if c not in cols]
        if missing:
            raise RuntimeError(
                f"Loaded table is missing expected columns: {missing}. Got: {cols}"
            )

        row_count = con.execute(f"SELECT COUNT(*) FROM {full_table}").fetchone()[0]
        if not isinstance(row_count, int) or row_count <= 0:
            raise RuntimeError(f"Loaded table row count is invalid: {row_count!r}")

        min_ts, max_ts = con.execute(
            f"SELECT MIN(timestamp), MAX(timestamp) FROM {full_table}"
        ).fetchone()

        logger.info("Loaded rows: %s", row_count)
        logger.info("Timestamp range: %s .. %s", min_ts, max_ts)
    finally:
        con.close()

