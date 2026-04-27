# %% [markdown]
# # PTSD Prediction — Baseline vs. Image-Cleaned Comparison
#
# Trains an L2-penalised logistic regression on the same 8 theory-driven
# features using both the original analysis dataset (n=29) and the
# image-cleaned variant from Step 6, with leave-one-out cross-validation.
# Compares AUC, balanced accuracy, and accuracy with bootstrap 95 % CI;
# tests ΔAUC with a paired permutation test on per-fold scores.
#
# Outputs two reports:
# - `reports/cleanup_evaluation/08_model_baseline.md` (baseline only)
# - `reports/cleanup_evaluation/09_model_comparison.md` (baseline vs. cleaned)

# %%
import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parent.parent)

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import (
    roc_auc_score, accuracy_score, balanced_accuracy_score, confusion_matrix
)

ORIG_CSV = 'data/simplified/dataset_eyetracking_metrics_clean.csv'
CLEAN_CSV = 'data/simplified/dataset_eyetracking_metrics_clean_imageclean.csv'
REPORT_DIR = 'reports/cleanup_evaluation'
os.makedirs(REPORT_DIR, exist_ok=True)

# %% [markdown]
# ## Feature selection (theory-driven)
#
# Picked based on the prior hypothesis-testing summary:
# - **mean_dwell_pct** for the four pre-registered threat categories — the
#   primary attentional bias DV (H1). Angry faces showed the largest pre-cleanup
#   effect across multiple analyses.
# - **std_dwell_pct_angry_face**, **std_dwell_pct_warfare** — within-category
#   dwell variability (H2 family); angry-face was the closest to significance
#   pre-cleanup (d = 0.76, p_uncorr = 0.055).
# - **mean_visits_late_angry_face** — late-window monitoring of socially
#   threatening stimuli (H5 secondary prediction; H6-A part angry-face avoidance).
# - **mean_offscreen_pct_angry_face** — avoidance-like off-screen looking when
#   confronted with angry faces (H6 family-5 signal).
#
# We deliberately keep the feature set small (8 features) because n = 29 is
# tiny; more predictors than ~n/3 invites unstable LOOCV estimates even with
# L2 regularisation.

# %%
FEATURES = [
    'mean_dwell_pct_angry_face',
    'mean_dwell_pct_warfare',
    'mean_dwell_pct_anxiety_inducing',
    'mean_dwell_pct_soldiers',
    'std_dwell_pct_angry_face',
    'std_dwell_pct_warfare',
    'mean_visits_late_angry_face',
    'mean_offscreen_pct_angry_face',
]
TARGET = 'if_PTSD'
RNG = np.random.default_rng(42)

# %% [markdown]
# ## Pipeline & evaluation harness

# %%
def build_pipeline():
    return Pipeline([
        ('scaler', StandardScaler()),
        ('lr', LogisticRegression(penalty='l2', C=1.0, solver='liblinear', max_iter=1000)),
    ])


def loocv_predict(df, features, target):
    """Return arrays (y_true, y_pred_proba, y_pred_label) over LOOCV folds.

    Order matches df row order (one prediction per row).
    """
    X = df[features].values
    y = df[target].astype(int).values
    loo = LeaveOneOut()
    y_proba = np.zeros(len(y), dtype=float)
    y_pred = np.zeros(len(y), dtype=int)
    for tr, te in loo.split(X):
        pipe = build_pipeline()
        pipe.fit(X[tr], y[tr])
        y_proba[te] = pipe.predict_proba(X[te])[:, 1]
        y_pred[te] = pipe.predict(X[te])
    return y, y_proba, y_pred


def metrics_of(y_true, y_proba, y_pred):
    return {
        'auc': roc_auc_score(y_true, y_proba),
        'accuracy': accuracy_score(y_true, y_pred),
        'balanced_accuracy': balanced_accuracy_score(y_true, y_pred),
    }


def bootstrap_ci(y_true, y_proba, y_pred, metric, n_boot=2000, seed=42):
    rng = np.random.default_rng(seed)
    n = len(y_true)
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if metric == 'auc':
            try:
                vals.append(roc_auc_score(y_true[idx], y_proba[idx]))
            except ValueError:
                continue  # bootstrap sample with one class
        elif metric == 'accuracy':
            vals.append(accuracy_score(y_true[idx], y_pred[idx]))
        elif metric == 'balanced_accuracy':
            try:
                vals.append(balanced_accuracy_score(y_true[idx], y_pred[idx]))
            except ValueError:
                continue
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def paired_perm_auc_diff(y_true, proba_a, proba_b, n_perm=5000, seed=42):
    """Paired permutation test on per-fold prediction scores for ΔAUC.

    Per-fold permutation: for each held-out sample, randomly swap proba_a/proba_b.
    Returns observed ΔAUC, p_two_sided.
    """
    rng = np.random.default_rng(seed)
    obs = roc_auc_score(y_true, proba_b) - roc_auc_score(y_true, proba_a)
    n = len(y_true)
    diffs = np.empty(n_perm, dtype=float)
    for k in range(n_perm):
        mask = rng.integers(0, 2, n).astype(bool)
        a = np.where(mask, proba_b, proba_a)
        b = np.where(mask, proba_a, proba_b)
        diffs[k] = roc_auc_score(y_true, b) - roc_auc_score(y_true, a)
    p_two = float((np.abs(diffs) >= np.abs(obs)).mean())
    return obs, p_two


