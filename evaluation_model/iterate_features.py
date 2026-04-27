# %% [markdown]
# # PTSD Predictor — Feature-Set Iteration on the Cleaned Dataset
#
# Tries three principled feature sets (≤ 6 features each) on the
# image-cleaned per-category dataset, scores each by LOOCV AUC + bootstrap
# 95 % CI, picks the winner, and re-runs the winner on the un-image-cleaned
# dataset as a backward check.
#
# `nose_dist_norm` is merged in from `data/simplified/dataset_merged_1_and_2.csv`
# (col 175). `blink_count` is deliberately not used (low data quality at
# this eye-tracker's sample frequency — see project history).

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

CLEAN_CSV = 'data/simplified/dataset_eyetracking_metrics_clean_imageclean.csv'
ORIG_CSV = 'data/simplified/dataset_eyetracking_metrics_clean.csv'
MERGED_CSV = 'data/simplified/dataset_merged_1_and_2.csv'
REPORT_DIR = 'reports/cleanup_evaluation'
os.makedirs(REPORT_DIR, exist_ok=True)

TARGET = 'if_PTSD'
RNG_SEED = 42

# %% [markdown]
# ## Candidate feature sets

# %%
# `nose_dist_norm` was dropped from all candidates after the outlier analysis
# showed the feature's predictive value collapsed (AUC 0.637 → 0.560) when
# the top 3 PTSD participants were removed. Right-skewed distribution with
# medians nearly equal across groups (471 PTSD vs 425 no-PTSD); the
# discriminative signal sat in 3-4 extreme PTSD individuals — likely a
# tracker quality issue rather than a real PTSD-related head-movement effect.
# Same failure mode as `blink_count`. See exploration in conversation history.

CANDIDATES = {
    'A2_reference_minus_nose': [
        'std_dwell_pct_happy_event',
        'std_dwell_pct_combat_vehicles',
        'std_dwell_pct_angry_face',
        'std_dwell_pct_neutral',
    ],
    'B_h1_h6_driven': [
        'std_dwell_pct_angry_face',
        'std_dwell_pct_warfare',
        'mean_dwell_pct_angry_face',
        'mean_dwell_pct_warfare',
        'mean_offscreen_pct_angry_face',
        'mean_visits_late_angry_face',
    ],
    'D_threat_stds_only': [
        # Pre-registered 4 threat categories' dwell-time SDs — directly tests
        # H2 (PTSD shows higher within-category SD on threat).
        'std_dwell_pct_angry_face',
        'std_dwell_pct_warfare',
        'std_dwell_pct_soldiers',
        'std_dwell_pct_anxiety_inducing',
    ],
    'F_broad_stds': [
        # 4 pre-registered threat SDs + the 2 non-threat SDs from the
        # reference model (combat_vehicles, happy_event). Tests whether
        # broad-coverage SDs beat threat-only SDs.
        'std_dwell_pct_angry_face',
        'std_dwell_pct_warfare',
        'std_dwell_pct_soldiers',
        'std_dwell_pct_anxiety_inducing',
        'std_dwell_pct_combat_vehicles',
        'std_dwell_pct_happy_event',
    ],
}

# %% [markdown]
# ## Helpers

# %%
def build_pipeline():
    return Pipeline([
        ('scaler', StandardScaler()),
        ('lr', LogisticRegression(
            penalty='l2', C=1.0, solver='liblinear',
            class_weight='balanced', max_iter=2000,
        )),
    ])


def loocv_predict(df, features, target):
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


def fitted_coef_summary(df, features, target):
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


