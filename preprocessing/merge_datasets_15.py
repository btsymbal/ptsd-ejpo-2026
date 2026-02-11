# %% [markdown]
# # Merge Clinical and Eye-Tracking Datasets
#
# This notebook merges two datasets to create a unified dataset for analysis:
# - **Eye-tracking metrics** (dataset_2_15.csv): 187 columns of behavioral and physiological measurements
# - **Clinical data** (PTSD_Anima_Table_05_08_with_antipsychotic.csv): Diagnostic information including
#   PTSD status, severity scores, and antipsychotic medication use
#
# Both datasets contain 15 rows with matching session identifiers, allowing for a 1:1 merge.
#
# ## Transformations:
# - Merge on 'sessions' column using inner join with 1:1 validation
# - Drop 'TBI' column per requirements
# - Export merged dataset with 15 rows × 191 columns

# %%
import pandas as pd

# %% [markdown]
# ## Load Datasets

# %%
# Load eye-tracking metrics
df_metrics = pd.read_csv('data/simplified/dataset_2_15.csv')
print(f"Eye-tracking metrics shape: {df_metrics.shape}")
print(f"Columns: {df_metrics.shape[1]}")

# Load clinical data
df_clinical = pd.read_csv('data/additional/PTSD_Anima_Table_05_08_with_antipsychotic.csv')
print(f"\nClinical data shape: {df_clinical.shape}")
print(f"Columns: {df_clinical.shape[1]}")

# Verify sessions column exists in both
print(f"\n'sessions' column in df_metrics: {'sessions' in df_metrics.columns}")
print(f"'sessions' column in df_clinical: {'sessions' in df_clinical.columns}")

# %% [markdown]
# ## Pre-Merge Inspection

# %%
print("Session IDs in eye-tracking data:")
print(df_metrics['sessions'].tolist())

print("\nSession IDs in clinical data:")
print(df_clinical['sessions'].tolist())

# Check for duplicates
print(f"\nDuplicates in df_metrics sessions: {df_metrics['sessions'].duplicated().sum()}")
print(f"Duplicates in df_clinical sessions: {df_clinical['sessions'].duplicated().sum()}")

# Check column overlap (should only be 'sessions')
overlap_cols = set(df_metrics.columns) & set(df_clinical.columns)
print(f"\nOverlapping columns: {overlap_cols}")

print(f"\nExpected merge result: {df_metrics.shape[0]} rows × {df_metrics.shape[1] + df_clinical.shape[1] - len(overlap_cols)} columns")

# %% [markdown]
# ## Merge Datasets

# %%
# Perform inner join with 1:1 validation
df_merged = pd.merge(
    df_metrics,
    df_clinical,
    on='sessions',
    how='inner',
    validate='1:1'
)

print(f"Merged dataset shape: {df_merged.shape}")
print(f"Rows: {df_merged.shape[0]}")
print(f"Columns: {df_merged.shape[1]}")

# Display clinical columns that were added
clinical_cols = [col for col in df_clinical.columns if col != 'sessions']
print(f"\nClinical columns added: {clinical_cols}")

# %% [markdown]
# ## Drop TBI Column

# %%
print(f"Columns before dropping TBI: {df_merged.shape[1]}")
print(f"'TBI' column present: {'TBI' in df_merged.columns}")

df_merged = df_merged.drop(columns=['TBI'])

print(f"\nColumns after dropping TBI: {df_merged.shape[1]}")
print(f"'TBI' column present: {'TBI' in df_merged.columns}")

# %% [markdown]
# ## Validation

# %%
print("Dataset Validation:")
print("=" * 80)

# Assert row count
assert df_merged.shape[0] == 15, f"Expected 15 rows, got {df_merged.shape[0]}"
print(f"✓ Row count: {df_merged.shape[0]} (expected: 15)")

# Assert column count
assert df_merged.shape[1] == 191, f"Expected 191 columns, got {df_merged.shape[1]}"
print(f"✓ Column count: {df_merged.shape[1]} (expected: 191)")

# Check for unexpected NaN values introduced by merge
nan_counts_before_metrics = df_metrics.isnull().sum().sum()
nan_counts_before_clinical = df_clinical.isnull().sum().sum()
nan_counts_after = df_merged.isnull().sum().sum()

print(f"\n✓ NaN values in original datasets: {nan_counts_before_metrics + nan_counts_before_clinical}")
print(f"✓ NaN values in merged dataset: {nan_counts_after}")
print(f"✓ No unexpected NaN values introduced by merge: {nan_counts_after == nan_counts_before_metrics + nan_counts_before_clinical}")

# Verify clinical columns are present
required_clinical_cols = ['if_PTSD', 'ITI_PTSD', 'ITI_cPTSD', 'if_antipsychotic']
for col in required_clinical_cols:
    assert col in df_merged.columns, f"Missing expected column: {col}"
    print(f"✓ Column '{col}' present")

# Confirm TBI column is removed
assert 'TBI' not in df_merged.columns, "TBI column should be removed"
print(f"✓ TBI column removed")

print("\n" + "=" * 80)
print("All validations passed!")

# %% [markdown]
# ## Preview Merged Dataset

# %%
print("\nMerged dataset preview:")
print(f"Shape: {df_merged.shape}")
print(f"\nColumns ({len(df_merged.columns)}):")
print(df_merged.columns.tolist())

print("\nFirst 3 rows:")
df_merged.head(3)

# %% [markdown]
# ## Export Merged Dataset

# %%
output_path = 'data/simplified/dataset_merged_15.csv'
df_merged.to_csv(output_path, index=False)

print(f"\n{'=' * 80}")
print(f"SUCCESS: Merged dataset exported to: {output_path}")
print(f"Final dimensions: {df_merged.shape[0]} rows × {df_merged.shape[1]} columns")
print(f"{'=' * 80}")
