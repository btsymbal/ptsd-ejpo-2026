# %% [markdown]
# # Merge Datasets 1 and 2 (15 rows each)
#
# This notebook merges two 15-row datasets into a single 30-row dataset.
#
# **Input datasets**:
# - `dataset_1_15.csv`: 15 rows, clinical columns at start, includes TBI column
# - `dataset_merged_2_15.csv`: 15 rows, clinical columns at end, no TBI column
#
# **Key transformations**:
# 1. Drop TBI column from dataset 1
# 2. Replace zero values with NaN in clinical assessment columns (`ITI_PTSD`, `ITI_cPTSD`, `if_antipsychotic`) for dataset 1 only
# 3. Vertically concatenate datasets (30 rows total)
#
# **Output**: `dataset_merged_1_and_2_15.csv` (30 rows × 191 columns)

# %%
import pandas as pd
import numpy as np

# %% [markdown]
# ## 1. Load Datasets

# %%
# Load both datasets
df1 = pd.read_csv('data/simplified/dataset_1_15.csv')
df2 = pd.read_csv('data/simplified/dataset_merged_2_15.csv')

print("Dataset 1 shape:", df1.shape)
print("Dataset 2 shape:", df2.shape)
print()

# %%
# Inspect column counts and key columns
print(f"Dataset 1 columns: {df1.shape[1]}")
print(f"Dataset 2 columns: {df2.shape[1]}")
print()

# Check for TBI column
print("TBI in dataset 1:", 'TBI' in df1.columns)
print("TBI in dataset 2:", 'TBI' in df2.columns)
print()

# Display first few session IDs from each dataset
print("Dataset 1 sessions (first 5):", df1['sessions'].head().tolist())
print("Dataset 2 sessions (first 5):", df2['sessions'].head().tolist())

# %% [markdown]
# ## 2. Drop TBI Column from Dataset 1

# %%
# Drop TBI column to align with dataset 2
print("Before dropping TBI:")
print(f"  Dataset 1: {df1.shape[1]} columns")

df1 = df1.drop(columns=['TBI'])

print("After dropping TBI:")
print(f"  Dataset 1: {df1.shape[1]} columns")
print(f"  Dataset 2: {df2.shape[1]} columns")
print(f"  Match: {df1.shape[1] == df2.shape[1]}")
print()

# %% [markdown]
# ## 3. Fill Empty Values with 0 in Dataset 1 Clinical Columns
#
# In dataset 1, empty (NaN) values in clinical assessment columns should be
# filled with 0 to standardize the representation of missing/unknown data.

# %%
# Inspect current values before replacement
columns_to_clean = ['ITI_PTSD', 'ITI_cPTSD', 'if_antipsychotic']

print("Before filling NaN with 0 (dataset 1):")
for col in columns_to_clean:
    if col in df1.columns:
        unique_vals = df1[col].unique()
        nan_count = df1[col].isna().sum()
        print(f"  {col}: unique values = {unique_vals}, NaN count = {nan_count}")
print()

# %%
# Replace NaN with 0
for col in columns_to_clean:
    if col in df1.columns:
        df1[col] = df1[col].fillna(0)

print("After filling NaN with 0 (dataset 1):")
for col in columns_to_clean:
    if col in df1.columns:
        unique_vals = df1[col].unique()
        nan_count = df1[col].isna().sum()
        print(f"  {col}: unique values = {unique_vals}, NaN count = {nan_count}")
print()

# %% [markdown]
# ## 4. Verify Column Alignment

# %%
# Check if column names match (order doesn't matter for concat)
df1_cols = sorted(df1.columns)
df2_cols = sorted(df2.columns)

if df1_cols == df2_cols:
    print("✓ Column names match perfectly")
else:
    print("✗ Column mismatch detected")
    # Find differences
    df1_only = set(df1.columns) - set(df2.columns)
    df2_only = set(df2.columns) - set(df1.columns)
    if df1_only:
        print(f"  Columns only in dataset 1: {df1_only}")
    if df2_only:
        print(f"  Columns only in dataset 2: {df2_only}")
print()

# %% [markdown]
# ## 5. Concatenate Datasets Vertically

# %%
# Append df2 rows under df1 rows
df_merged = pd.concat(
    [df1, df2],
    axis=0,              # Vertical concatenation (along rows)
    ignore_index=True    # Reset index to 0-29
)

print("Merged dataset shape:", df_merged.shape)
print("Expected shape: (30, 191)")
print()

# %% [markdown]
# ## 6. Validate Merged Dataset

# %%
# Assert critical validations
print("Running validations...")

# Check dimensions
assert df_merged.shape == (30, 191), f"Expected (30, 191), got {df_merged.shape}"
print("✓ Dimensions correct: 30 rows × 191 columns")

# Verify TBI column removed
assert 'TBI' not in df_merged.columns, "TBI column should not exist"
print("✓ TBI column successfully removed")

# Check required columns exist
required_cols = ['sessions', 'if_PTSD', 'ITI_PTSD', 'ITI_cPTSD', 'if_antipsychotic']
for col in required_cols:
    assert col in df_merged.columns, f"Missing required column: {col}"
print(f"✓ All required columns present: {required_cols}")

# Check for duplicate session IDs
assert df_merged['sessions'].nunique() == 30, "Sessions should be unique"
print("✓ All 30 sessions are unique")

# Verify NaN filling worked (first 15 rows should have no NaN in clinical columns)
for col in ['ITI_PTSD', 'ITI_cPTSD', 'if_antipsychotic']:
    nans_in_first_15 = df_merged.iloc[:15][col].isna().sum()
    assert nans_in_first_15 == 0, f"Found {nans_in_first_15} NaN values in {col} (rows 0-14)"
print("✓ NaN filling verified: no NaN values in clinical columns (rows 0-14)")

print()
print("All validations passed! ✓")
print()

# %% [markdown]
# ## 7. Export Merged Dataset

# %%
output_path = 'data/simplified/dataset_merged_1_and_2_15.csv'
df_merged.to_csv(output_path, index=False)

print(f"Merged dataset exported to: {output_path}")
print(f"Final shape: {df_merged.shape}")
print()

# %%
# Display summary statistics
print("Dataset Summary:")
print(f"  Total rows: {len(df_merged)}")
print(f"  Total columns: {len(df_merged.columns)}")
print(f"  Unique sessions: {df_merged['sessions'].nunique()}")
print()
print("Clinical assessment columns:")
for col in ['if_PTSD', 'ITI_PTSD', 'ITI_cPTSD', 'if_antipsychotic']:
    if col in df_merged.columns:
        non_null = df_merged[col].notna().sum()
        print(f"  {col}: {non_null}/30 non-null values")
print()
print("Session ID ranges:")
print(f"  Rows 0-14 (dataset 1): {df_merged.iloc[:15]['sessions'].tolist()}")
print(f"  Rows 15-29 (dataset 2): {df_merged.iloc[15:]['sessions'].tolist()}")