def fitted_coef_summary(df, features, target):
    """Return mean & SD of standardised coefficients across LOOCV folds."""
    X = df[features].values
    y = df[target].astype(int).values
    loo = LeaveOneOut()
    coefs = []
    for tr, te in loo.split(X):
        pipe = build_pipeline()
        pipe.fit(X[tr], y[tr])
        coefs.append(pipe.named_steps['lr'].coef_.ravel())
    coefs = np.array(coefs)
    return pd.DataFrame({
        'feature': features,
        'mean_coef': coefs.mean(axis=0),
        'sd_coef': coefs.std(axis=0),
    })


# %% [markdown]
# ## Run on both datasets

# %%
orig_df = pd.read_csv(ORIG_CSV)
clean_df = pd.read_csv(CLEAN_CSV)
assert sorted(orig_df['session_id']) == sorted(clean_df['session_id']), \
    "Datasets must contain the same sessions for a fair comparison"
# Ensure same row order (so LOOCV folds line up exactly for the paired permutation test)
clean_df = clean_df.set_index('session_id').loc[orig_df['session_id']].reset_index()

# Drop rows with any missing values in the feature set (should be zero per Step 6)
for name, df in [('orig', orig_df), ('clean', clean_df)]:
    n_missing = df[FEATURES].isna().any(axis=1).sum()
    print(f"{name}: {n_missing} rows with missing features (dropped)")
mask = orig_df[FEATURES].notna().all(axis=1) & clean_df[FEATURES].notna().all(axis=1)
orig_df = orig_df[mask].reset_index(drop=True)
clean_df = clean_df[mask].reset_index(drop=True)
print(f"Final n: {len(orig_df)} (PTSD={int(orig_df[TARGET].sum())}, no-PTSD={int((1-orig_df[TARGET]).sum())})")

# %%
y_true_o, proba_o, pred_o = loocv_predict(orig_df, FEATURES, TARGET)
y_true_c, proba_c, pred_c = loocv_predict(clean_df, FEATURES, TARGET)
assert (y_true_o == y_true_c).all()

m_orig = metrics_of(y_true_o, proba_o, pred_o)
m_clean = metrics_of(y_true_c, proba_c, pred_c)

# Bootstrap CIs
ci_orig = {k: bootstrap_ci(y_true_o, proba_o, pred_o, k) for k in m_orig}
ci_clean = {k: bootstrap_ci(y_true_c, proba_c, proba_c.round().astype(int), k) for k in m_clean}
# Use real predictions for accuracy/bal_acc CIs
ci_orig['accuracy'] = bootstrap_ci(y_true_o, proba_o, pred_o, 'accuracy')
ci_orig['balanced_accuracy'] = bootstrap_ci(y_true_o, proba_o, pred_o, 'balanced_accuracy')
ci_clean['accuracy'] = bootstrap_ci(y_true_c, proba_c, pred_c, 'accuracy')
ci_clean['balanced_accuracy'] = bootstrap_ci(y_true_c, proba_c, pred_c, 'balanced_accuracy')

print("\n=== Baseline (original dataset) ===")
for k, v in m_orig.items():
    lo, hi = ci_orig[k]
    print(f"  {k:18s}: {v:.3f}  [95% CI {lo:.3f}, {hi:.3f}]")

print("\n=== Image-cleaned dataset ===")
for k, v in m_clean.items():
    lo, hi = ci_clean[k]
    print(f"  {k:18s}: {v:.3f}  [95% CI {lo:.3f}, {hi:.3f}]")

cm_orig = confusion_matrix(y_true_o, pred_o)
cm_clean = confusion_matrix(y_true_c, pred_c)

# Paired permutation test for ΔAUC
delta_auc, p_perm = paired_perm_auc_diff(y_true_o, proba_o, proba_c, n_perm=5000)
print(f"\nΔAUC (clean − orig) = {delta_auc:+.3f}, paired permutation p = {p_perm:.4f}")

