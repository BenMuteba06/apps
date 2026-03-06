# io_layer/file_readers.py
from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Optional

import pandas as pd


# ---------------------------
# Types & Config Structures
# ---------------------------

@dataclass(frozen=True)
class ReadOptions:
    """
    General options for reading tabular files.
    These map to pandas read_* parameters where applicable.
    """
    # Common
    columns: Optional[Iterable[str]] = None      # subset of columns to read
    dtypes: Optional[Dict[str, Any]] = None      # explicit dtype mapping
    parse_dates: Optional[Iterable[str]] = None  # columns to parse as dates
    date_format: Optional[str] = None            # strptime format for faster parsing
    na_values: Optional[Iterable[Any]] = None
    keep_default_na: bool = True
    encoding: Optional[str] = None               # e.g., "utf-8", "latin1"
    errors: str = "strict"                       # encoding error handling: "strict"|"ignore"|"replace"

    # CSV-specific
    sep: str = ","
    quotechar: str = '"'
    escapechar: Optional[str] = None
    doublequote: bool = True
    header: int | None = 0
    skiprows: Optional[Iterable[int]] = None
    nrows: Optional[int] = None
    # Faster reading when columns are known
    usecols: Optional[Iterable[str]] = None

    # Excel-specific
    sheet: str | int | None = 0                  # sheet name or index
    engine: Optional[str] = None                 # let pandas choose by default


# ---------------------------
# Helpers
# ---------------------------

SUPPORTED_CSV_EXTS = {".csv", ".txt"}
SUPPORTED_XLSX_EXTS = {".xlsx", ".xlsm", ".xls", ".xlsb"}  # xlsb needs engine='pyxlsb' if used
SUPPORTED_EXTS = SUPPORTED_CSV_EXTS | SUPPORTED_XLSX_EXTS


def _ensure_path(path: str | Path) -> Path:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    if not p.is_file():
        raise IsADirectoryError(f"Expected file, got directory: {p}")
    return p


def _ext(path: Path) -> str:
    return path.suffix.lower()


def is_supported_table(path: str | Path) -> bool:
    """Returns True if file extension is a supported table format."""
    try:
        return _ext(Path(path)) in SUPPORTED_EXTS
    except Exception:
        return False


def file_checksum(path: str | Path, algo: str = "md5") -> str:
    """
    Compute a checksum for caching/invalidations.
    """
    path = _ensure_path(path)
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def file_mtime(path: str | Path) -> float:
    """Return last modified time (epoch seconds) for cache keys."""
    return _ensure_path(path).stat().st_mtime


def list_tables_in_dir(
    directory: str | Path,
    recurse: bool = False,
    include_hidden: bool = False,
) -> list[Path]:
    """
    List supported table files (csv/xlsx/xls…) under a directory.
    """
    d = Path(directory)
    if not d.exists():
        raise FileNotFoundError(f"Directory not found: {d}")
    if not d.is_dir():
        raise NotADirectoryError(f"Expected directory, got file: {d}")

    pattern = "**/*" if recurse else "*"
    files = [p for p in d.glob(pattern) if p.is_file() and is_supported_table(p)]
    if not include_hidden:
        # files = [p for p in files if not any(part.startswith(".") for part in p.parts)]
        files = [p for p in files if not p.name.startswith(".")]
    return sorted(files)


# ---------------------------
# Core Readers
# ---------------------------

def read_csv_file(path: str | Path, options: Optional[ReadOptions] = None) -> pd.DataFrame:
    """
    Read a CSV/TXT file with robust defaults and consistent errors.
    """
    options = options or ReadOptions()
    path = _ensure_path(path)

    try:
        # pandas read_csv keyword mapping
        df = pd.read_csv(
            path,
            sep=options.sep,
            quotechar=options.quotechar,
            escapechar=options.escapechar,
            doublequote=options.doublequote,
            header=options.header,
            names=None,  # leave None; user can adjust if needed
            usecols=options.usecols or options.columns,
            dtype=options.dtypes,
            parse_dates=options.parse_dates,
            dayfirst=False,
            # infer_datetime_format=options.date_format is not None,
            encoding=options.encoding,
            encoding_errors=options.errors,
            na_values=options.na_values,
            keep_default_na=options.keep_default_na,
            skiprows=options.skiprows,
            nrows=options.nrows,
        )
        # Optional post-parse strict date format
        if options.date_format and options.parse_dates:
            for col in options.parse_dates:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], format=options.date_format, errors="raise")
        return df

    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(
            e.encoding or "unknown", e.object, e.start, e.end,
            f"Encoding issue reading {path}. Try options.encoding='utf-8' or 'latin1'. Original: {e.reason}"
        )
    except pd.errors.ParserError as e:
        # Often related to malformed CSV; provide helpful hint
        hint = ("CSV parse error. Check delimiter, header row, or quote characters. "
                f"Tried sep='{options.sep}', header={options.header}.")
        raise ValueError(f"{hint} File: {path}\nOriginal: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Failed to read CSV file: {path}\nReason: {e}") from e