def bootstrap_ci(y_true, y_proba, y_pred, metric, n_boot=2000, seed=RNG_SEED):
    rng = np.random.default_rng(seed)
    n = len(y_true)
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        try:
            if metric == 'auc':
                vals.append(roc_auc_score(y_true[idx], y_proba[idx]))
            elif metric == 'accuracy':
                vals.append(accuracy_score(y_true[idx], y_pred[idx]))
            elif metric == 'balanced_accuracy':
                vals.append(balanced_accuracy_score(y_true[idx], y_pred[idx]))
        except ValueError:
            continue  # bootstrap sample with one class
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def metrics_with_ci(y_true, y_proba, y_pred):
    out = {
        'auc': roc_auc_score(y_true, y_proba),
        'balanced_accuracy': balanced_accuracy_score(y_true, y_pred),
        'accuracy': accuracy_score(y_true, y_pred),
    }
    out['auc_ci'] = bootstrap_ci(y_true, y_proba, y_pred, 'auc')
    out['balanced_accuracy_ci'] = bootstrap_ci(y_true, y_proba, y_pred, 'balanced_accuracy')
    out['accuracy_ci'] = bootstrap_ci(y_true, y_proba, y_pred, 'accuracy')
    return out


def univariate_aucs(df, features, target):
    """Sanity: AUC of each feature taken alone (sign-flipped if negative)."""
    rows = []
    y = df[target].astype(int).values
    for f in features:
        x = df[f].values
        try:
            a = roc_auc_score(y, x)
        except ValueError:
            a = np.nan
        # Report AUC with sign flipped if < 0.5 to make it always >= 0.5
        a_aligned = max(a, 1 - a) if not np.isnan(a) else np.nan
        rows.append({'feature': f, 'univariate_auc': a, 'aligned': a_aligned})
    return pd.DataFrame(rows)


# %% [markdown]
# ## Load datasets
#
# All candidates use only columns already present in the per-category
# datasets. `nose_dist_norm` is no longer merged in (see comment above
# CANDIDATES for the rejection rationale).

# %%
clean = pd.read_csv(CLEAN_CSV)
orig = pd.read_csv(ORIG_CSV)

# Align row order (cleaned and orig must match for the backward check to be paired)
orig = orig.set_index('session_id').loc[clean['session_id']].reset_index()
print(f"Aligned: {len(clean)} sessions; PTSD={int(clean[TARGET].sum())}, no-PTSD={int((1 - clean[TARGET]).sum())}")

# %% [markdown]
# ## Run all three candidates on the cleaned dataset

# %%
results = {}
per_fold = {'session_id': clean['session_id'].values, 'y_true': clean[TARGET].astype(int).values}

print("=" * 90)
print("CANDIDATE EVALUATIONS — image-cleaned dataset (n = {})".format(len(clean)))
print("=" * 90)

for name, feats in CANDIDATES.items():
    print(f"\n--- {name} ({len(feats)} features) ---")
    print("  features:")
    for f in feats:
        print(f"    - {f}")

    y, proba, pred = loocv_predict(clean, feats, TARGET)
    m = metrics_with_ci(y, proba, pred)
    coef = fitted_coef_summary(clean, feats, TARGET)
    uni = univariate_aucs(clean, feats, TARGET)

    results[name] = {
        'features': feats,
        'metrics': m,
        'coef': coef,
        'univariate': uni,
        'cm': confusion_matrix(y, pred),
        'proba': proba,
        'pred': pred,
    }
    per_fold[f'proba_{name}'] = proba
    per_fold[f'pred_{name}'] = pred

    print(f"  AUC               : {m['auc']:.3f}  [95% CI {m['auc_ci'][0]:.3f}, {m['auc_ci'][1]:.3f}]")
    print(f"  Balanced accuracy : {m['balanced_accuracy']:.3f}  [95% CI {m['balanced_accuracy_ci'][0]:.3f}, {m['balanced_accuracy_ci'][1]:.3f}]")
    print(f"  Accuracy          : {m['accuracy']:.3f}  [95% CI {m['accuracy_ci'][0]:.3f}, {m['accuracy_ci'][1]:.3f}]")
    print(f"  Coefficients (mean ± SD across folds, standardised X):")
    for _, r in coef.iterrows():
        print(f"    {r['feature']:36s}  {r['mean_coef']:+.3f} ± {r['sd_coef']:.3f}")
    print(f"  Univariate AUC (sanity, 'aligned' = max(AUC, 1-AUC)):")
    for _, r in uni.iterrows():
        a = r['univariate_auc']
        a_str = '  nan' if np.isnan(a) else f'{a:.3f}'
        print(f"    {r['feature']:36s}  raw={a_str}  aligned={r['aligned']:.3f}")