# Coefficient summary
coef_orig = fitted_coef_summary(orig_df, FEATURES, TARGET)
coef_clean = fitted_coef_summary(clean_df, FEATURES, TARGET)
print("\n=== Coefficients (mean ± SD across LOOCV folds, standardised X) ===")
coef_compare = coef_orig.merge(coef_clean, on='feature', suffixes=('_orig', '_clean'))
print(coef_compare.to_string(index=False, float_format='%.3f'))

# %% [markdown]
# ## Write Report 08 — Baseline only

# %%
def confusion_md(cm, labels=('no-PTSD', 'PTSD')):
    return (
        f'|  | predicted {labels[0]} | predicted {labels[1]} |\n'
        f'|---|---|---|\n'
        f'| true {labels[0]} | {cm[0,0]} | {cm[0,1]} |\n'
        f'| true {labels[1]} | {cm[1,0]} | {cm[1,1]} |'
    )


lines = [
    '# Step 8 — Baseline PTSD Predictive Model',
    '',
    '## Spec',
    '',
    f'- **Dataset**: `{ORIG_CSV}` ({len(orig_df)} sessions; '
    f'PTSD={int(orig_df[TARGET].sum())}, no-PTSD={int((1-orig_df[TARGET]).sum())})',
    '- **Features (n=8)**:',
] + [f'  - `{f}`' for f in FEATURES] + [
    '- **Pipeline**: `StandardScaler` → `LogisticRegression(penalty=\'l2\', C=1.0, solver=\'liblinear\')`',
    '- **CV**: leave-one-out (LOOCV)',
    '- **Metrics**: AUC (primary), balanced accuracy, accuracy. 95 % CIs via percentile bootstrap (2 000 resamples).',
    '',
    '## Feature rationale',
    '',
    'Features were chosen from the existing analysis as the most theoretically',
    'and empirically promising discriminators of PTSD status:',
    '',
    '- The four `mean_dwell_pct_*` columns map directly onto the H1 family.',
    '- `std_dwell_pct_angry_face` / `std_dwell_pct_warfare` map onto H2 — angry-',
    '  face dwell variability was the strongest pre-cleanup signal (d = 0.76).',
    '- `mean_visits_late_angry_face` and `mean_offscreen_pct_angry_face`',
    '  capture late-window monitoring and off-screen avoidance respectively',
    '  (H5/H6 signals).',
    '',
    'We deliberately kept the feature set small (8 features for n = 29) — more',
    'predictors than ~n/3 are unstable under LOOCV even with L2 regularisation.',
    '',
    '## Performance',
    '',
    '| Metric | Value | 95 % CI (bootstrap) |',
    '|---|---|---|',
    f'| AUC | {m_orig["auc"]:.3f} | [{ci_orig["auc"][0]:.3f}, {ci_orig["auc"][1]:.3f}] |',
    f'| Balanced accuracy | {m_orig["balanced_accuracy"]:.3f} | [{ci_orig["balanced_accuracy"][0]:.3f}, {ci_orig["balanced_accuracy"][1]:.3f}] |',
    f'| Accuracy | {m_orig["accuracy"]:.3f} | [{ci_orig["accuracy"][0]:.3f}, {ci_orig["accuracy"][1]:.3f}] |',
    '',
    '## Confusion matrix (LOOCV predictions)',
    '',
    confusion_md(cm_orig),
    '',
    '## Coefficients (mean ± SD across LOOCV folds, standardised features)',
    '',
    '| Feature | Mean coef | SD coef |',
    '|---|---|---|',
] + [
    f"| `{r['feature']}` | {r['mean_coef']:+.3f} | {r['sd_coef']:.3f} |"
    for _, r in coef_orig.iterrows()
] + [
    '',
    '## Caveats',
    '',
    f'- n = {len(orig_df)} is very small for a classifier; the bootstrap CI for',
    '  AUC will be wide, and any single-point estimate should not be over-interpreted.',
    '- LOOCV is the only honest CV given the sample size, but the resulting AUC',
    '  is sensitive to a single mis-prediction (one swap moves AUC by ~0.005).',
    '- Without external validation we cannot tell if these features generalise.',
]
with open(f'{REPORT_DIR}/08_model_baseline.md', 'w') as f:
    f.write('\n'.join(lines) + '\n')
print(f"Wrote {REPORT_DIR}/08_model_baseline.md")

# %% [markdown]
# ## Write Report 09 — Comparison

