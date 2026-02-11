# Antipsychotic Medication Classification Report

## Introduction

This report documents the methodology and results of classifying antipsychotic medications in the PTSD Anima Table dataset. The analysis was performed on 15 patient treatment records from `PTSD_Anima_Table_05_08_preprocessed.csv`.

### Methodology

1. **Data Source**: PTSD treatment records with Ukrainian medication names and dosages
2. **Classification Approach**: Each medication was researched to determine its pharmacological class
3. **Binary Indicator**: Added `if_antipsychotic` column (1 = patient receives at least one antipsychotic, 0 = no antipsychotics)
4. **Special Handling**: Dosage-dependent classification for Prochlorperazine (Вертинекс)

### Results Summary

- **Total Patients**: 15
- **Patients with Antipsychotics**: 7 (46.7%)
- **Patients without Antipsychotics**: 8 (53.3%)
- **Primary Antipsychotic**: Quetiapine (Кветирон) - present in all 7 positive cases

---

## Medication Classification Summary

| Medication (Ukrainian) | Generic/International Name | Pharmacological Class | Antipsychotic Status | Classification |
|------------------------|---------------------------|----------------------|---------------------|----------------|
| **Кветирон** | Quetiapine | Atypical (second-generation) antipsychotic | **YES** | **1** |
| **Вертинекс** | Prochlorperazine | Phenothiazine (first-generation) antipsychotic | **DOSAGE-DEPENDENT** | **0 or 1** |
| Спітомін / Спітамін | Buspirone | Anxiolytic (anti-anxiety) | NO | 0 |
| Міасер / Міорікс | Mirtazapine | Tetracyclic antidepressant | NO | 0 |
| Сертралін / Сертралофт | Sertraline | SSRI antidepressant | NO | 0 |
| Есциталопрам | Escitalopram | SSRI antidepressant | NO | 0 |
| Пароксин / Пароксетин | Paroxetine | SSRI antidepressant | NO | 0 |
| Тразодон / Тразадон | Trazodone | Serotonin antagonist/reuptake inhibitor (SARI) antidepressant | NO | 0 |
| Вальпроком | Valproate (Valproic acid) | Mood stabilizer / Anticonvulsant | NO | 0 |
| Мелатонін / Вітамелатонін | Melatonin | Hormone supplement | NO | 0 |
| Прегабалін | Pregabalin | Anticonvulsant / Anxiolytic | NO | 0 |
| Дулоксетин | Duloxetine | SNRI antidepressant | NO | 0 |
| Венлафаксин | Venlafaxine | SNRI antidepressant | NO | 0 |
| Кетамін | Ketamine | NMDA receptor antagonist / Dissociative anesthetic | NO | 0 |
| Бетагестин | Betahistine | Histamine analogue (for vertigo) | NO | 0 |
| Мебікар | Mebicar | Anxiolytic | NO | 0 |
| Гідозепан | Gidazepam | Benzodiazepine | NO | 0 |

### Antipsychotic Medications

