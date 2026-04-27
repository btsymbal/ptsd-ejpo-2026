# %% [markdown]
# # LMM-Based Image Quality Evaluation
#
# **Goal**: Identify poorly performing images in the stimulus set by combining
# previously computed per-image metrics (CV, effect sizes, distributional
# properties) and flag candidates for removal. An LMM per category provides
# image-level BLUPs (Best Linear Unbiased Predictors) as an **informational
# diagnostic** of per-image engagement.
#
# **Model**: `dwell_pct ~ if_PTSD + (1 | image) + VC(participant)` fitted
# separately for each image category.
#
# The BLUP captures each image's deviation from the category mean after
# controlling for group and participant variability — it is a measure of
# overall engagement, *not* a direct measure of PTSD-specific response.
# We tried fitting a random slope `(1 + if_PTSD | image)` to obtain per-image
# PTSD effects, but statsmodels' MixedLM could not reliably converge such
# models given the competing participant variance component. BLUPs are
# therefore retained as a diagnostic visual (dotplots) but are **not** part
# of the flagging criteria. Flagging uses CV and effect size only, both of
# which directly reflect group-sensitive signals.

# %%
import json
import os
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.regression.mixed_linear_model import MixedLM

os.chdir(Path(__file__).resolve().parent.parent)

FIG_DIR = 'figures/images_analysis/lmm_image_quality'
REPORT_DIR = 'reports/images_analysis'
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Expected sign of effect size per category (positive = PTSD higher dwell time).
# None = no directional expectation.
EXPECTED_SIGN = {
    'angry_face': 'positive',
    'anxiety_inducing': 'positive',
    'combat_vehicles': 'positive',
    'happy_event': 'negative',
    'happy_face': 'negative',
    'neutral': None,
    'neutral_face': 'negative',
    'sad_face': 'positive',
    'sleep_related': 'positive',  # PTSD group expected to dwell longer due to sleep-related symptoms
    'soldiers': 'positive',
    'warfare': 'positive',
}

# Categories excluded from flagging (included in LMM/diagnostics but not flagged).
# 'neutral' is excluded because no consistent attentional bias is expected and
# the category is used as a baseline/filler — flagging would be uninterpretable.
FLAGGING_EXCLUDED = {'neutral'}

# Flagging thresholds
CV_THRESHOLD = 1.0    # CV >= 1.0 (within-group SD exceeds the mean) → noisy measurement

# %% [markdown]
# ## 1. Load Data

# %%
df = pd.read_csv('data/simplified/dataset_image_dwell_times_clean.csv')

with open('materials/id_to_category_mapping.json') as f:
    cat_map = json.load(f)

# Load pre-computed metrics from sibling notebooks
cv_df = pd.read_csv('data/output/cv_dwell_time_per_image.csv')
dist_df = pd.read_csv('data/output/distributional_properties_per_image.csv')
gc_df = pd.read_csv('data/output/group_comparisons_per_image.csv')

categories = sorted(df['category'].unique())
n_sessions = df['session_id'].nunique()
n_images = df['image_id'].nunique()

print(f"Total observations: {len(df)}")
print(f"Sessions:           {n_sessions}")
print(f"Unique images:      {n_images}")
print(f"Categories:         {len(categories)}")

# %% [markdown]
# ## 2. Fit LMM Per Category

# %%
blup_rows = []
model_summaries = {}

