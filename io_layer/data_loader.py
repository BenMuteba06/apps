# io_layer/data_loader.py

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Iterable

import pandas as pd

from .zip_utils import (
    is_zip_file,
    extract_zip,
    zip_checksum,
)
from .file_readers import (
    list_tables_in_dir,
    read_many,
    ReadOptions,
)
import re

# ------------------------------------------------------
# Data Loader Configuration
# ------------------------------------------------------

@dataclass(frozen=True)
class DataSourceConfig:
    """
    Defines how and where to load the data from.

    Examples:
        - Path to a ZIP file containing CSV/XLSX
        - Path to an unzipped folder
        - Future: S3 bucket, database, etc.
    """
    source_path: str                    # Path to zip or folder
    extract_to: Optional[str] = None    # Where to extract if ZIP
    recurse: bool = False               # Whether to search subfolders
    clean_names: bool = True            # Lowercase + remove spaces in table names
    allowed_tables: Optional[Iterable[str]] = None  # Restrict table loading
    options_per_table: Optional[Dict[str, ReadOptions]] = None


# ------------------------------------------------------
# File Name Normalization
# ------------------------------------------------------


def normalize_name(name: str) -> str:
    """Normalize table names for dictionary keys."""
    name = name.lower().strip()
    name = re.sub(r'_?\(\d+\)', '', name)  # removes _(1), (1), _(2) etc.
    name = name.replace(" ", "_")
    name = name.strip("_")  # clean any leading/trailing underscores left behind
    return name


# ------------------------------------------------------
# Core Loader
# ------------------------------------------------------

def load_tables(config: DataSourceConfig) -> Dict[str, pd.DataFrame]:
    """
    Load data tables from ZIP or folder paths.

    Returns:
        dict[str, DataFrame] where keys are normalized table names.
    """
    source = Path(config.source_path)

    # ------------------
    # 1. Determine load directory
    # ------------------
    if is_zip_file(source):
        if not config.extract_to:
            raise ValueError("Config.extract_to is required for ZIP sources.")

        extract_dir = extract_zip(source, config.extract_to)
        _ = zip_checksum(source)
        load_dir = extract_dir

        # # TEMP DEBUG
        # from pathlib import Path as _P
        # print(f"\n=== extract_dir returned by extract_zip: {extract_dir}")
        # print(f"=== Does it exist? {_P(extract_dir).exists()}")
        # print(f"=== Contents of extract_to root ({config.extract_to}):")
        # for f in _P(config.extract_to).rglob("*"):
        #     print(f"  {f}")
        # print("=== END DEBUG\n")


    else:
        # assume folder path
        if not source.exists() or not source.is_dir():
            raise NotADirectoryError(f"Folder does not exist or is not a directory: {source}")
        load_dir = source

    # ------------------
    # 2. List supported files in directory
    # ------------------
    table_files = list_tables_in_dir(load_dir, recurse=config.recurse)

    
    # TEMP DEBUG - remove after fix
    # from pathlib import Path as _P
    # print(f"\n=== DEBUG: load_dir = {load_dir}")
    # print("=== All files found (rglob):")
    # for f in _P(load_dir).rglob("*"):
    #     print(f"  {f}")
    # print("=== table_files from list_tables_in_dir:")
    # for f in table_files:
    #     print(f"  {f}")
    # print("=== END DEBUG\n")

  

    if not table_files:
        raise FileNotFoundError(f"No CSV/XLSX files found in: {load_dir}")

    # ------------------
    # 3. Prepare naming function for read_many()
    # ------------------
    def name_fn(path: Path) -> str:
        raw = path.stem
        name = normalize_name(raw) if config.clean_names else raw
        return name

    # ------------------
    # 4. Load all tables
    # ------------------
    tables = read_many(
        paths=table_files,
        options_by_name=config.options_per_table or {},
        name_fn=name_fn,
    )

    # ------------------
    # 5. Optionally filter to allowed tables
    # ------------------
    if config.allowed_tables:
        allowed = {normalize_name(n) for n in config.allowed_tables}
        tables = {k: v for k, v in tables.items() if k in allowed}

    if not tables:
        raise ValueError("No tables available after applying allowed_tables filter.")

    return tables