def read_excel_file(path: str | Path, options: Optional[ReadOptions] = None) -> pd.DataFrame:
    """
    Read an Excel file (.xlsx/.xls/.xlsm). For .xlsb, set options.engine='pyxlsb' and install extra deps if needed.
    """
    options = options or ReadOptions()
    path = _ensure_path(path)

    try:
        df = pd.read_excel(
            path,
            sheet_name=options.sheet,
            dtype=options.dtypes,
            usecols=options.usecols or options.columns,
            na_values=options.na_values,
            keep_default_na=options.keep_default_na,
            engine=options.engine,  # let pandas choose if None
        )
        # Normalize datetime columns if specified
        if options.parse_dates:
            for col in options.parse_dates:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], format=options.date_format, errors="coerce")
        return df

    except ValueError as e:
        # Covers many Excel engine/sheet/column issues
        raise ValueError(f"Excel read error for {path} (sheet={options.sheet}). {e}") from e
    except Exception as e:
        raise RuntimeError(f"Failed to read Excel file: {path}\nReason: {e}") from e


def detect_and_read(path: str | Path, options: Optional[ReadOptions] = None) -> pd.DataFrame:
    """
    Unified entrypoint: detect file type by extension and read accordingly.
    """
    p = _ensure_path(path)
    ext = _ext(p)

    if ext in SUPPORTED_CSV_EXTS:
        return read_csv_file(p, options)
    if ext in SUPPORTED_XLSX_EXTS:
        return read_excel_file(p, options)
    raise ValueError(f"Unsupported file type: {ext} for {p}")


# ---------------------------
# Batch Utilities
# ---------------------------

def read_many(
    paths: Iterable[str | Path],
    options_by_name: Optional[Dict[str, ReadOptions]] = None,
    name_fn: Optional[Callable[[Path], str]] = None,
) -> Dict[str, pd.DataFrame]:
    """
    Read multiple files and return a dict[name] -> DataFrame.

    - options_by_name: per-table options, keyed by name (after applying name_fn).
    - name_fn: how to name each table (default: base filename without extension).
    """
    options_by_name = options_by_name or {}

    def default_name_fn(p: Path) -> str:
        return p.stem.lower().strip()

    resolver = name_fn or default_name_fn

    result: Dict[str, pd.DataFrame] = {}
    for raw in paths:
        p = _ensure_path(raw)
        name = resolver(p)
        opts = options_by_name.get(name, None)
        df = detect_and_read(p, opts)
        result[name] = df
    return result


# ---------------------------
# Optional: Lightweight Schema Hook
# ---------------------------

def ensure_columns(df: pd.DataFrame, required: Iterable[str], table_name: str = "table") -> pd.DataFrame:
    """
    Simple guard to fail fast if critical columns are missing.
    Use a richer validator later (e.g., pandera/your own schema module).
    """
    required = list(required)
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"{table_name}: missing required columns: {missing}")
    return df


# ---------------------------
# Convenience for Common CSV Pitfalls
# ---------------------------

def sniff_csv_delimiter(path: str | Path, sample_size: int = 8192) -> str:
    """
    Try to guess a CSV delimiter (comma/semicolon/tab/pipe) from a sample.
    Useful when files come from varied sources.
    """
    path = _ensure_path(path)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        sample = f.read(sample_size)
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(sample, delimiters=[",", ";", "\t", "|"])
        return dialect.delimiter
    except Exception:
        return ","  # sensible default