# %% [markdown]
# ## Pick winner

# %%
ranked = sorted(
    results.items(),
    key=lambda kv: (-kv[1]['metrics']['auc'], -kv[1]['metrics']['balanced_accuracy']),
)
print("\n" + "=" * 90)
print("RANKING (by AUC, ties broken by balanced accuracy):")
for i, (n, r) in enumerate(ranked, 1):
    print(f"  {i}. {n}  AUC={r['metrics']['auc']:.3f}  bal_acc={r['metrics']['balanced_accuracy']:.3f}")

winner_name, winner = ranked[0]
print(f"\nWinner: {winner_name}")

# %% [markdown]
# ## Backward check — winner on uncleaned dataset

# %%
print("\n" + "=" * 90)
print(f"BACKWARD CHECK — {winner_name} on the original dataset (un-image-cleaned)")
print("=" * 90)

y_o, proba_o, pred_o = loocv_predict(orig, winner['features'], TARGET)
m_o = metrics_with_ci(y_o, proba_o, pred_o)
coef_o = fitted_coef_summary(orig, winner['features'], TARGET)

print(f"  AUC               : {m_o['auc']:.3f}  [95% CI {m_o['auc_ci'][0]:.3f}, {m_o['auc_ci'][1]:.3f}]")
print(f"  Balanced accuracy : {m_o['balanced_accuracy']:.3f}  [95% CI {m_o['balanced_accuracy_ci'][0]:.3f}, {m_o['balanced_accuracy_ci'][1]:.3f}]")
print(f"  Accuracy          : {m_o['accuracy']:.3f}  [95% CI {m_o['accuracy_ci'][0]:.3f}, {m_o['accuracy_ci'][1]:.3f}]")

# Paired permutation test on the per-fold probabilities (cleaned vs original)
def paired_perm_auc_diff(y_true, proba_a, proba_b, n_perm=5000, seed=RNG_SEED):
    rng = np.random.default_rng(seed)
    obs = roc_auc_score(y_true, proba_b) - roc_auc_score(y_true, proba_a)
    n = len(y_true)
    diffs = np.empty(n_perm, dtype=float)
    for k in range(n_perm):
        mask = rng.integers(0, 2, n).astype(bool)
        a = np.where(mask, proba_b, proba_a)
        b = np.where(mask, proba_a, proba_b)
        diffs[k] = roc_auc_score(y_true, b) - roc_auc_score(y_true, a)
    return obs, float((np.abs(diffs) >= np.abs(obs)).mean())

delta_auc, p_perm = paired_perm_auc_diff(y_o, proba_o, winner['proba'])
print(f"\nΔAUC (cleaned − original) on the *winning* feature set: {delta_auc:+.3f}, paired-perm p = {p_perm:.4f}")

# Save per-fold predictions for traceability
per_fold[f'proba_orig_{winner_name}'] = proba_o
per_fold[f'pred_orig_{winner_name}'] = pred_o
pf_df = pd.DataFrame(per_fold)
pf_df.to_csv(f'{REPORT_DIR}/11_model_iteration_per_fold_predictions.csv', index=False)
print(f"\nSaved: {REPORT_DIR}/11_model_iteration_per_fold_predictions.csv")

# %% [markdown]
# ## Write report

# %%
def confusion_md(cm, labels=('no-PTSD', 'PTSD')):
    return (
        f'|  | predicted {labels[0]} | predicted {labels[1]} |\n'
        f'|---|---|---|\n'
        f'| true {labels[0]} | {cm[0,0]} | {cm[0,1]} |\n'
        f'| true {labels[1]} | {cm[1,0]} | {cm[1,1]} |'
    )