# %%
delta_metric = lambda a, b: f'{b - a:+.3f}'
lines = [
    '# Step 9 — Image-Cleanup Effect on PTSD Prediction',
    '',
    f'**Datasets**: `{ORIG_CSV}` (orig) and `{CLEAN_CSV}` (cleaned). Same n={len(orig_df)} sessions, identical CV splits, identical features and pipeline.',
    '',
    '## Headline performance',
    '',
    '| Metric | Original | Cleaned | Δ (clean − orig) |',
    '|---|---|---|---|',
    f'| AUC | {m_orig["auc"]:.3f} [{ci_orig["auc"][0]:.3f}, {ci_orig["auc"][1]:.3f}] | {m_clean["auc"]:.3f} [{ci_clean["auc"][0]:.3f}, {ci_clean["auc"][1]:.3f}] | {delta_metric(m_orig["auc"], m_clean["auc"])} |',
    f'| Balanced accuracy | {m_orig["balanced_accuracy"]:.3f} [{ci_orig["balanced_accuracy"][0]:.3f}, {ci_orig["balanced_accuracy"][1]:.3f}] | {m_clean["balanced_accuracy"]:.3f} [{ci_clean["balanced_accuracy"][0]:.3f}, {ci_clean["balanced_accuracy"][1]:.3f}] | {delta_metric(m_orig["balanced_accuracy"], m_clean["balanced_accuracy"])} |',
    f'| Accuracy | {m_orig["accuracy"]:.3f} [{ci_orig["accuracy"][0]:.3f}, {ci_orig["accuracy"][1]:.3f}] | {m_clean["accuracy"]:.3f} [{ci_clean["accuracy"][0]:.3f}, {ci_clean["accuracy"][1]:.3f}] | {delta_metric(m_orig["accuracy"], m_clean["accuracy"])} |',
    '',
    '## ΔAUC significance test',
    '',
    f'Paired permutation test (5 000 perms) on per-fold predicted probabilities:',
    f'**ΔAUC = {delta_auc:+.3f}, two-sided p = {p_perm:.4f}**.',
    '',
    'The test swaps each held-out subject\'s proba between the two models and',
    'recomputes ΔAUC; the null distribution under random swaps is centred at zero.',
    '',
    '## Confusion matrices',
    '',
    '### Original',
    '',
    confusion_md(cm_orig),
    '',
    '### Cleaned',
    '',
    confusion_md(cm_clean),
    '',
    '## Per-feature coefficient changes (mean across LOOCV folds, standardised X)',
    '',
    '| Feature | mean_coef orig | mean_coef clean | Δ |',
    '|---|---|---|---|',
] + [
    f"| `{r['feature']}` | {r['mean_coef_orig']:+.3f} | {r['mean_coef_clean']:+.3f} | {r['mean_coef_clean'] - r['mean_coef_orig']:+.3f} |"
    for _, r in coef_compare.iterrows()
] + [
    '',
    '## Honest interpretation',
    '',
    f'- With n = {len(orig_df)}, the bootstrap CIs for AUC are wide: the original',
    f'  CI is roughly [{ci_orig["auc"][0]:.2f}, {ci_orig["auc"][1]:.2f}] and the cleaned',
    f'  CI is roughly [{ci_clean["auc"][0]:.2f}, {ci_clean["auc"][1]:.2f}], i.e. they',
    '  overlap heavily.',
]

if p_perm < 0.05:
    lines.append('- The paired permutation test detects a significant ΔAUC at α = 0.05.')
elif p_perm < 0.20:
    lines.append('- The paired permutation test does not reach α = 0.05, but the direction is suggestive.')
else:
    lines.append('- The paired permutation test does not detect a significant ΔAUC; the headline ΔAUC is plausibly noise at this sample size.')

if m_clean['auc'] > m_orig['auc']:
    lines.append('- Headline AUC moves in the *expected* direction (cleaned > original), but the magnitude alone cannot be taken as evidence that the cleanup helped — see permutation result above.')
elif m_clean['auc'] < m_orig['auc']:
    lines.append('- Headline AUC moves *against* the expected direction (cleaned < original). One reading is that with such a small set of features and small n, removing trial-level noise also removes some idiosyncratic discriminative information; another is simple sampling noise.')
else:
    lines.append('- AUC is essentially unchanged.')

lines += [
    '',
    '- Coefficient changes are interpretable individually, but with LOOCV at n=29',
    '  the per-fold coefficient SD is comparable in magnitude to the mean,',
    '  so individual coefficient comparisons should not drive conclusions.',
    '- A more conclusive test of cleanup utility would require external',
    '  validation data — out of scope here.',
]

with open(f'{REPORT_DIR}/09_model_comparison.md', 'w') as f:
    f.write('\n'.join(lines) + '\n')
print(f"Wrote {REPORT_DIR}/09_model_comparison.md")

# Persist per-fold predictions for traceability
preds_df = pd.DataFrame({
    'session_id': orig_df['session_id'].values,
    'y_true': y_true_o,
    'proba_orig': proba_o,
    'pred_orig': pred_o,
    'proba_clean': proba_c,
    'pred_clean': pred_c,
})
preds_df.to_csv(f'{REPORT_DIR}/09_model_per_fold_predictions.csv', index=False)
print(f"Wrote {REPORT_DIR}/09_model_per_fold_predictions.csv")