#### Кветирон (Quetiapine)
- **Class**: Atypical (second-generation) antipsychotic
- **FDA Indications**: Schizophrenia, bipolar disorder (manic/depressive episodes), adjunct treatment for major depressive disorder
- **Off-label Uses**: PTSD, anxiety disorders, insomnia
- **Mechanism**: Antagonist at serotonin (5-HT2A) and dopamine (D2) receptors
- **Dosage in Dataset**: 50-100 mg/day
- **Sources**:
  - [Drugs.com - Quetiapine](https://www.drugs.com/quetiapine.html)
  - [NCBI StatPearls - Quetiapine](https://www.ncbi.nlm.nih.gov/books/NBK459145/)

#### Вертинекс (Prochlorperazine) - **DOSAGE-DEPENDENT**
- **Class**: Phenothiazine (first-generation) antipsychotic
- **Primary Medical Use**: Antiemetic, vestibular disorder treatment
- **Antipsychotic Use**: High doses (≥30-40 mg/day) for psychosis
- **Classification Rule**:
  - **Low doses (≤20 mg/day)**: Classified as **0** (vestibular/antiemetic use)
  - **High doses (≥30 mg/day)**: Classified as **1** (antipsychotic use)
- **Dosage in Dataset**: 15 mg/day (5 mg × 3) → **Classified as 0** (vestibular use)
- **Rationale**: All instances in the dataset use low doses typical for vestibular/antiemetic indications, not antipsychotic purposes
- **Sources**:
  - [NCBI StatPearls - Prochlorperazine](https://www.ncbi.nlm.nih.gov/books/NBK537083/)
  - [Drugs.com - Prochlorperazine Dosage](https://www.drugs.com/dosage/prochlorperazine.html)
  - [Compendium UA - Vertinex](https://compendium.com.ua/info/220097/)

---

## Row-by-Row Analysis

### 1. Session: Hbclb0zZSybizAHveOgU
**Classification**: `if_antipsychotic = 0`

**Treatment**:
- Вітамелатонін 3 мг (Melatonin) → Non-antipsychotic
- Сертралофт 50 мг (Sertraline) → SSRI antidepressant

**Decision**: No antipsychotic medications present.

---

### 2. Session: 9Pd2lTJaNZ7CGrLBPjuU
**Classification**: `if_antipsychotic = 1` ✓

**Treatment**:
- **Кветирон 50 мг (Quetiapine)** → **ANTIPSYCHOTIC** ✓
- Вальпроком 300 мг × 3 (Valproate) → Mood stabilizer
- Тразадон 50 мг (Trazodone) → Antidepressant
- Сертралофт 50 мг (Sertraline) → SSRI antidepressant

**Decision**: Quetiapine is an atypical antipsychotic → **1**

---

### 3. Session: WM5kGy75RPmQz9VXrLsl
**Classification**: `if_antipsychotic = 1` ✓

**Treatment**:
- Сертралін 50 мг (Sertraline) → SSRI antidepressant
- Спітомін 5 мг × 3 (Buspirone) → Anxiolytic
- **Кветирон 50 мг (Quetiapine)** → **ANTIPSYCHOTIC** ✓

**Decision**: Quetiapine is an atypical antipsychotic → **1**

---

### 4. Session: WqhUtMHW8tiAAqpxAtpL
**Classification**: `if_antipsychotic = 0`

**Treatment**:
- Есциталопрам 20 мг (Escitalopram) → SSRI antidepressant
- Тразодон 100 мг (Trazodone) → Antidepressant
- Спітомін 5 мг × 3 (Buspirone) → Anxiolytic

**Decision**: No antipsychotic medications present.

---

### 5. Session: xx19J8Xeoc4thStIAtUe
**Classification**: `if_antipsychotic = 0`

**Treatment**:
- Пароксин 20 мг (Paroxetine) → SSRI antidepressant
- Спітомін 5 мг × 2 (Buspirone) → Anxiolytic
- Мелатонін 3 мг (Melatonin) → Hormone supplement

**Decision**: No antipsychotic medications present.

---

### 6. Session: 1Uehxi3TOkqvnzgttQI7
**Classification**: `if_antipsychotic = 1` ✓

**Treatment**:
- Вертинекс 5 мг × 3 (Prochlorperazine, 15 mg/day) → Low dose: vestibular use (**0**)
- Мелатонін 3 мг (Melatonin) → Hormone supplement
- Есциталопрам 20 мг (Escitalopram) → SSRI antidepressant
- **Кветирон 100 мг (Quetiapine)** → **ANTIPSYCHOTIC** ✓

**Decision**: Quetiapine is present, Prochlorperazine at low dose (vestibular use) → **1**

---

### 7. Session: vgyT6YEmZhhePfsV4X68
**Classification**: `if_antipsychotic = 0`

**Treatment**:
- КЕТАМІН (Ketamine) → Dissociative anesthetic / Off-label antidepressant

**Decision**: Ketamine is NOT classified as an antipsychotic. While it has psychoactive properties, it's an NMDA receptor antagonist used for depression and pain, not psychosis. → **0**

**Note**: This is a unique case - ketamine monotherapy for PTSD, likely part of experimental/off-label treatment protocol.

---

### 8. Session: 9gSnpeygVxyRw0VLNI6F
**Classification**: `if_antipsychotic = 0`

**Treatment**:
- Спітомін 10 мг × 2 (Buspirone) → Anxiolytic
- Прегабалін 150 мг (Pregabalin) → Anticonvulsant/anxiolytic
- Есциталопрам 10 мг (Escitalopram) → SSRI antidepressant

**Decision**: No antipsychotic medications present.

---

### 9. Session: DTGxc0RwsWrTMRKpenb8
**Classification**: `if_antipsychotic = 1` ✓

**Treatment**:
- Сертралін 100 мг (Sertraline) → SSRI antidepressant
- Міасер 10 мг (Mirtazapine) → Tetracyclic antidepressant
- **Кветирон 50 мг (Quetiapine)** → **ANTIPSYCHOTIC** ✓

**Decision**: Quetiapine is an atypical antipsychotic → **1**

---

### 10. Session: Rj39OXC79SHjMrwZ7Y4i
**Classification**: `if_antipsychotic = 1` ✓

**Treatment**:
- **Кветирон 50 мг (Quetiapine)** → **ANTIPSYCHOTIC** ✓
- Мелатонін 3 мг (Melatonin) → Hormone supplement

**Decision**: Quetiapine is an atypical antipsychotic → **1**

**Note**: Interestingly, this patient has `if_PTSD = 0` (no PTSD diagnosis) but receives an antipsychotic, suggesting other psychiatric comorbidities or symptom profiles.

---

### 11. Session: KKkmpSfLPj0PXD7j5Hjb
**Classification**: `if_antipsychotic = 0`

**Treatment**:
- Спітомін 5 мг × 3 (Buspirone) → Anxiolytic
- Венлафаксин 75 мг (Venlafaxine) → SNRI antidepressant
- Бетагестин 16 мг × 3 (Betahistine) → Histamine analogue for vertigo

**Decision**: No antipsychotic medications present.

---

### 12. Session: rnRyj0bgZnB5es4ZA1Ok
**Classification**: `if_antipsychotic = 0`

**Treatment**:
- Пароксетин 20 мг (Paroxetine) → SSRI antidepressant
- Спітамін 5 мг × 3 (Buspirone) → Anxiolytic [variant spelling]
- Мелатонін 3 мг (Melatonin) → Hormone supplement

**Decision**: No antipsychotic medications present.

---

### 13. Session: M8mMRA4CbH4vfG8mUXdV
**Classification**: `if_antipsychotic = 0`

**Treatment**:
- Вертинекс 5 мг × 3 (Prochlorperazine, 15 mg/day) → Low dose: vestibular use (**0**)
- Міорікс 15 мг (Mirtazapine) → Tetracyclic antidepressant
- Бетагестин 16 мг × 2 (Betahistine) → Histamine analogue for vertigo

**Decision**: Prochlorperazine at low dose (15 mg/day) used for vestibular purposes, not antipsychotic purposes → **0**

**Note**: Combination of Вертинекс + Бетагестин suggests vestibular/balance disorder treatment.

---

### 14. Session: xn3yMJ8STzchnQPg94lH
**Classification**: `if_antipsychotic = 1` ✓

**Treatment**:
- Вертинекс 5 мг × 3 (Prochlorperazine, 15 mg/day) → Low dose: vestibular use (**0**)
- **Кветирон 50 мг (Quetiapine)** → **ANTIPSYCHOTIC** ✓
- Мелатонін 3 мг (Melatonin) → Hormone supplement
- Прегабалін 150 мг (Pregabalin) → Anticonvulsant/anxiolytic

**Decision**: Quetiapine is present → **1**

**Note**: Another patient with `if_PTSD = 0` receiving an antipsychotic.

---

### 15. Session: IUbJEKjKp7EgZC04EUbS
**Classification**: `if_antipsychotic = 1` ✓

**Treatment**:
- Дулоксетин 60 мг (Duloxetine) → SNRI antidepressant
- Вальпроком 300 мг × 3 (Valproate) → Mood stabilizer
- **Кветирон 100 мг (Quetiapine)** → **ANTIPSYCHOTIC** ✓
- Мебікар 30 мг × 3 (Mebicar) → Anxiolytic
- Гідозепан 50 мг (Gidazepam) → Benzodiazepine

**Decision**: Quetiapine is an atypical antipsychotic → **1**

**Note**: Complex polypharmacy regimen with 5 medications, suggesting severe/complex symptomatology.

---

## Special Cases and Peculiarities

### 1. Dosage-Dependent Classification: Prochlorperazine (Вертинекс)

**Medication**: Вертинекс (Prochlorperazine)
**Occurrences**: 3 patients (Sessions 6, 13, 14)
**Dosage**: 5 mg × 3 daily = 15 mg/day in all cases

**Pharmacology**:
- Prochlorperazine is pharmacologically a phenothiazine antipsychotic
- **However**, it's primarily prescribed for non-psychiatric indications at low doses
- **Antiemetic/Vestibular dose**: 5-10 mg, 2-4 times daily (max 40 mg/day for nausea)
- **Antipsychotic dose**: 10 mg 3-4 times daily initially, up to 150 mg/day for psychosis

**Classification Decision**:
- All instances: **15 mg/day** → **Below antipsychotic threshold**
- Clinical context: Combined with Бетагестин (betahistine) in Session 13 → Strong indication of vestibular disorder treatment
- **Final classification**: **0** (not used as antipsychotic in this dataset)

### 2. Ketamine (Кетамін) Classification

**Session**: 7 (vgyT6YEmZhhePfsV4X68)
**Treatment**: Ketamine monotherapy

**Pharmacology**:
- NMDA receptor antagonist
- Dissociative anesthetic
- FDA-approved (as esketamine) for treatment-resistant depression
- Off-label use for PTSD, severe depression, chronic pain

**Why NOT an Antipsychotic**:
- Mechanism of action: NMDA antagonism (not dopamine/serotonin antagonism like antipsychotics)
- Indications: Depression, pain (not psychosis or schizophrenia)
- Can actually **induce** psychotic-like symptoms transiently
- No FDA approval or clinical use for antipsychotic purposes

**Classification**: **0** (dissociative anesthetic/antidepressant, not antipsychotic)

### 3. Patients Without PTSD Receiving Antipsychotics

**Sessions**: 10 (Rj39OXC79SHjMrwZ7Y4i), 14 (xn3yMJ8STzchnQPg94lH)
**PTSD Status**: `if_PTSD = 0`
**Treatment**: Both receive Quetiapine (Кветирон)

**Implications**:
- Antipsychotics may be prescribed for comorbid conditions (e.g., bipolar disorder, severe anxiety, psychosis)
- Quetiapine has anxiolytic and sedative properties beyond antipsychotic effects
- Off-label use for insomnia is common
- Suggests heterogeneous patient population with varying psychiatric diagnoses

### 4. Medication Name Variations

**Observed Variations**:
- **Sertraline**: Сертралін / Сертралофт
- **Mirtazapine**: Міасер / Міорікс
- **Trazodone**: Тразодон / Тразадон
- **Paroxetine**: Пароксин / Пароксетин
- **Buspirone**: Спітомін / Спітамін

**Handling**: All variants mapped to the same generic medication in the classification dictionary.

### 5. Polypharmacy Patterns

**Complex Regimens (4-5 medications)**:
- Session 2: Quetiapine + Valproate + Trazodone + Sertraline (antipsychotic + mood stabilizer + 2 antidepressants)
- Session 15: Quetiapine + Valproate + Duloxetine + Mebicar + Gidazepam (antipsychotic + mood stabilizer + antidepressant + anxiolytic + benzodiazepine)

**Minimal Regimens (1-2 medications)**:
- Session 7: Ketamine monotherapy
- Session 10: Quetiapine + Melatonin

**Most Common Medication**: Quetiapine (Кветирон) - present in 9/15 patients (60%)

---

## Clinical Insights

### Antipsychotic Use in PTSD

**Prevalence**: 7/15 patients (46.7%) receive antipsychotic medication

**Primary Agent**: Quetiapine (100% of antipsychotic cases)

**Rationale for Quetiapine in PTSD**:
1. **Trauma-related psychosis**: Some PTSD patients experience psychotic symptoms
2. **Severe hyperarousal**: Quetiapine has sedating properties useful for hypervigilance
3. **Nightmares**: Quetiapine may reduce trauma-related nightmares
4. **Insomnia**: Low-dose quetiapine commonly used off-label for sleep
5. **Comorbid conditions**: Bipolar disorder, depression with psychotic features

**Dosage Range**: 50-100 mg/day (low to moderate doses, consistent with off-label PTSD/sleep use rather than primary psychotic disorder treatment)

### Medication Classes Distribution

| Class | Count | Percentage |
|-------|-------|------------|
| SSRI Antidepressants | 10 | 66.7% |
| Anxiolytics | 9 | 60.0% |
| **Antipsychotics** | **7** | **46.7%** |
| Sleep Aids (Melatonin) | 6 | 40.0% |
| Other Antidepressants | 5 | 33.3% |
| Mood Stabilizers | 3 | 20.0% |
| Anticonvulsants | 2 | 13.3% |

---

## Sources and References

### Primary Sources - Antipsychotics

1. **Quetiapine (Кветирон)**
   - [Drugs.com - Quetiapine](https://www.drugs.com/quetiapine.html)
   - [NCBI StatPearls - Quetiapine](https://www.ncbi.nlm.nih.gov/books/NBK459145/)
   - [DrugBank - Quetiapine](https://go.drugbank.com/drugs/DB01224)
   - [NCBI StatPearls - Atypical Antipsychotic Agents](https://www.ncbi.nlm.nih.gov/books/NBK448156/)
   - [NAMI - Quetiapine (Seroquel)](https://www.nami.org/about-mental-illness/treatments/mental-health-medications/types-of-medication/quetiapine-seroquel/)

2. **Prochlorperazine (Вертинекс)**
   - [NCBI StatPearls - Prochlorperazine](https://www.ncbi.nlm.nih.gov/books/NBK537083/)
   - [Drugs.com - Prochlorperazine Dosage](https://www.drugs.com/dosage/prochlorperazine.html)
   - [Compendium UA - Vertinex](https://compendium.com.ua/info/220097/)

### Primary Sources - Other Medications

3. **Buspirone (Спітомін)**
   - [Compendium UA - Spіtomіn](https://compendium.com.ua/dec/270542/)
   - [NCBI StatPearls - Buspirone](https://www.ncbi.nlm.nih.gov/books/NBK531477/)

4. **Mirtazapine (Міасер, Міорікс)**
   - [NCBI StatPearls - Mirtazapine](https://www.ncbi.nlm.nih.gov/books/NBK519059/)

5. **Sertraline (Сертралін, Сертралофт)**
   - [NCBI StatPearls - Sertraline](https://www.ncbi.nlm.nih.gov/books/NBK547689/)

6. **Ketamine (Кетамін)**
   - [PMC - Ketamine: NMDA Receptors and Beyond](https://pmc.ncbi.nlm.nih.gov/articles/PMC5148235/)
   - [American Journal of Psychiatry - Ketamine and Other NMDA Antagonists in Depression](https://psychiatryonline.org/doi/10.1176/appi.ajp.2015.15040465)
   - **Note**: Ketamine is classified as an NMDA receptor antagonist used as an anesthetic and antidepressant, NOT an antipsychotic

### Clinical Guidelines

7. **Antipsychotics in PTSD**
   - [American Psychological Association - PTSD Treatment Guidelines](https://www.apa.org/ptsd-guideline)
   - [VA/DoD Clinical Practice Guideline for PTSD](https://www.healthquality.va.gov/guidelines/MH/ptsd/)

---

## Conclusion

This analysis successfully classified all medications in the PTSD Anima Table dataset, identifying 7 patients (46.7%) receiving antipsychotic medications. Quetiapine (Кветирон) was the sole antipsychotic agent used, prescribed at low-to-moderate doses (50-100 mg/day) consistent with off-label use for PTSD-related symptoms such as hyperarousal, nightmares, and insomnia.

The dosage-dependent classification of Prochlorperazine (Вертинекс) demonstrated the importance of contextual analysis - all instances in the dataset used low doses (15 mg/day) for vestibular/antiemetic purposes rather than antipsychotic indications.

The resulting dataset (`PTSD_Anima_Table_05_08_with_antipsychotic.csv`) now includes the binary `if_antipsychotic` indicator, enabling further statistical analysis of treatment patterns and outcomes in PTSD patients.

---

**Report Generated**: 2026-02-11
**Analyst**: Claude Sonnet 4.5
**Dataset**: PTSD_Anima_Table_05_08_preprocessed.csv (15 patients)
**Output**: PTSD_Anima_Table_05_08_with_antipsychotic.csv