lines = [
    '# Step 11 — PTSD Predictor: Feature-Set Iteration',
    '',
    '## Why we iterated',
    '',
    'The Step 8/9 PTSD predictor was a quick feasibility model picked to keep the',
    'image-cleanup comparison fair, not optimised for performance (AUC 0.574 / 0.480',
    'on original / cleaned with 8 mostly mean-dwell features). A reference model from',
    'a prior analysis (`/Users/bohdantsymbal/Downloads/model_summary.txt`) reached',
    'AUC = 0.820 on a slightly different sample with 6 features, leaning heavily on',
    '**dwell-time SDs across multiple categories**.',
    '',
    'This step tests several principled feature sets on the image-cleaned dataset',
    '(n = 29) and re-runs the winner on the un-image-cleaned dataset as a backward',
    'check.',
    '',
    '## Excluded features and why',
    '',
    "- **`blink_count`** — flagged as low-quality (eye-tracker sample rate too low to",
    '  detect blinks reliably; outlier sessions already removed for this reason). The',
    '  reference model used it but was inflated by one extreme participant; we drop it.',
    "- **`nose_dist_norm`** (head-trajectory length) — initial iteration found it the",
    '  strongest non-gaze feature, but a follow-up exploration showed the same outlier',
    "  pathology as `blink_count`: PTSD vs no-PTSD medians are almost equal (471 vs",
    '  425), the discriminative signal sits in the upper tail (4 of 5 Tukey outliers',
    "  are PTSD, including a 2218 maximum), and dropping the top 3 PTSD participants",
    '  collapses the univariate AUC from 0.637 to 0.560. Most likely a tracker',
    "  quality issue rather than a real PTSD-related head-movement effect. Dropped.",
    '',
    '## Decisions (locked)',
    '',
    "- **Pipeline**: `StandardScaler → LogisticRegression(penalty='l2', C=1.0,",
    "  solver='liblinear', class_weight='balanced')`. `class_weight='balanced'`",
    '  handles the mild 17 / 12 imbalance without SMOTE (synthetic samples',
    '  inside LOOCV inflate AUC misleadingly at n = 29).',
    '- **CV**: leave-one-out. **Primary metric**: AUC. **Secondary**: balanced',
    '  accuracy, accuracy. **CIs**: percentile bootstrap, 2 000 resamples.',
    "- **≤ 6 features per candidate** (n = 29 — more invites unstable LOOCV).",
    '',
    f'## Candidates ({len(CANDIDATES)})',
    '',
]
for name, feats in CANDIDATES.items():
    lines.append(f'### {name}')
    lines.append('')
    lines.append('Features:')
    for f in feats:
        lines.append(f'- `{f}`')
    lines.append('')

lines += [
    '## Results — cleaned dataset (n = ' + str(len(clean)) + ')',
    '',
    '| Candidate | AUC | Balanced acc | Accuracy |',
    '|---|---|---|---|',
]
for name, r in results.items():
    m = r['metrics']
    lines.append(
        f"| {name} | {m['auc']:.3f} [{m['auc_ci'][0]:.3f}, {m['auc_ci'][1]:.3f}] | "
        f"{m['balanced_accuracy']:.3f} [{m['balanced_accuracy_ci'][0]:.3f}, {m['balanced_accuracy_ci'][1]:.3f}] | "
        f"{m['accuracy']:.3f} [{m['accuracy_ci'][0]:.3f}, {m['accuracy_ci'][1]:.3f}] |"
    )
lines.append('')

# Per-candidate detail tables
for name, r in results.items():
    lines.append(f'### {name} — coefficients & univariate AUCs')
    lines.append('')
    lines.append('| Feature | mean coef | SD coef | univariate AUC | aligned AUC |')
    lines.append('|---|---|---|---|---|')
    coef_by_feat = {row['feature']: row for _, row in r['coef'].iterrows()}
    uni_by_feat = {row['feature']: row for _, row in r['univariate'].iterrows()}
    for f in r['features']:
        c = coef_by_feat[f]
        u = uni_by_feat[f]
        a = u['univariate_auc']
        a_str = 'NaN' if np.isnan(a) else f'{a:.3f}'
        lines.append(f"| `{f}` | {c['mean_coef']:+.3f} | {c['sd_coef']:.3f} | {a_str} | {u['aligned']:.3f} |")
    lines.append('')
    lines.append('Confusion matrix (LOOCV):')
    lines.append('')
    lines.append(confusion_md(r['cm']))
    lines.append('')

