# run_me_once.py
from pathlib import Path
import sys
from pathlib import Path
import os

sys.path.append(str(Path(__file__).resolve().parent.parent))
from io_layer.data_loader import DataSourceConfig, load_tables

def main():
    repo_root = Path(__file__).resolve().parent
    zip_path = repo_root / "streamlit" / "assets" / "kpis.zip"
    #extract_dir = Path(os.environ.get("TEMP", "C:/temp")) / "kpi_unzipped"  # uses Windows TEMP Only good for local testing, not cross-platform
    extract_dir = Path(__file__).resolve().parent / ".cache" / "kpi_unzipped"
    extract_dir.mkdir(parents=True, exist_ok=True)

    cfg = DataSourceConfig(
        source_path=str(zip_path),
        extract_to=str(extract_dir),
        recurse=True,
        clean_names=True,
        allowed_tables=None,
        options_per_table=None,
    )

    tables = load_tables(cfg)

    print("Loaded tables:")
    for name, df in tables.items():
        print(f" - {name}: shape={df.shape}, cols={list(df.columns)[:6]}{'...' if df.shape[1]>6 else ''}")

if __name__ == "__main__":
    main()