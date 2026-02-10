# %% [markdown]
# # PTSD Anima Table Preprocessing
#
# This notebook preprocesses the PTSD Anima Table data from materials/PTSD_Anima_Table_05_08.xlsx
# by applying the following transformations:
# - Keep only the last 15 rows
# - Drop Patient Name + ID column
# - Drop all empty columns
# - Extract session IDs from Anima ID URLs
# - Rename columns for consistency
# - Convert PTSD qualitative assessments to binary (0/1)
# - Normalize missing values in ITI scores
# - Drop additional columns not needed for analysis (ITI score PTSD + cPTSD, Alcohol abuse,
#   Substance abuse, Psychiatric history, Battle injuries, Comments)

# %%
import pandas as pd
import re

# %% [markdown]
# ## Load Data

# %%
# Load Excel file
df = pd.read_excel('../materials/PTSD_Anima_Table_05_08.xlsx')

# Display original shape
print(f"Original shape: {df.shape}")
df.head()

# %% [markdown]
# ## Keep Last 15 Rows

# %%
df = df.tail(15).reset_index(drop=True)
print(f"After filtering to last 15 rows: {df.shape}")

# %% [markdown]
# ## Drop Patient Name + ID Column

# %%
df = df.drop(columns=['Patient Name + ID'])
print(f"After dropping 'Patient Name + ID': {df.shape}")

# %% [markdown]
# ## Drop Empty Columns

# %%
# Identify and drop columns that are completely empty
empty_cols = df.columns[df.isna().all()].tolist()
print(f"Dropping empty columns: {empty_cols}")
df = df.dropna(axis=1, how='all')
print(f"After dropping empty columns: {df.shape}")

# %% [markdown]
# ## Process Anima ID Column

# %%
# Extract session IDs from URLs
# Pattern: https://anima-mil-dev-3c6b5.web.app/s/{ID}/r -> {ID}
def extract_session_id(url):
    if pd.isna(url):
        return url
    # Extract the ID between /s/ and /r
    match = re.search(r'/s/([^/]+)/r', str(url))
    if match:
        return match.group(1)
    return url

df['Anima ID'] = df['Anima ID'].apply(extract_session_id)
print("Session IDs extracted from URLs")
print(f"Sample values: {df['Anima ID'].head().tolist()}")

# %% [markdown]
# ## Rename Columns

# %%
df = df.rename(columns={
    'Anima ID': 'sessions',
    'PTSD_qual': 'if_PTSD',
    'ITI score PTSD': 'ITI_PTSD',
    'ITI score cPTSD': 'ITI_cPTSD'
})
print(f"Columns renamed. Current columns: {list(df.columns)}")

# %% [markdown]
# ## Transform if_PTSD Column

# %%
# Map + to 1, - to 0
print(f"Original if_PTSD values: {df['if_PTSD'].unique()}")
df['if_PTSD'] = df['if_PTSD'].map({'+': 1, '-': 0})
print(f"Transformed if_PTSD values: {df['if_PTSD'].unique()}")

# %% [markdown]
# ## Drop cPTSD_qual Column

# %%
df = df.drop(columns=['cPTSD_qual'])
print(f"After dropping 'cPTSD_qual': {df.shape}")

# %% [markdown]
# ## Process ITI Score Columns

# %%
# Replace '-' with 0 in both ITI score columns
print(f"Original ITI_PTSD unique values: {df['ITI_PTSD'].unique()}")
print(f"Original ITI_cPTSD unique values: {df['ITI_cPTSD'].unique()}")

df['ITI_PTSD'] = df['ITI_PTSD'].replace('-', 0)
df['ITI_cPTSD'] = df['ITI_cPTSD'].replace('-', 0)

# Convert to numeric if needed
df['ITI_PTSD'] = pd.to_numeric(df['ITI_PTSD'], errors='coerce').fillna(0)
df['ITI_cPTSD'] = pd.to_numeric(df['ITI_cPTSD'], errors='coerce').fillna(0)

print(f"Transformed ITI_PTSD unique values: {df['ITI_PTSD'].unique()}")
print(f"Transformed ITI_cPTSD unique values: {df['ITI_cPTSD'].unique()}")

# %% [markdown]
# ## Drop Additional Columns

# %%
# Drop columns not needed for analysis
columns_to_drop = [
    'ITI score PTSD + cPTSD',
    'Alcohol abuse',
    'Substance abuse',
    'Psychiatric history',
    'Battle injuries',
    'Comments'
]
df = df.drop(columns=columns_to_drop)
print(f"After dropping additional columns: {df.shape}")
print(f"Remaining columns: {list(df.columns)}")

# %% [markdown]
# ## Final Dataset

# %%
print(f"Final shape: {df.shape}")
print(f"\nColumns: {list(df.columns)}")
print(f"\nData types:\n{df.dtypes}")
df.head()

# %% [markdown]
# ## Export to CSV

# %%
output_path = '../data/additional/PTSD_Anima_Table_05_08_preprocessed.csv'
df.to_csv(output_path, index=False)
print(f"Data exported to: {output_path}")
print(f"Final dataset shape: {df.shape}")
