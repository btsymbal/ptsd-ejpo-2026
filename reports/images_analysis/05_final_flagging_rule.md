# Step 5 — Final Flagging Rule and Image Lists

## Combined rule

```
flagged = C1  OR  C2  OR  (C3 AND C4)
```

| Tag | Criterion | Threshold | Strength |
|---|---|---|---|
| C1 | within-PTSD-group CV | `CV_PTSD ≥ 1.0` | strong |
| C2 | wrong-direction effect size, p-confidence-gated | wrong sign **and** `p_uncorrected ≤ 0.5` | strong |
| C3 | pooled skewness | `\|skewness\| > 1.0` | weak |
| C4 | bottom-quintile BLUP | `BLUP ≤ q20` within category | weak |

Either strong criterion fires alone. The two weak criteria must co-occur to
trigger a flag — neither is reliable enough on its own.

## Categories excluded from ALL flagging

`neutral`, `neutral_face`, and `sad_face` have **no directional expectation**
(after Step 1's table revision). They are excluded from every criterion, not
just C2. The reasoning:

- These categories have no theoretical role beyond serving as comparators or
  fillers. Without a directional hypothesis, statistics like CV / skewness /
  BLUP lose the interpretation that anchors them in the threat / engagement
  categories. High within-PTSD CV on an angry_face image plausibly means
  "the image fails to reliably trigger hypervigilance"; high CV on a neutral
  filler more plausibly reflects partner-context heterogeneity (the same
  neutral image can be paired with diverse partners across slides) and is
  not a property of the image itself.
- Trimming neutrals would also break threat-vs-neutral slide-pairs used by
  the `std_delta_dwell_pct` metrics in H3 / H4, weakening rather than
  cleaning the signal.
- The previous version of this report flagged 16 neutrals + 4 neutral_face
  + 2 sad_face on noise grounds; on review those flags were not theoretically
  defensible, so they were removed.

C2 was already auto-skipped for these categories (no expected sign).
C1, C3, and C4 are now also explicitly skipped.

## Counts

- **Total images**: 150
- **Flagged**: **22** (14.7 %)
- **Kept**: **128** (85.3 %)

| Category | n_images | Flagged | Kept | C1 (CV) | C2 (ES) | C3 (skew) | C4 (BLUP) |
|---|---|---|---|---|---|---|---|
| angry_face | 10 | 2 | 8 | 1 | 1 | 2 | 2 |
| anxiety_inducing | 14 | 3 | 11 | 3 | 1 | 3 | 3 |
| combat_vehicles | 8 | 4 | 4 | 3 | 1 | 3 | 2 |
| happy_event | 9 | 2 | 7 | 2 | 0 | 0 | 2 |
| happy_face | 11 | 4 | 7 | 2 | 2 | 2 | 3 |
| **neutral** | **50** | **0** | **50** | excluded | excluded | excluded | excluded |
| **neutral_face** | **13** | **0** | **13** | excluded | excluded | excluded | excluded |
| **sad_face** | **8** | **0** | **8** | excluded | excluded | excluded | excluded |
| sleep_related | 7 | 2 | 5 | 1 | 1 | 1 | 2 |
| soldiers | 8 | 1 | 7 | 1 | 1 | 0 | 2 |
| warfare | 12 | 4 | 8 | 3 | 1 | 1 | 3 |

Per-criterion flag totals (within directional categories; an image can fire more than one):

- C1 (CV ≥ 1.0): 16 images
- C2 (wrong-direction ES with p ≤ 0.5): 8 images
- C3 (|skew| > 1.0): 12 images
- C4 (bottom-quintile BLUP): 19 images
- C3 ∧ C4 conjunction: 5 images (**0 unique** to the weak rule — all 5 are also caught by C1 or C2)

The weak-AND rule produces no unique flags in this dataset; it functions as a
robustness check on the strong criteria.

## Risk: categories trimmed below half their stimuli

| Category | Kept / Original | % retained |
|---|---|---|
| **combat_vehicles** | **4 / 8** | **50 %** |
| happy_face | 7 / 11 | 64 % |
| warfare | 8 / 12 | 67 % |
| sleep_related | 5 / 7 | 71 % |
| happy_event | 7 / 9 | 78 % |
| anxiety_inducing | 11 / 14 | 79 % |
| angry_face | 8 / 10 | 80 % |
| soldiers | 7 / 8 | 88 % |
| neutral / neutral_face / sad_face | 50/50, 13/13, 8/8 | 100 % |

`combat_vehicles` is the most aggressively trimmed (4/8 kept). It is not part
of the four pre-registered threat categories used in H1–H6 (which are
angry_face, anxiety_inducing, warfare, soldiers, all retained at 67–88 %).

## Flagged images (22) — full list

Sorted by category. `Fired` shows which criteria triggered the flag.

| image_id | category | Fired | CV_PTSD | ES | p_unc | skew | BLUP |
|---|---|---|---|---|---|---|---|
| Byi3ZPboRuWBVDB9i8iTHA | angry_face | C2 | 0.897 | -0.425 | 0.269 | 0.887 | -0.887 |
| axcFiBXmT_69RLbTxgEX_g | angry_face | C1, C3∧C4 | 1.123 | -0.137 | 0.547 | 1.002 | -1.973 |
| CCkWAVY9SZyZENRWRaCbQQ | anxiety_inducing | C1 | 1.057 | 0.181 | 0.425 | 1.368 | -0.998 |
| E0GzwqkNRt2EbWvJjA60Hw | anxiety_inducing | C1, C3∧C4 | 1.021 | 0.029 | 0.912 | 1.324 | -1.541 |
| fefWMtd9R8KSv7H2BTpIrw | anxiety_inducing | C1, C2 | 1.164 | -0.225 | 0.318 | 0.911 | -2.251 |
| D50IOgoBSkCOAosH87negA | combat_vehicles | C1 | 1.116 | -0.039 | 0.877 | 1.139 | 0.645 |
| F-zQ4ls4SyqcPxvljy9n0Q | combat_vehicles | C2 | 0.611 | -0.312 | 0.416 | 0.514 | 1.701 |
| VBsOU00iTcmFmqu6o4q07A | combat_vehicles | C1, C3∧C4 | 1.088 | 0.025 | 0.928 | 1.944 | -9.176 |
| cdYWSf1LR1mOH4iXiIMfNQ | combat_vehicles | C1 | 1.003 | 0.167 | 0.464 | 1.187 | 1.001 |
| Dtg8yTd7QBCVthQf7oIqdg | happy_event | C1 | 1.012 | -0.309 | 0.168 | 0.571 | 0.011 |
| XtWPclE2Rs6IrWpB1mbQ_g | happy_event | C1 | 1.041 | -0.098 | 0.673 | 0.872 | -2.814 |
| 68123428 | happy_face | C2 | 0.640 | 0.262 | 0.492 | 0.321 | 1.177 |
| 68123473 | happy_face | C1, C3∧C4 | 1.008 | -0.029 | 0.912 | 1.371 | -1.881 |
| 68123521 | happy_face | C1 | 1.057 | 0.088 | 0.706 | 0.995 | 1.261 |
| LT6YQ4czS9Wle5QjrZ76dQ | happy_face | C2 | 0.622 | 0.157 | 0.491 | 0.542 | -0.793 |
| MamyfpQXRqCkhsxuPo2UxQ | sleep_related | C1, C3∧C4 | 1.205 | -0.152 | 0.504 | 1.364 | -1.948 |
| YaLqQjVwQz6vQerO40WDBg | sleep_related | C2 | 0.950 | -0.206 | 0.362 | 0.745 | -3.964 |
| WMKKOlK4QrGOs3Cn2b_lZg | soldiers | C1, C2 | 1.131 | -0.319 | 0.155 | 0.339 | -4.840 |
| CLZddDIORpCOa5MK6Rsc7w | warfare | C1 | 1.102 | -0.137 | 0.549 | 0.889 | -0.658 |
| KzR2IFB3TZOI8LzfUmb0Gw | warfare | C1 | 1.054 | -0.083 | 0.722 | 0.858 | -4.350 |
| Onhyu_ssRze6tmryDPDhcw | warfare | C1 | 1.011 | 0.142 | 0.532 | 0.743 | -2.144 |
| R0NAzO_VSdqYLe6zb_H3-Q | warfare | C2 | 0.893 | -0.327 | 0.393 | 0.454 | 0.157 |

## Kept images (128) — list per category

The full kept list is also persisted in `data/simplified/image_quality_flags.csv`
(filter `flagged == False`).

- **angry_face (8)**: BAOhiP_wSnyRiMS3lZq4zA, M95ngKo-QWWxwOhsfpmvLw, PpPBepq2REWzonwOmYkBUw, R1NzwXDRShWWp4HpNh1-2A, Xb2P-bDyT_W3tSYII2opow, ZUgMPgL5SoyAINkAswtDwA, bJnTKAzEQ3-NyTGOsrddQQ, dTqTjHGMRueb2c9_TY4bSw
- **anxiety_inducing (11)**: Avz7posjRDC31ra0FeWfRQ, Kno61J2KRhSSUm45uLTRng, M1gYVgk3Qf2m1xK8NsXYmw, MAVnJw1TTRyvln50SeMNpw, O_0Teij0SoWKQvRhaFqWXA, Up86Zd5UTZ2xTykWepL8cQ, UpJ_d0LSQYuIKfuHLEy0PQ, WgzeDfeySaSXhM2QZpmFQw, YfybFlozTz67WOldee9tpA, cnjRsAWeQ0e99kkLp7ih4A, dZ2NqhW_RJm9CGPdC4piMg
- **combat_vehicles (4)**: Ai0jboQ1QzWS3gAVnAedEA, OAsePi_KS8i54UAUhpwrFw, T4n7VCwpSiW0Oii6aVdzaw, cpneNStTRAyJlnfbtOB0Zg
- **happy_event (7)**: AV47lONxTSegnnp_qwxxYw, CHjJZrBdQD28QvgZtchlzw, EowvXzukT6u5Ppa_WElX6Q, FogYThQ8Sn-ECl0o8aOcVg, J5_ezvirSneOQTadVzF48Q, WGmH4OZ5TuOGZwwWr3684A, dhTttH-yT_6WdPoz5dAEvg
- **happy_face (7)**: 68123392, 68123404, 68123436, 68123459, 68123496, EJxzD89zQIWuvnHndKmNrQ, VB475CAWQ6yW-xyzrTOGtg
- **neutral (50)** — all retained
- **neutral_face (13)** — all retained
- **sad_face (8)** — all retained
- **sleep_related (5)**: DJw0-xR_TCaB-_LfnL6lig, QGxFijjYTfWrvg-X02lKcw, XfzYJsixTLCkgWabGvqmlw, b1Q664ESSTG5H25GTXaraQ, dIsJdajoT4msRkkJ_zfW3w
- **soldiers (7)**: A_-1OArYQ_adCPIKemPHdg, A_4H9MYOSCi9sWd3eD8UHA, C2BYNvtJTjOgDpgLvVllVQ, DnxOjrfTQhy9XTxVLuLkQA, FJdnEtD7Sk2EI0szZnHvag, JcPDoVJFSBOgXj8ah7sktg, VZYx7WlqSna6IT90T01LsQ
- **warfare (8)**: A0FBsiMtS76m71TF6zckvA, EZke_5L8R-y--ZMKEVT5qw, LUfNX6YAT-KEsiV3SxKq2w, NB3PTjWUR_SdWHVUuhnXBg, OHKQX4gnTWeT_PiEr1dDeg, Xr4MjhfmTraeKHh0zeNi_Q, ajpX0QFhSHSqvoYiV23Iag, ezkn-4dzQuS05frSm-jyGA

## Output

Persisted to `data/simplified/image_quality_flags.csv` with columns:
`image_id, category, CV_PTSD, Effect_Size, ES_Type, p_uncorrected, p_BH,
skewness, BLUP, flag_cv, flag_es, flag_skew, flag_blup, n_flags, flagged`.

Rows for excluded categories have all flag columns set to `False` and are
included for completeness.

This is the canonical input to Step 6 (re-aggregation of per-category metrics).
