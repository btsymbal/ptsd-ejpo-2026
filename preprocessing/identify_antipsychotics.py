# %% [markdown]
# # Antipsychotic Medication Classification
#
# This notebook analyzes treatment data from PTSD_Anima_Table_05_08_preprocessed.csv to identify
# which patients are receiving antipsychotic medications. The goal is to add a binary indicator
# column (if_antipsychotic) showing whether each patient's treatment regimen includes at least
# one antipsychotic medication, then remove the Treatment column and export the processed dataset.
#
# ## Methodology
#
# - Parse Treatment column containing Ukrainian medication names with dosages
# - Classify each medication as antipsychotic (1) or non-antipsychotic (0)
# - Handle special cases (e.g., dosage-dependent classification for Prochlorperazine)
# - Add binary if_antipsychotic column
# - Export processed dataset

# %%
import os
from pathlib import Path

import pandas as pd
import re
from typing import Dict, Tuple

# Set working directory to project root (works from any location)
os.chdir(Path(__file__).resolve().parent.parent)

# %% [markdown]
# ## Load Data

# %%
# Load preprocessed CSV
df = pd.read_csv('data/additional/PTSD_Anima_Table_05_08_preprocessed.csv')

# Display original shape
print(f"Original shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
df.head()

# %% [markdown]
# ## Explore Treatment Column

# %%
print("Sample Treatment entries:")
print("=" * 80)
for idx, treatment in enumerate(df['Treatment'].head(5), 1):
    print(f"\n{idx}. {treatment}")
    print("-" * 80)

# %% [markdown]
# ## Extract Unique Medications

# %%
def parse_medications(treatment_text):
    """
    Parse treatment text to extract individual medications.

    Args:
        treatment_text: String containing medication names and dosages (multi-line)

    Returns:
        List of tuples: (medication_name, dosage_info)
    """
    if pd.isna(treatment_text):
        return []

    # Split by newlines to get individual medications
    lines = str(treatment_text).strip().split('\n')
    medications = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Extract medication name (remove dosage info)
        # Pattern: medication name followed by dosage (e.g., "Кветирон 50мг")
        # Keep the full line for dosage extraction
        medications.append(line)

    return medications

# Extract all unique medications
all_medications = []
for treatment in df['Treatment'].dropna():
    meds = parse_medications(treatment)
    all_medications.extend(meds)

print(f"Total medication entries: {len(all_medications)}")
print(f"\nUnique medications:")
unique_meds = sorted(set(all_medications))
for i, med in enumerate(unique_meds, 1):
    print(f"{i:2d}. {med}")

# %% [markdown]
# ## Medication Classification Dictionary
#
# Based on pharmacological research, medications are classified as:
# - **1**: Antipsychotic medication
# - **0**: Non-antipsychotic medication
# - **'dosage_dependent'**: Classification depends on dosage (Prochlorperazine/Вертинекс)
#
# ### Confirmed Antipsychotics:
# - **Кветирон** (Quetiapine): Atypical (second-generation) antipsychotic
#
# ### Dosage-Dependent:
# - **Вертинекс** (Prochlorperazine): Phenothiazine antipsychotic
#   - Low doses (≤20 mg/day): Used for vestibular/antiemetic purposes → 0
#   - High doses (≥30 mg/day): Used for antipsychotic purposes → 1
#
# ### Non-Antipsychotics:
# - **Спітомін/Спітамін** (Buspirone): Anxiolytic
# - **Міасер/Міорікс** (Mirtazapine): Tetracyclic antidepressant
# - **Сертралін/Сертралофт** (Sertraline): SSRI antidepressant
# - **Есциталопрам** (Escitalopram): SSRI antidepressant
# - **Пароксин/Пароксетин** (Paroxetine): SSRI antidepressant
# - **Тразодон/Тразадон** (Trazodone): Antidepressant
# - **Вальпроком** (Valproate): Mood stabilizer/anticonvulsant
# - **Мелатонін/Вітамелатонін** (Melatonin): Hormone supplement
# - **Прегабалін** (Pregabalin): Anticonvulsant
# - **Дулоксетин** (Duloxetine): SNRI antidepressant
# - **Венлафаксин** (Venlafaxine): SNRI antidepressant
# - **Кетамін** (Ketamine): Dissociative anesthetic (off-label for depression)
# - **Бетагестин** (Betahistine): Histamine analogue
# - **Мебікар** (Mebicar): Anxiolytic
# - **Гідозепан** (Gidazepam): Benzodiazepine

# %%
# Medication classification dictionary
medication_classification: Dict[str, int | str] = {
    # ANTIPSYCHOTICS (1)
    'кветирон': 1,  # Quetiapine - atypical antipsychotic

    # DOSAGE-DEPENDENT
    'вертинекс': 'dosage_dependent',  # Prochlorperazine - needs dosage evaluation

    # NON-ANTIPSYCHOTICS (0)
    'спітомін': 0,  # Buspirone - anxiolytic
    'спітамін': 0,  # Buspirone - anxiolytic (variant spelling)
    'міасер': 0,  # Mirtazapine - antidepressant
    'міорікс': 0,  # Mirtazapine - antidepressant
    'сертралін': 0,  # Sertraline - SSRI
    'сертралофт': 0,  # Sertraline - SSRI
    'есциталопрам': 0,  # Escitalopram - SSRI
    'пароксин': 0,  # Paroxetine - SSRI
    'пароксетин': 0,  # Paroxetine - SSRI (variant spelling)
    'тразодон': 0,  # Trazodone - antidepressant
    'тразадон': 0,  # Trazodone - antidepressant (variant spelling)
    'вальпроком': 0,  # Valproate - mood stabilizer
    'мелатонін': 0,  # Melatonin
    'вітамелатонін': 0,  # Melatonin variant
    'прегабалін': 0,  # Pregabalin - anticonvulsant
    'дулоксетин': 0,  # Duloxetine - SNRI
    'венлафаксин': 0,  # Venlafaxine - SNRI
    'кетамін': 0,  # Ketamine - dissociative anesthetic
    'бетагестин': 0,  # Betahistine - histamine analogue
    'мебікар': 0,  # Mebicar - anxiolytic
    'гідозепан': 0,  # Gidazepam - benzodiazepine
}

print("Medication classification dictionary created")
print(f"Total medications classified: {len(medication_classification)}")
print(f"Antipsychotics: {sum(1 for v in medication_classification.values() if v == 1)}")
print(f"Dosage-dependent: {sum(1 for v in medication_classification.values() if v == 'dosage_dependent')}")
print(f"Non-antipsychotics: {sum(1 for v in medication_classification.values() if v == 0)}")

# %% [markdown]
# ## Extract Medication Name and Dosage

# %%
def extract_med_name_and_dosage(med_line: str) -> Tuple[str, float]:
    """
    Extract medication name and daily dosage from a medication line.

    Args:
        med_line: Full medication line (e.g., "Вертинекс 5мг х3")

    Returns:
        Tuple of (medication_name_lowercase, total_daily_dosage_mg)
    """
    # Extract medication name (first word, case-insensitive)
    parts = med_line.strip().split()
    if not parts:
        return "", 0.0

    med_name = parts[0].lower().strip('.,')

    # Extract dosage information
    # Pattern: "XXмг" or "XX мг" possibly followed by "х2", "х3", "Х2", "Х3", etc.
    dosage_match = re.search(r'(\d+)\s*мг', med_line, re.IGNORECASE)
    multiplier_match = re.search(r'[хx](\d+)', med_line, re.IGNORECASE)

    single_dose = float(dosage_match.group(1)) if dosage_match else 0.0
    multiplier = float(multiplier_match.group(1)) if multiplier_match else 1.0

    total_daily_dosage = single_dose * multiplier

    return med_name, total_daily_dosage

# Test the function
print("Testing medication extraction:")
test_cases = [
    "Вертинекс 5мг х3",
    "Кветирон 50мг",
    "Сертралін 100 мг.",
    "КЕТАМІН"
]
for test in test_cases:
    name, dosage = extract_med_name_and_dosage(test)
    print(f"  '{test}' → name='{name}', dosage={dosage}mg/day")

# %% [markdown]
# ## Classification Function

# %%
def classify_treatment(treatment_text: str, classification_dict: Dict) -> int:
    """
    Classify whether a treatment regimen contains antipsychotic medications.

    Args:
        treatment_text: Multi-line string with medication names and dosages
        classification_dict: Dictionary mapping medication names to classifications

    Returns:
        1 if treatment contains antipsychotic, 0 otherwise
    """
    if pd.isna(treatment_text):
        return 0

    medications = parse_medications(treatment_text)

    for med_line in medications:
        med_name, daily_dosage = extract_med_name_and_dosage(med_line)

        if med_name not in classification_dict:
            print(f"WARNING: Unknown medication '{med_name}' in line: {med_line}")
            continue

        classification = classification_dict[med_name]

        # Handle dosage-dependent classification (Prochlorperazine/Вертинекс)
        if classification == 'dosage_dependent':
            # Вертинекс (Prochlorperazine):
            # - Low doses (≤20 mg/day): vestibular/antiemetic use → 0
            # - High doses (≥30 mg/day): antipsychotic use → 1
            if daily_dosage >= 30:
                return 1  # High dose = antipsychotic use
            else:
                continue  # Low dose = not antipsychotic, check other meds

        # Direct classification
        if classification == 1:
            return 1  # Found an antipsychotic

    return 0  # No antipsychotics found

# Test the function
print("\nTesting classification function:")
test_treatments = [
    "Кветирон 50мг",  # Should be 1
    "Сертралін 50 мг.\nСпітомін 5мг. х3",  # Should be 0
    "Вертинекс 5мг х3\nМелатонін 3мг.",  # Should be 0 (low dose Prochlorperazine)
    "Вертинекс 15мг х3\nМелатонін 3мг.",  # Should be 1 (high dose Prochlorperazine)
]
for test in test_treatments:
    result = classify_treatment(test, medication_classification)
    print(f"  {test.replace(chr(10), ' | ')} → {result}")

# %% [markdown]
# ## Apply Classification to Dataset

# %%
print("Applying classification to all rows...")
print("=" * 80)

# Apply classification
df['if_antipsychotic'] = df['Treatment'].apply(
    lambda x: classify_treatment(x, medication_classification)
)

print(f"\nClassification complete!")
print(f"Total rows: {len(df)}")
print(f"Patients with antipsychotics: {df['if_antipsychotic'].sum()}")
print(f"Patients without antipsychotics: {(df['if_antipsychotic'] == 0).sum()}")

# %% [markdown]
# ## Detailed Classification Results

# %%
print("\nDetailed classification results:")
print("=" * 80)
for idx, row in df.iterrows():
    session_id = row['sessions']
    treatment = row['Treatment']
    classification = row['if_antipsychotic']

    print(f"\n{idx + 1}. Session: {session_id}")
    print(f"   Classification: {'ANTIPSYCHOTIC' if classification == 1 else 'NO ANTIPSYCHOTIC'}")
    print(f"   Treatment:")
    if pd.isna(treatment):
        print(f"      (empty)")
    else:
        for line in str(treatment).split('\n'):
            if line.strip():
                med_name, dosage = extract_med_name_and_dosage(line)
                med_class = medication_classification.get(med_name, 'UNKNOWN')
                if med_class == 'dosage_dependent':
                    if dosage >= 30:
                        med_class = '1 (HIGH DOSE)'
                    else:
                        med_class = '0 (LOW DOSE)'
                print(f"      - {line.strip()} → [{med_class}]")

# %% [markdown]
# ## Drop Treatment Column

# %%
print("\nDropping Treatment column...")
df_final = df.drop(columns=['Treatment'])
print(f"After dropping Treatment: {df_final.shape}")
print(f"Remaining columns: {list(df_final.columns)}")

# %% [markdown]
# ## Verify Final Dataset

# %%
print("\nFinal dataset verification:")
print(f"Shape: {df_final.shape}")
print(f"\nColumn data types:")
print(df_final.dtypes)
print(f"\nif_antipsychotic value counts:")
print(df_final['if_antipsychotic'].value_counts().sort_index())
print(f"\nNull values per column:")
print(df_final.isnull().sum())

# Display first few rows
print("\nFirst 5 rows of final dataset:")
df_final.head()

# %% [markdown]
# ## Export Processed Dataset

# %%
output_path = 'data/additional/PTSD_Anima_Table_05_08_with_antipsychotic.csv'
df_final.to_csv(output_path, index=False)
print(f"\nData exported to: {output_path}")
print(f"Final dataset shape: {df_final.shape}")
print(f"Export complete!")
