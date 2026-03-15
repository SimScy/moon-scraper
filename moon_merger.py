import pandas as pd
import os
import time

# -----------------------------
# CONFIGURATION
# -----------------------------

INPUT_DIR = "data/raw"
OUTPUT_FILE = "data/processed/moon_dataset.csv"

os.makedirs("data/processed", exist_ok=True)

# -----------------------------
# Process and clean a single daily dataset
# -----------------------------

def process_file(filepath):
    """
    Load a raw daily moon data file, clean the data,
    and return a minute-level dataframe with a full time index.
    """

    filename = os.path.basename(filepath)

    # Extract date from filename (datatable_YYYY-MM-DD.txt)
    date = filename.replace("datatable_", "").replace(".txt", "")

    df = pd.read_csv(
        filepath,
        sep="\t",
        encoding="utf-8",
        # Skip metadata header lines
        skiprows=4
    )

    # Clean column names
    df.columns = df.columns.str.replace("\xa0", " ").str.strip()

    # Remove degree symbol from numeric columns
    for col in ["Altitude", "Azimuth (E of N)"]:
        df[col] = df[col].str.replace("°", "").astype(float)

    # Standardize variable names
    df = df.rename(columns={
    "Azimuth (E of N)": "Azimuth",
    "Fraction Illuminated": "Illumination"}
    )

    # Create datetime column
    df["datetime"] = pd.to_datetime(
        date + " " + df["Time"].astype(str).str.strip(),
        format="%Y-%m-%d %H:%M",
        errors="coerce"
    )

    # Remove rows without valid datetime (metadata rows in the raw table)
    df = df.dropna(subset=["datetime"])
 
    # Set datetime as index for time-series operations
    df = df.set_index("datetime")

    # Create a full minute-level time range for the day
    full_range = pd.date_range(
        start=f"{date} 00:00",
        end=f"{date} 23:59",
        freq="1min"
    )

    # Reindex to ensure a complete timeline.
    # Missing rows are filled with NaN. These typically occur when the moon
    # is below -12° altitude, where the source calculator does not report values.
    df = df.reindex(full_range)

    # Restore datetime as a column
    df = df.reset_index().rename(columns={"index": "datetime"})


    return df

    
# -----------------------------
# Start Timer
# -----------------------------

start = time.time()

# -----------------------------
# Find input files
# -----------------------------

file_list = sorted(
    f for f in os.listdir(INPUT_DIR)
    if f.startswith("datatable_") and f.endswith(".txt")
)

# -----------------------------
# Process files
# -----------------------------

dfs = []

for datei in file_list:

    path = os.path.join(INPUT_DIR, datei)
    dfs.append(process_file(path))

# -----------------------------
# Combine all daily datasets
# -----------------------------

full_df = pd.concat(dfs, ignore_index=True)

# Move datetime column to the front
cols = ["datetime"] + [c for c in full_df.columns if c != "datetime"]
full_df = full_df[cols]

# -----------------------------
# Save final dataset
# -----------------------------

full_df.to_csv(OUTPUT_FILE, index=False)

duration = time.time() - start

print(f"Dataset with {len(full_df)} rows saved in: {OUTPUT_FILE}")
print(f"Process took {duration:.2f} seconds")