for cat in categories:
    cat_df = df[df['category'] == cat].copy()
    n_img = cat_df['image_id'].nunique()
    n_sess = cat_df['session_id'].nunique()

    print(f"\n{'='*70}")
    print(f"Category: {cat} ({n_img} images, {n_sess} participants, {len(cat_df)} obs)")
    print('='*70)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        model = MixedLM.from_formula(
            'dwell_pct ~ if_PTSD',
            data=cat_df,
            re_formula='1',
            groups='image_id',
            vc_formula={'participant': '0 + C(session_id)'}
        )
        result = model.fit(reml=True)
        convergence_warnings = [x for x in w if 'converg' in str(x.message).lower()
                                or 'hessian' in str(x.message).lower()]

    intercept = result.fe_params['Intercept']
    group_coef = result.fe_params['if_PTSD']
    group_pval = result.pvalues['if_PTSD']
    image_var = result.cov_re.iloc[0, 0] if result.cov_re.shape[0] > 0 else 0.0
    participant_var = result.vcomp[0] if len(result.vcomp) > 0 else 0.0
    residual_var = result.scale

    model_summaries[cat] = {
        'n_images': n_img,
        'n_participants': n_sess,
        'n_obs': len(cat_df),
        'intercept': intercept,
        'group_coef': group_coef,
        'group_pval': group_pval,
        'image_var': image_var,
        'participant_var': participant_var,
        'residual_var': residual_var,
        'converged': result.converged,
        'hessian_warning': len(convergence_warnings) > 0,
        'result': result,
    }

    print(f"  Intercept:       {intercept:.4f}")
    print(f"  Group (if_PTSD): {group_coef:.4f} (p = {group_pval:.4f})")
    print(f"  Image variance:       {image_var:.4f}")
    print(f"  Participant variance: {participant_var:.4f}")
    print(f"  Residual variance:    {residual_var:.4f}")
    if convergence_warnings:
        print(f"  WARNING: {convergence_warnings[0].message}")

    # Extract image engagement BLUPs (informational only — not used for flagging)
    for img_id, re in result.random_effects.items():
        blup_rows.append({
            'image_id': img_id,
            'category': cat,
            'BLUP': re.values[0],
        })

blup_df = pd.DataFrame(blup_rows)
print(f"\nBLUP table: {len(blup_df)} images")

# %% [markdown]
# ## 3. LMM Assumption Checks
#
# Key assumptions:
# 1. **Normality of residuals** — Q-Q plot + Shapiro-Wilk test
# 2. **Homoscedasticity** — Residuals vs. fitted values scatter
# 3. **Normality of random effects** — Q-Q plot for image random intercepts
# 4. **Independence** — Satisfied by design (each participant sees each image once)
# 5. **Linearity** — Trivially met with a single binary predictor

# %%
assumption_rows = []

n_cats = len(categories)
fig_diag, axes_diag = plt.subplots(n_cats, 3, figsize=(15, n_cats * 3.2))
if n_cats == 1:
    axes_diag = axes_diag.reshape(1, -1)

for i, cat in enumerate(categories):
    result = model_summaries[cat]['result']
    cat_df_diag = df[df['category'] == cat]

    # Compute proper conditional fitted values: fixed effects + image BLUPs only.
    # statsmodels' result.fittedvalues includes participant VC pseudo-predictions
    # that are poorly estimated, creating spurious residual-fitted correlations.
    image_blups_dict = {img: re.values[0] for img, re in result.random_effects.items()}
    fitted = (result.fe_params['Intercept']
              + result.fe_params['if_PTSD'] * cat_df_diag['if_PTSD'].values
              + cat_df_diag['image_id'].map(image_blups_dict).values)
    resid = cat_df_diag['dwell_pct'].values - fitted

    # Shapiro-Wilk on residuals (use up to 5000 obs)
    resid_sample = resid if len(resid) <= 5000 else np.random.default_rng(42).choice(resid, 5000, replace=False)
    sw_stat, sw_p = stats.shapiro(resid_sample)

    # Image BLUPs for this category
    cat_blups = blup_df[blup_df['category'] == cat]['BLUP'].values

    assumption_rows.append({
        'Category': cat,
        'n_obs': len(resid),
        'Shapiro_W': sw_stat,
        'Shapiro_p': sw_p,
        'Resid_skewness': stats.skew(resid, bias=False),
        'Resid_kurtosis': stats.kurtosis(resid, bias=False),
        'n_blups': len(cat_blups),
    })

    # (a) Residual Q-Q plot
    ax_qq = axes_diag[i, 0]
    stats.probplot(resid, dist='norm', plot=ax_qq)
    ax_qq.set_title(f'{cat}\nResidual Q-Q', fontsize=8)
    ax_qq.tick_params(labelsize=6)

    # (b) Residuals vs fitted
    ax_rf = axes_diag[i, 1]
    ax_rf.scatter(fitted, resid, alpha=0.3, s=8, color='steelblue')
    ax_rf.axhline(0, color='grey', linestyle='--', linewidth=0.8)
    ax_rf.set_xlabel('Fitted', fontsize=7)
    ax_rf.set_ylabel('Residual', fontsize=7)
    ax_rf.set_title(f'{cat}\nResid vs Fitted', fontsize=8)
    ax_rf.tick_params(labelsize=6)

    # (c) Image BLUP Q-Q
    ax_bq = axes_diag[i, 2]
    if len(cat_blups) >= 3:
        stats.probplot(cat_blups, dist='norm', plot=ax_bq)
    else:
        ax_bq.text(0.5, 0.5, f'n={len(cat_blups)}\n(too few)', ha='center', va='center',
                   transform=ax_bq.transAxes, fontsize=8)
    ax_bq.set_title(f'{cat}\nImage BLUP Q-Q', fontsize=8)
    ax_bq.tick_params(labelsize=6)

