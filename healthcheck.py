# healthcheck.py — run this to verify imports work before Streamlit starts
import sys
from pathlib import Path

print(f"Python: {sys.version}")
print(f"Working directory: {Path.cwd()}")
print(f"__file__ resolves to: {Path(__file__).resolve()}")

# Test core imports
try:
    import streamlit
    print(f" streamlit: {streamlit.__version__}")
except Exception as e:
    print(f" streamlit: {e}")

try:
    import pandas
    print(f" pandas: {pandas.__version__}")
except Exception as e:
    print(f" pandas: {e}")

try:
    import altair
    print(f" altair: {altair.__version__}")
except Exception as e:
    print(f" altair: {e}")

# Test zip path
zip_path = Path(__file__).resolve().parent / "streamlit" / "assets" / "kpis.zip"
print(f"\nZip path: {zip_path}")
print(f"Zip exists: {zip_path.exists()}")