# %% [markdown]
# # Dataset Column Comparison
#
# This notebook compares the columns between dataset_1_15.csv and dataset_2_15.csv
# to identify which columns are present in one dataset but missing in the other.

# %%
import os
from pathlib import Path

import pandas as pd

# Set working directory to project root (works from any location)
os.chdir(Path(__file__).resolve().parent.parent)

# %% [markdown]
# ## Load Datasets

# %%
# Load both datasets
df1 = pd.read_csv('data/simplified/dataset_1_15.csv')
df2 = pd.read_csv('data/simplified/dataset_2_15.csv')

print(f"Dataset 1 shape: {df1.shape}")
print(f"Dataset 2 shape: {df2.shape}")

# %% [markdown]
# ## Column Analysis

# %%
# Get column sets
cols1 = set(df1.columns)
cols2 = set(df2.columns)

print(f"Number of columns in Dataset 1: {len(cols1)}")
print(f"Number of columns in Dataset 2: {len(cols2)}")

# %% [markdown]
# ## Column Differences

# %%
# Find columns only in Dataset 1
only_in_df1 = cols1 - cols2

# Find columns only in Dataset 2
only_in_df2 = cols2 - cols1

# Find common columns
common_cols = cols1 & cols2

print(f"\nCommon columns: {len(common_cols)}")
print(f"Columns only in Dataset 1: {len(only_in_df1)}")
print(f"Columns only in Dataset 2: {len(only_in_df2)}")

# %%
# Display columns only in Dataset 1
print("\n" + "="*60)
print("COLUMNS ONLY IN DATASET 1:")
print("="*60)
if only_in_df1:
    for col in sorted(only_in_df1):
        print(f"  - {col}")
else:
    print("  (None)")

# %%
# Display columns only in Dataset 2
print("\n" + "="*60)
print("COLUMNS ONLY IN DATASET 2:")
print("="*60)
if only_in_df2:
    for col in sorted(only_in_df2):
        print(f"  - {col}")
else:
    print("  (None)")

# %%
# Display common columns
print("\n" + "="*60)
print("COMMON COLUMNS:")
print("="*60)
if common_cols:
    for col in sorted(common_cols):
        print(f"  - {col}")
else:
    print("  (None)")

# %% [markdown]
# ## Summary

# %%
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Total unique columns across both datasets: {len(cols1 | cols2)}")
print(f"Columns in both datasets: {len(common_cols)}")
print(f"Columns unique to Dataset 1: {len(only_in_df1)}")
print(f"Columns unique to Dataset 2: {len(only_in_df2)}")
print(f"\nColumn overlap: {len(common_cols) / len(cols1 | cols2) * 100:.1f}%")