fig_diag.tight_layout()
fname = f'{FIG_DIR}/assumption_diagnostics.png'
fig_diag.savefig(fname, dpi=600, bbox_inches='tight')
plt.close(fig_diag)
print(f"Saved: {fname}")

# %%
assumption_df = pd.DataFrame(assumption_rows)
print("\n=== Assumption Check Summary ===\n")
print(assumption_df.to_string(index=False, float_format='%.4f'))

n_normal = (assumption_df['Shapiro_p'] > 0.05).sum()
print(f"\nResidual normality (Shapiro-Wilk p > 0.05): {n_normal}/{n_cats}")
if n_normal < n_cats:
    print("NOTE: LMMs are generally robust to moderate departures from normality,")
    print("especially with the sample sizes in this study. Interpret with caution")
    print("for categories with strongly non-normal residuals.")

# %% [markdown]
# ## 4. Merge Summary Table

# %%
# CV from PTSD group
cv_ptsd = cv_df[cv_df['Group'] == 'PTSD'][['image_id', 'CV']].copy()
cv_ptsd.columns = ['image_id', 'CV_PTSD']

# Effect sizes and p-values from group comparisons
gc_cols = gc_df[['Image_ID', 'Category', 'Effect_Size_Type', 'Effect_Size',
                  'p_uncorrected', 'p_BH', 'CI_lo', 'CI_hi']].copy()
gc_cols.columns = ['image_id', 'category', 'ES_Type', 'Effect_Size',
                    'p_uncorrected', 'p_BH', 'CI_lo', 'CI_hi']

# Distributional properties
dist_cols = dist_df[['image_id', 'skewness', 'kurtosis']].copy()

# Merge all
summary = blup_df.merge(cv_ptsd, on='image_id', how='left')
summary = summary.merge(gc_cols, on=['image_id', 'category'], how='left')
summary = summary.merge(dist_cols, on='image_id', how='left')

print(f"Summary table: {len(summary)} rows, {summary.shape[1]} columns")
print(summary.columns.tolist())
print()

