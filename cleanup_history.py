#!/usr/bin/env python3
import os
import pandas as pd

def clean_history_csv(
    input_path: str = "./data/history.csv",
    output_path: str = "./data/history_cleaned.csv",
    subset: list[str] | None = None,
    keep: str = "first"
) -> None:
    """
    Load a history CSV, drop duplicate rows, and write a cleaned CSV.

    Args:
        input_path:    Path to the original history.csv
        output_path:   Where to save the de-duplicated CSV
        subset:        List of column names to consider when identifying duplicates;
                       if None, all columns are used.
        keep:          Whether to keep the "first" or "last" occurrence of each duplicate.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Cannot find input file: {input_path}")

    df = pd.read_csv(input_path)
    before = len(df)

    # drop duplicates
    df_clean = df.drop_duplicates(subset=subset, keep=keep)

    after = len(df_clean)
    removed = before - after

    df_clean.to_csv(output_path, index=False)
    print(f"✅ Read {before} rows from {input_path}")
    print(f"🗑  Dropped {removed} duplicate rows (keeping '{keep}')")
    print(f"✅ Wrote {after} rows to {output_path}")

if __name__ == "__main__":
    # you can customize subset or keep-policy here if you like
    clean_history_csv()