# Winner summary
lines += [
    '## Winner',
    '',
    f'**{winner_name}** with AUC = {winner["metrics"]["auc"]:.3f} '
    f'[{winner["metrics"]["auc_ci"][0]:.3f}, {winner["metrics"]["auc_ci"][1]:.3f}].',
    '',
    'Ranking (by AUC, ties broken by balanced accuracy):',
    '',
]
for i, (n, r) in enumerate(ranked, 1):
    lines.append(f"{i}. **{n}** — AUC {r['metrics']['auc']:.3f}, balanced acc {r['metrics']['balanced_accuracy']:.3f}")

lines += [
    '',
    '## Backward check — winning feature set on the *un-image-cleaned* dataset',
    '',
    '| Metric | Cleaned | Original (un-cleaned) | Δ (clean − orig) |',
    '|---|---|---|---|',
    f"| AUC | {winner['metrics']['auc']:.3f} [{winner['metrics']['auc_ci'][0]:.3f}, {winner['metrics']['auc_ci'][1]:.3f}] | "
    f"{m_o['auc']:.3f} [{m_o['auc_ci'][0]:.3f}, {m_o['auc_ci'][1]:.3f}] | {winner['metrics']['auc'] - m_o['auc']:+.3f} |",
    f"| Balanced accuracy | {winner['metrics']['balanced_accuracy']:.3f} [{winner['metrics']['balanced_accuracy_ci'][0]:.3f}, {winner['metrics']['balanced_accuracy_ci'][1]:.3f}] | "
    f"{m_o['balanced_accuracy']:.3f} [{m_o['balanced_accuracy_ci'][0]:.3f}, {m_o['balanced_accuracy_ci'][1]:.3f}] | {winner['metrics']['balanced_accuracy'] - m_o['balanced_accuracy']:+.3f} |",
    f"| Accuracy | {winner['metrics']['accuracy']:.3f} [{winner['metrics']['accuracy_ci'][0]:.3f}, {winner['metrics']['accuracy_ci'][1]:.3f}] | "
    f"{m_o['accuracy']:.3f} [{m_o['accuracy_ci'][0]:.3f}, {m_o['accuracy_ci'][1]:.3f}] | {winner['metrics']['accuracy'] - m_o['accuracy']:+.3f} |",
    '',
    f'Paired permutation test on per-fold predicted probabilities for ΔAUC (cleaned − original): '
    f'**ΔAUC = {delta_auc:+.3f}, two-sided p = {p_perm:.4f}**.',
    '',
    '## Honest caveats',
    '',
    f'- **n = {len(clean)}** is very small for a classifier. Bootstrap CIs are wide;',
    '  most span 0.5 (chance) for AUC.',
    '- **A swap of one or two LOOCV predictions** moves AUC by ~0.05. Headline',
    '  ranking differences smaller than that should not drive conclusions.',
    "- **The reference model's AUC = 0.820 was on a different sample** with",
    '  different exclusions (and used `blink_count`, which we deliberately drop).',
    '  We should not expect to match that headline.',
    "- **Backward check direction**: positive Δ (cleaned > original) is the",
    '  predicted direction. If the winner shows negative Δ on this small sample,',
    '  read it as "image cleanup did not move the predictor at this resolution",',
    '  not "image cleanup hurt the predictor." See the paired-perm p-value.',
]

report_path = f'{REPORT_DIR}/11_model_iteration.md'
with open(report_path, 'w') as f:
    f.write('\n'.join(lines) + '\n')
print(f"Saved: {report_path}")