for cat in categories:
    cat_data = summary[summary['category'] == cat].sort_values('BLUP', ascending=False)
    print(f"\n--- {cat} ({len(cat_data)} images) ---")
    display_cols = ['image_id', 'BLUP', 'CV_PTSD', 'ES_Type', 'Effect_Size', 'p_uncorrected', 'skewness']
    print(cat_data[display_cols].to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## 5. Visualizations

# %%
# Plot 1: BLUP Dotplot (per category) — informational only, not used for flagging.
# BLUP = image random intercept from intercept-only LMM, reflecting overall engagement
# (deviation from category mean after controlling for group and participant effects).
for cat in categories:
    cat_data = summary[summary['category'] == cat].sort_values('BLUP').reset_index(drop=True)
    n_img = len(cat_data)
    fig_height = max(3, n_img * 0.32)

    fig, ax = plt.subplots(figsize=(8, fig_height))
    y_pos = np.arange(n_img)

    ax.scatter(cat_data['BLUP'], y_pos, color='steelblue', s=40, zorder=3)
    ax.axvline(0, color='grey', linestyle='--', linewidth=0.8)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(cat_data['image_id'].values, fontsize=7)
    ax.set_xlabel('BLUP (image random intercept — engagement diagnostic)')
    ax.set_title(f'Image BLUPs — {cat} [diagnostic only]')
    ax.grid(axis='x', alpha=0.3)

    fname = f'{FIG_DIR}/blup_dotplot_{cat}.png'
    fig.savefig(fname, dpi=600, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved: {fname}')

# %%
# Plot 2: BLUP vs CV scatter (per category) — informational only.
for cat in categories:
    cat_data = summary[summary['category'] == cat]
    n_img = len(cat_data)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(cat_data['BLUP'], cat_data['CV_PTSD'], color='steelblue', s=40, zorder=3)

    for _, row in cat_data.iterrows():
        ax.annotate(row['image_id'], (row['BLUP'], row['CV_PTSD']),
                     fontsize=5, alpha=0.7, xytext=(3, 3), textcoords='offset points')

    ax.axvline(0, color='grey', linestyle='--', linewidth=0.8)
    ax.set_xlabel('BLUP (image random intercept — engagement diagnostic)')
    ax.set_ylabel('CV (PTSD group)')
    ax.set_title(f'BLUP vs CV — {cat} [diagnostic only]')
    ax.grid(alpha=0.3)

    fname = f'{FIG_DIR}/blup_vs_cv_{cat}.png'
    fig.savefig(fname, dpi=600, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved: {fname}')

# %%
# Plot 3: Per-image effect size dotplot (per category)
MARKER_D = 'o'
MARKER_R = 'D'

for cat in categories:
    cat_data = summary[summary['category'] == cat].sort_values('Effect_Size').reset_index(drop=True)
    n_img = len(cat_data)
    fig_height = max(3, n_img * 0.32)

    fig, ax = plt.subplots(figsize=(8, fig_height))
    y_pos = np.arange(n_img)

    for i, (_, r) in enumerate(cat_data.iterrows()):
        marker = MARKER_D if r['ES_Type'] == "Cohen's d" else MARKER_R
        color = '#333333'
        ax.errorbar(r['Effect_Size'], i,
                     xerr=[[r['Effect_Size'] - r['CI_lo']], [r['CI_hi'] - r['Effect_Size']]],
                     fmt=marker, color=color, markersize=5, capsize=3, linewidth=1.0)

    ax.axvline(0, color='grey', linestyle='--', linewidth=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(cat_data['image_id'].values, fontsize=7)
    ax.set_xlabel('Effect Size (with 95% CI)\n← No-PTSD higher    |    PTSD higher →')
    ax.set_title(f'Per-Image Effect Sizes — {cat}')

    expected = EXPECTED_SIGN.get(cat)
    if expected == 'positive':
        ax.axvspan(ax.get_xlim()[0], 0, alpha=0.05, color='red')
    elif expected == 'negative':
        ax.axvspan(0, ax.get_xlim()[1], alpha=0.05, color='red')

    handles = [
        plt.Line2D([0], [0], marker=MARKER_D, color='grey', linestyle='None',
                   markersize=6, label="Cohen's d"),
        plt.Line2D([0], [0], marker=MARKER_R, color='grey', linestyle='None',
                   markersize=6, label='rank-biserial r'),
    ]
    ax.legend(handles=handles, loc='lower right', fontsize=7)

    fname = f'{FIG_DIR}/effect_size_dotplot_{cat}.png'
    fig.savefig(fname, dpi=600, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved: {fname}')

# %% [markdown]
# ## 6. Flag Poorly Performing Images
#
# An image is flagged if it meets **either** of these criteria:
#
# 1. **CV criterion** (within-PTSD-group CV >= 1.0) — within-group SD exceeds
#    the mean, indicating a substantively noisy measurement
# 2. **Effect size criterion** (unexpected direction) — image drives the
#    group difference opposite to the theoretical prediction
#
# Each criterion independently identifies a real failure mode: an image failing
# CV is an unreliable measurement regardless of its effect size; an image failing
# the effect-size check fails its theoretical purpose regardless of its noise
# level. Conjunction (AND) would require both failures to co-occur, which is
# stricter than either problem alone warrants.
#
# The BLUP from the LMM is retained as an informational diagnostic (see dotplots
# in §5) but is not used for flagging. Previous attempts to incorporate BLUPs
# as a direction-aware flagging criterion are documented in the project history;
# the intercept-BLUP captures overall engagement rather than PTSD-specific
# response, and random-slope extensions did not converge reliably in statsmodels.

# %%
flag_rows = []

for cat in categories:
    cat_data = summary[summary['category'] == cat].copy()
    n_img = len(cat_data)
    expected = EXPECTED_SIGN.get(cat)

    if cat in FLAGGING_EXCLUDED:
        cat_data['flag_cv'] = False
        cat_data['flag_es'] = False
        cat_data['n_flags'] = 0
        cat_data['flagged'] = False
        flag_rows.append(cat_data)
        continue

    # --- Criterion 1: CV >= fixed threshold (within PTSD group) ---
    # CV is scale-free (SD/mean); CV >= 1.0 means within-group SD exceeds the
    # mean — a substantively noisy measurement regardless of category.
    cat_data['flag_cv'] = cat_data['CV_PTSD'] >= CV_THRESHOLD

    # --- Criterion 2: Effect size in unexpected direction ---
    # For categories with a theoretical direction, flag images whose effect
    # size has the wrong sign. For no-expectation categories (if any remain
    # after 'neutral' is excluded from flagging), no ES-based flag is applied.
    def check_es(row):
        es = row['Effect_Size']
        if expected == 'positive':
            return es < 0
        elif expected == 'negative':
            return es > 0
        else:
            return False
    cat_data['flag_es'] = cat_data.apply(check_es, axis=1)

    # --- Count flags (either criterion sufficient) ---
    cat_data['n_flags'] = (cat_data['flag_cv'].astype(int)
                           + cat_data['flag_es'].astype(int))
    cat_data['flagged'] = cat_data['n_flags'] >= 1

    flag_rows.append(cat_data)

flagged_df = pd.concat(flag_rows, ignore_index=True)

# %% [markdown]
# ## 7. Summary & Recommendation

# %%
n_flagged = flagged_df['flagged'].sum()
n_total = len(flagged_df)

print("=" * 90)
print("IMAGE QUALITY EVALUATION — SUMMARY")
print("=" * 90)
print(f"\nTotal images evaluated: {n_total}")
print(f"Images flagged (either criterion): {n_flagged}")

print(f"\n--- Flags per category ---\n")
cat_flag_counts = flagged_df.groupby('category').agg(
    n_images=('image_id', 'count'),
    n_flagged=('flagged', 'sum'),
    n_flag_cv=('flag_cv', 'sum'),
    n_flag_es=('flag_es', 'sum'),
).astype(int)
print(cat_flag_counts.to_string())

if n_flagged > 0:
    print(f"\n--- Flagged images (either criterion) ---\n")
    flagged_images = flagged_df[flagged_df['flagged']].sort_values(
        ['n_flags', 'CV_PTSD'], ascending=[False, False]
    )
    for _, r in flagged_images.iterrows():
        expected = EXPECTED_SIGN.get(r['category'], 'none')
        print(f"  {r['image_id']} ({r['category']}):")
        print(f"    CV_PTSD = {r['CV_PTSD']:.4f}, "
              f"ES ({r['ES_Type']}) = {r['Effect_Size']:.4f}, "
              f"BLUP = {r['BLUP']:.4f}")
        print(f"    Expected direction: {expected}")
        print()

# Recommendation
print("=" * 90)
print("RECOMMENDATION")
print("=" * 90)
pct_flagged = n_flagged / n_total * 100 if n_total > 0 else 0
print(f"\n{n_flagged}/{n_total} images ({pct_flagged:.1f}%) flagged across all categories.")

if n_flagged == 0:
    print("\nNo images meet either flagging criterion. The stimulus set appears")
    print("to be performing adequately. No trimming is recommended at this time.")
elif pct_flagged <= 10:
    print(f"\nA small proportion of images are flagged. Removing these {n_flagged} image(s)")
    print("could modestly improve measurement quality, but the impact would be limited.")
    print("Consider removal if the categories can tolerate fewer stimuli.")
elif pct_flagged <= 20:
    print(f"\nA moderate proportion of images are flagged. Trimming these {n_flagged} images")
    print("is recommended if the categories have enough remaining stimuli for reliable")
    print("measurement. Review category-level counts above to assess impact.")
else:
    print(f"\nA substantial proportion of images ({pct_flagged:.1f}%) are flagged. This may")
    print("indicate broader issues with the paradigm design or population variability")
    print("rather than individual image quality. Trimming alone may not suffice.")

print("=" * 90)

# %% [markdown]
# ## 8. Write Report

# %%
report_lines = [
    '# LMM-Based Image Quality Evaluation',
    '',
    '## Methodology',
    '',
    'This analysis integrates multiple per-image metrics to identify poorly performing',
    'images in the stimulus set. The approach combines:',
    '',
    '1. **Coefficient of Variation (CV)**: within-group variability of dwell time percentage',
    '   per image, computed separately for PTSD and No-PTSD groups. High CV indicates',
    '   inconsistent attentional responses across participants.',
    '2. **Distributional properties**: skewness and kurtosis of dwell time distributions',
    '   across all participants, identifying images with atypical response patterns.',
    '3. **Group comparisons**: per-image effect sizes (Cohen\'s d for parametric tests,',
    '   rank-biserial r for non-parametric tests) comparing PTSD vs No-PTSD dwell time,',
    '   with Benjamini-Hochberg FDR correction.',
    '4. **Linear Mixed Models (LMM)**: fitted as an informational diagnostic only.',
    '   Model: `dwell_pct ~ if_PTSD + (1 | image) + VC(participant)` per category',
    '   using REML estimation. Image-level BLUPs (Best Linear Unbiased Predictors)',
    '   capture each image\'s deviation from the category mean after controlling',
    '   for group and participant variability — i.e. overall engagement, not a',
    '   PTSD-specific response. BLUPs are reported in dotplots for interpretive',
    '   context but are **not** used for flagging (see discussion below).',
    '',
    'Images are flagged if they meet **either** of two direction-aware criteria',
    '(applied to all categories except `neutral`, which is excluded from flagging',
    'as a baseline/filler category with no interpretable attentional bias expectation).',
    'Each criterion independently indicates a real failure mode — unreliability or',
    'failure of the theoretical prediction — so either alone is sufficient to flag.',
    '',
    '- **CV criterion**: within-PTSD-group CV >= 1.0 (within-group SD exceeds',
    '  the mean — a scale-free indicator of substantively noisy measurement).',
    '- **Effect size criterion**: Cohen\'s d / rank-biserial r from the raw',
    '  group comparison has the unexpected sign (opposite to the category\'s',
    '  theoretical direction). Magnitude is not thresholded — any wrong-direction',
    '  effect counts, since it indicates the image drives the group difference',
    '  opposite to its intended purpose.',
    '',
    '**Note on BLUPs and flagging**: Earlier iterations used a direction-aware',
    'BLUP criterion (bottom/top 20% within category, per `EXPECTED_SIGN`). On',
    'reflection this conflated the image\'s overall engagement level with its',
    'PTSD-specific response — the intercept BLUP measures only the former. A',
    'random-slope extension `(1 + if_PTSD | image)` would give per-image PTSD',
    'effects directly, but statsmodels\' MixedLM could not reliably converge such',
    'models here given the competing participant variance component. The effect',
    'size criterion (Cohen\'s d / rank-biserial r) is already a direct, model-free',
    'test of the theoretical direction prediction, so dropping the BLUP criterion',
    'does not lose group-sensitive signal.',
    '',
    '### Expected Directions',
    '',
    '| Category | Expected sign | Rationale |',
    '|----------|---------------|-----------|',
]
EXPECTED_RATIONALE = {
    'angry_face': 'hypervigilance to threat',
    'anxiety_inducing': 'hypervigilance to potential (hidden) threat',
    'combat_vehicles': 'emotionally driven memories',
    'happy_event': 'anhedonistic subtype',
    'happy_face': 'anhedonistic subtype',
    'neutral': 'no consistent pattern (paired with diverse images)',
    'neutral_face': 'hypervigilance to threat (opposite image)',
    'sad_face': 'anhedonistic subtype (opposite image)',
    'sleep_related': 'PTSD group expected to dwell longer due to sleep-related symptoms',
    'soldiers': 'hypervigilance to threat',
    'warfare': 'hypervigilance to threat',
}
for cat in sorted(EXPECTED_SIGN.keys()):
    sign = EXPECTED_SIGN[cat] if EXPECTED_SIGN[cat] else '—'
    report_lines.append(f'| {cat} | {sign} | {EXPECTED_RATIONALE[cat]} |')

report_lines += [
    '',
    '## LMM Results Per Category (diagnostic)',
    '',
    '| Category | n_images | n_participants | Intercept | Group coef | Group p | Image var | Participant var | Residual var | Converged | Hessian warning |',
    '|----------|----------|----------------|-----------|------------|---------|-----------|-----------------|--------------|-----------|-----------------|',
]
for cat in categories:
    s = model_summaries[cat]
    report_lines.append(
        f"| {cat} | {s['n_images']} | {s['n_participants']} | {s['intercept']:.4f} | "
        f"{s['group_coef']:.4f} | {s['group_pval']:.4f} | {s['image_var']:.4f} | "
        f"{s['participant_var']:.4f} | {s['residual_var']:.4f} | "
        f"{'Yes' if s['converged'] else 'No'} | "
        f"{'Yes' if s['hessian_warning'] else 'No'} |"
    )

report_lines += [
    '',
    '## Assumption Checks',
    '',
    'LMM assumptions were assessed for each category.',
    '',
    '**Note on residual computation**: Residuals and fitted values for diagnostics are',
    'computed as fixed effects + image BLUPs only, excluding participant variance-component',
    'predictions. This is necessary because statsmodels\' `fittedvalues` includes participant',
    'VC pseudo-predictions that are poorly estimated (the VC approach does not produce true',
    'conditional modes for the second random effect), creating spurious residual-fitted',
    'correlations. The image BLUPs — the primary output of interest — are properly estimated',
    'via the `groups` factor.',
    '',
    '- **Normality of residuals**: Shapiro-Wilk test + Q-Q plots',
    '- **Homoscedasticity**: Residuals vs. fitted values scatter plots',
    '- **Normality of random effects**: Q-Q plots for image BLUPs',
    '- **Independence**: Satisfied by design (each participant sees each image once)',
    '- **Linearity**: Trivially met with a single binary predictor',
    '',
    '| Category | n_obs | Shapiro W | Shapiro p | Resid skewness | Resid kurtosis | n_BLUPs |',
    '|----------|-------|-----------|-----------|----------------|----------------|---------|',
]
for _, r in assumption_df.iterrows():
    report_lines.append(
        f"| {r['Category']} | {int(r['n_obs'])} | {r['Shapiro_W']:.4f} | {r['Shapiro_p']:.4f} | "
        f"{r['Resid_skewness']:.4f} | {r['Resid_kurtosis']:.4f} | {int(r['n_blups'])} |"
    )

n_normal = (assumption_df['Shapiro_p'] > 0.05).sum()
n_hessian = sum(1 for s in model_summaries.values() if s['hessian_warning'])
hessian_cats = [cat for cat, s in model_summaries.items() if s['hessian_warning']]

report_lines += [
    '',
    f'Residual normality satisfied (p > 0.05): {n_normal}/{n_cats} categories.',
    '',
    'LMMs are generally robust to moderate departures from normality, especially with',
    'repeated measures and the sample sizes in this study. Categories with strongly',
    'non-normal residuals should be interpreted with caution.',
    '',
]

if n_hessian > 0:
    report_lines += [
        f'### Convergence Warnings',
        '',
        f'{n_hessian}/{n_cats} categories produced Hessian/convergence warnings:',
        f'{", ".join(hessian_cats)}.',
        '',
        'These warnings typically arise in categories with few images (7-13), where the',
        'image variance component is estimated at a boundary or the optimization landscape',
        'is flat. The models still converge to parameter estimates, but BLUPs from these',
        'categories should be interpreted with extra caution. Flagging decisions for these',
        'categories are less reliable than for categories without warnings.',
        '',
    ]

report_lines.append(f'Diagnostic plots: `{FIG_DIR}/assumption_diagnostics.png`')

# Full summary table for flagged images
report_lines += [
    '',
    '## Flagged Images',
    '',
    f'**Total flagged (either criterion)**: {n_flagged}/{n_total}',
    '',
]
if n_flagged > 0:
    report_lines += [
        '| Image ID | Category | BLUP | CV (PTSD) | ES Type | Effect Size | p (uncorr) | Skewness |',
        '|----------|----------|------|-----------|---------|-------------|------------|----------|',
    ]
    flagged_images = flagged_df[flagged_df['flagged']].sort_values(
        ['CV_PTSD'], ascending=[False]
    )
    for _, r in flagged_images.iterrows():
        report_lines.append(
            f"| {r['image_id']} | {r['category']} | {r['BLUP']:.4f} | {r['CV_PTSD']:.4f} | "
            f"{r['ES_Type']} | {r['Effect_Size']:.4f} | {r['p_uncorrected']:.4f} | "
            f"{r['skewness']:.4f} |"
        )
    report_lines.append('')
else:
    report_lines.append('No images met both flagging criteria.')
    report_lines.append('')

# Category-level summary
report_lines += [
    '### Flags Per Category',
    '',
    '| Category | n_images | Flagged | CV flags | ES flags |',
    '|----------|----------|---------|----------|----------|',
]
for cat in categories:
    row = cat_flag_counts.loc[cat]
    report_lines.append(
        f"| {cat} | {row['n_images']} | {row['n_flagged']} | "
        f"{row['n_flag_cv']} | {row['n_flag_es']} |"
    )

report_lines += [
    '',
    '## Summary & Recommendation',
    '',
    f'{n_flagged}/{n_total} images ({pct_flagged:.1f}%) flagged across all categories.',
    '',
]
if n_flagged == 0:
    report_lines += [
        'No images meet either flagging criterion. The stimulus set appears',
        'to be performing adequately. No trimming is recommended at this time.',
    ]
elif pct_flagged <= 10:
    report_lines += [
        f'A small proportion of images are flagged. Removing these {n_flagged} image(s)',
        'could modestly improve measurement quality, but the impact would be limited.',
        'Consider removal if the categories can tolerate fewer stimuli.',
    ]
elif pct_flagged <= 20:
    report_lines += [
        f'A moderate proportion of images are flagged. Trimming these {n_flagged} images',
        'is recommended if the categories have enough remaining stimuli for reliable',
        'measurement. Review category-level counts to assess impact.',
    ]
else:
    report_lines += [
        f'A substantial proportion of images ({pct_flagged:.1f}%) are flagged. This may',
        'indicate broader issues with the paradigm design or population variability',
        'rather than individual image quality. Trimming alone may not suffice.',
    ]

report_lines += [
    '',
    '## Figures',
    '',
    f'- Assumption diagnostics: `{FIG_DIR}/assumption_diagnostics.png`',
]
for cat in categories:
    report_lines.append(f'- BLUP dotplot (diagnostic, {cat}): `{FIG_DIR}/blup_dotplot_{cat}.png`')
    report_lines.append(f'- BLUP vs CV (diagnostic, {cat}): `{FIG_DIR}/blup_vs_cv_{cat}.png`')
    report_lines.append(f'- Effect size dotplot ({cat}): `{FIG_DIR}/effect_size_dotplot_{cat}.png`')
report_lines.append('')

report_path = os.path.join(REPORT_DIR, 'lmm_image_quality_evaluation_report.md')
with open(report_path, 'w') as f:
    f.write('\n'.join(report_lines) + '\n')
print(f"Report written to {report_path}")
