# Image Dwell Times Overview Report

## 1. Dataset Overview

The image dwell times dataset contains **4,350 rows** (29 sessions × 150 images) with 10 columns.

- **Sessions**: 29
- **Unique images**: 150
- **Categories**: 11 (angry_face, anxiety_inducing, combat_vehicles, happy_event, happy_face, neutral, neutral_face, sad_face, sleep_related, soldiers, warfare)

Each `image_id` appears once per session, so per-image statistics are computed by aggregating `dwell_pct` across all sessions.

### Images per Category

| Category | # Images |
|---|---|
| neutral | 50 |
| anxiety_inducing | 14 |
| neutral_face | 13 |
| warfare | 12 |
| happy_face | 11 |
| angry_face | 10 |
| happy_event | 9 |
| combat_vehicles | 8 |
| sad_face | 8 |
| soldiers | 8 |
| sleep_related | 7 |

## 2. Per-Image Aggregation

Aggregating `dwell_pct` across 29 sessions yields a **150-row** dataframe (one row per image).

**Distribution of per-image mean dwell %:**

- Mean of means: 23.70%
- Median of means: 23.52%
- SD of means: 5.04%
- Range: [12.17%, 37.90%]

## 3. Overall Distribution of Per-Image Mean Dwell %

![Mean Dwell Distribution](../../figures/image_dwell_times_overview/mean_dwell_distribution.png)

| Statistic | Value |
|---|---|
| N (images) | 150 |
| Mean | 23.70% |
| Median | 23.52% |
| SD | 5.04% |
| Skewness | 0.282 |
| Kurtosis | 0.097 |
| Shapiro-Wilk W | 0.9887 |
| Shapiro-Wilk p | 2.6426e-01 |

The distribution of per-image mean dwell % is **normal** (Shapiro-Wilk p = 2.6426e-01).

## 4. Per-Image Dwell % Ranked Overview

![Ranked Mean Dwell](../../figures/image_dwell_times_overview/ranked_mean_dwell.png)

### Top 10 Images by Mean Dwell %

| Image ID | Category | Mean | Median | SD |
|---|---|---|---|---|
| MAVnJw1TTRyvln50SeMNpw | anxiety_inducing | 37.90 | 39.36 | 26.69 |
| Ai0jboQ1QzWS3gAVnAedEA | combat_vehicles | 37.38 | 34.46 | 27.42 |
| dZ2NqhW_RJm9CGPdC4piMg | anxiety_inducing | 36.96 | 37.43 | 20.22 |
| Xr4MjhfmTraeKHh0zeNi_Q | warfare | 34.24 | 40.11 | 20.64 |
| Kno61J2KRhSSUm45uLTRng | anxiety_inducing | 33.49 | 35.65 | 22.80 |
| O_0Teij0SoWKQvRhaFqWXA | anxiety_inducing | 33.38 | 30.75 | 17.12 |
| YfybFlozTz67WOldee9tpA | anxiety_inducing | 33.18 | 29.37 | 21.13 |
| 68123404 | happy_face | 33.14 | 34.76 | 19.47 |
| WGmH4OZ5TuOGZwwWr3684A | happy_event | 33.14 | 30.01 | 22.74 |
| A_4H9MYOSCi9sWd3eD8UHA | soldiers | 32.30 | 27.41 | 25.05 |

### Bottom 10 Images by Mean Dwell %

| Image ID | Category | Mean | Median | SD |
|---|---|---|---|---|
| E9z6UYe2Qnu-gdsCpob12A | neutral | 15.90 | 10.00 | 15.71 |
| VB475CAWQ6yW-xyzrTOGtg | happy_face | 15.57 | 14.71 | 12.51 |
| JbYJh1i-Q7CKzV1HlsBcmQ | neutral | 15.25 | 13.37 | 11.82 |
| a5wTdTZzRBWI8S5rtGpSnw | neutral | 15.11 | 12.58 | 16.01 |
| X9Z8xCu-TNe9rXbU-8Wkdg | neutral | 14.92 | 13.37 | 12.89 |
| EJxzD89zQIWuvnHndKmNrQ | happy_face | 14.79 | 12.03 | 13.70 |
| dpBTFNYGTIaEfm1C3JlVWw | neutral | 14.59 | 13.33 | 14.90 |
| DsaJ56FjR0Cb14kA_GqTXw | neutral | 13.95 | 7.78 | 14.63 |
| L4xt7K7OTPSrmYAYSUplWQ | neutral | 13.46 | 5.35 | 16.58 |
| bOAV4sD3StiJa9IPuXGfmA | neutral | 12.17 | 10.70 | 12.60 |

## 5. Within-Image Variability

![Within-Image Variability](../../figures/image_dwell_times_overview/within_image_variability.png)

**Per-image SD distribution**: mean = 19.63, median = 19.72, range = [11.82, 30.90]

**Mean–SD correlation**: r = 0.553, p = 2.237e-13

**High variability images** (SD > mean + 2×SD = 26.62): 6

| Image ID | Category | Mean | SD |
|---|---|---|---|
| cdYWSf1LR1mOH4iXiIMfNQ | combat_vehicles | 29.16 | 30.90 |
| D50IOgoBSkCOAosH87negA | combat_vehicles | 28.75 | 29.11 |
| CCkWAVY9SZyZENRWRaCbQQ | anxiety_inducing | 26.23 | 27.50 |
| Ai0jboQ1QzWS3gAVnAedEA | combat_vehicles | 37.38 | 27.42 |
| WgzeDfeySaSXhM2QZpmFQw | anxiety_inducing | 28.00 | 26.84 |
| MAVnJw1TTRyvln50SeMNpw | anxiety_inducing | 37.90 | 26.69 |

**Low variability images** (SD < mean − 2×SD = 12.63): 3

| Image ID | Category | Mean | SD |
|---|---|---|---|
| JbYJh1i-Q7CKzV1HlsBcmQ | neutral | 15.25 | 11.82 |
| VB475CAWQ6yW-xyzrTOGtg | happy_face | 15.57 | 12.51 |
| bOAV4sD3StiJa9IPuXGfmA | neutral | 12.17 | 12.60 |

## 6. Box Plots of Individual Images by Category

Each subplot shows the distribution of `dwell_pct` across all sessions for each image within a category, ordered by mean dwell %.

### angry_face

![angry_face boxplot](../../figures/image_dwell_times_overview/boxplot_angry_face.png)

### anxiety_inducing

![anxiety_inducing boxplot](../../figures/image_dwell_times_overview/boxplot_anxiety_inducing.png)

### combat_vehicles

![combat_vehicles boxplot](../../figures/image_dwell_times_overview/boxplot_combat_vehicles.png)

### happy_event

![happy_event boxplot](../../figures/image_dwell_times_overview/boxplot_happy_event.png)

### happy_face

![happy_face boxplot](../../figures/image_dwell_times_overview/boxplot_happy_face.png)

### neutral

![neutral boxplot](../../figures/image_dwell_times_overview/boxplot_neutral.png)

### neutral_face

![neutral_face boxplot](../../figures/image_dwell_times_overview/boxplot_neutral_face.png)

### sad_face

![sad_face boxplot](../../figures/image_dwell_times_overview/boxplot_sad_face.png)

### sleep_related

![sleep_related boxplot](../../figures/image_dwell_times_overview/boxplot_sleep_related.png)

### soldiers

![soldiers boxplot](../../figures/image_dwell_times_overview/boxplot_soldiers.png)

### warfare

![warfare boxplot](../../figures/image_dwell_times_overview/boxplot_warfare.png)

## 7. Distribution Plots per Category Group

Violin + strip plots overlay individual session observations on each image within a category, helping identify images with systematically different profiles.

### angry_face

![angry_face violin](../../figures/image_dwell_times_overview/violin_angry_face.png)

### anxiety_inducing

![anxiety_inducing violin](../../figures/image_dwell_times_overview/violin_anxiety_inducing.png)

### combat_vehicles

![combat_vehicles violin](../../figures/image_dwell_times_overview/violin_combat_vehicles.png)

### happy_event

![happy_event violin](../../figures/image_dwell_times_overview/violin_happy_event.png)

### happy_face

![happy_face violin](../../figures/image_dwell_times_overview/violin_happy_face.png)

### neutral

![neutral violin](../../figures/image_dwell_times_overview/violin_neutral.png)

### neutral_face

![neutral_face violin](../../figures/image_dwell_times_overview/violin_neutral_face.png)

### sad_face

![sad_face violin](../../figures/image_dwell_times_overview/violin_sad_face.png)

### sleep_related

![sleep_related violin](../../figures/image_dwell_times_overview/violin_sleep_related.png)

### soldiers

![soldiers violin](../../figures/image_dwell_times_overview/violin_soldiers.png)

### warfare

![warfare violin](../../figures/image_dwell_times_overview/violin_warfare.png)

## 8. Summary Statistics Table

Full table of all 150 images sorted by category then mean dwell %.

| Image ID | Category | N | Mean | Median | SD | Min | Max | IQR |
|---|---|---|---|---|---|---|---|---|
| R1NzwXDRShWWp4HpNh1-2A | angry_face | 29 | 31.78 | 32.65 | 20.88 | 0.00 | 89.57 | 28.78 |
| dTqTjHGMRueb2c9_TY4bSw | angry_face | 29 | 29.81 | 31.34 | 19.36 | 0.00 | 78.88 | 28.14 |
| ZUgMPgL5SoyAINkAswtDwA | angry_face | 29 | 27.53 | 26.74 | 20.53 | 0.00 | 82.01 | 23.41 |
| BAOhiP_wSnyRiMS3lZq4zA | angry_face | 29 | 26.77 | 22.06 | 15.13 | 0.69 | 61.39 | 18.72 |
| bJnTKAzEQ3-NyTGOsrddQQ | angry_face | 29 | 24.21 | 21.03 | 20.82 | 0.00 | 78.88 | 28.76 |
| PpPBepq2REWzonwOmYkBUw | angry_face | 29 | 23.34 | 17.38 | 20.76 | 0.00 | 64.17 | 34.70 |
| M95ngKo-QWWxwOhsfpmvLw | angry_face | 29 | 22.66 | 18.72 | 18.90 | 0.00 | 78.88 | 20.73 |
| Byi3ZPboRuWBVDB9i8iTHA | angry_face | 29 | 22.16 | 20.02 | 19.28 | 0.00 | 75.39 | 31.15 |
| axcFiBXmT_69RLbTxgEX_g | angry_face | 29 | 19.29 | 16.04 | 18.81 | 0.00 | 72.64 | 27.53 |
| Xb2P-bDyT_W3tSYII2opow | angry_face | 29 | 17.47 | 14.71 | 15.81 | 0.00 | 56.15 | 20.64 |
| MAVnJw1TTRyvln50SeMNpw | anxiety_inducing | 29 | 37.90 | 39.36 | 26.69 | 0.00 | 93.58 | 40.77 |
| dZ2NqhW_RJm9CGPdC4piMg | anxiety_inducing | 29 | 36.96 | 37.43 | 20.22 | 4.00 | 69.52 | 27.48 |
| Kno61J2KRhSSUm45uLTRng | anxiety_inducing | 29 | 33.49 | 35.65 | 22.80 | 0.00 | 75.76 | 28.97 |
| O_0Teij0SoWKQvRhaFqWXA | anxiety_inducing | 29 | 33.38 | 30.75 | 17.12 | 0.00 | 68.18 | 22.73 |
| YfybFlozTz67WOldee9tpA | anxiety_inducing | 29 | 33.18 | 29.37 | 21.13 | 0.00 | 81.55 | 31.96 |
| cnjRsAWeQ0e99kkLp7ih4A | anxiety_inducing | 29 | 32.24 | 32.08 | 19.65 | 0.00 | 68.18 | 26.74 |
| Up86Zd5UTZ2xTykWepL8cQ | anxiety_inducing | 29 | 28.60 | 24.69 | 20.97 | 0.00 | 74.20 | 34.75 |
| WgzeDfeySaSXhM2QZpmFQw | anxiety_inducing | 29 | 28.00 | 18.05 | 26.84 | 0.00 | 95.59 | 22.02 |
| M1gYVgk3Qf2m1xK8NsXYmw | anxiety_inducing | 29 | 26.66 | 22.73 | 20.55 | 0.00 | 65.51 | 33.96 |
| CCkWAVY9SZyZENRWRaCbQQ | anxiety_inducing | 29 | 26.23 | 16.04 | 27.50 | 0.00 | 100.27 | 30.10 |
| UpJ_d0LSQYuIKfuHLEy0PQ | anxiety_inducing | 29 | 25.14 | 21.39 | 19.96 | 0.00 | 62.83 | 23.28 |
| E0GzwqkNRt2EbWvJjA60Hw | anxiety_inducing | 29 | 24.46 | 17.38 | 23.57 | 0.00 | 86.23 | 26.74 |
| Avz7posjRDC31ra0FeWfRQ | anxiety_inducing | 29 | 24.21 | 15.30 | 24.05 | 0.00 | 67.29 | 48.13 |
| fefWMtd9R8KSv7H2BTpIrw | anxiety_inducing | 29 | 22.15 | 16.67 | 21.72 | 0.00 | 70.03 | 28.66 |
| Ai0jboQ1QzWS3gAVnAedEA | combat_vehicles | 29 | 37.38 | 34.46 | 27.42 | 0.00 | 99.15 | 43.28 |
| F-zQ4ls4SyqcPxvljy9n0Q | combat_vehicles | 29 | 29.95 | 33.42 | 21.00 | 0.00 | 86.90 | 24.51 |
| cdYWSf1LR1mOH4iXiIMfNQ | combat_vehicles | 29 | 29.16 | 15.60 | 30.90 | 0.00 | 100.01 | 35.45 |
| D50IOgoBSkCOAosH87negA | combat_vehicles | 29 | 28.75 | 14.49 | 29.11 | 0.00 | 98.04 | 31.63 |
| OAsePi_KS8i54UAUhpwrFw | combat_vehicles | 29 | 28.18 | 24.51 | 22.21 | 0.00 | 72.25 | 24.48 |
| T4n7VCwpSiW0Oii6aVdzaw | combat_vehicles | 29 | 27.45 | 28.00 | 23.86 | 0.00 | 82.75 | 35.40 |
| cpneNStTRAyJlnfbtOB0Zg | combat_vehicles | 29 | 25.69 | 24.51 | 16.62 | 0.00 | 60.16 | 25.67 |
| VBsOU00iTcmFmqu6o4q07A | combat_vehicles | 29 | 17.62 | 11.14 | 22.11 | 0.00 | 98.04 | 26.74 |
| WGmH4OZ5TuOGZwwWr3684A | happy_event | 29 | 33.14 | 30.01 | 22.74 | 0.00 | 84.22 | 29.46 |
| EowvXzukT6u5Ppa_WElX6Q | happy_event | 29 | 27.93 | 25.40 | 22.76 | 0.00 | 77.54 | 32.65 |
| J5_ezvirSneOQTadVzF48Q | happy_event | 29 | 26.89 | 26.74 | 16.55 | 0.00 | 65.51 | 22.77 |
| FogYThQ8Sn-ECl0o8aOcVg | happy_event | 29 | 26.84 | 26.67 | 15.78 | 0.00 | 60.16 | 19.93 |
| Dtg8yTd7QBCVthQf7oIqdg | happy_event | 29 | 24.47 | 20.05 | 21.59 | 0.00 | 70.19 | 33.46 |
| AV47lONxTSegnnp_qwxxYw | happy_event | 29 | 23.52 | 22.65 | 17.97 | 0.00 | 68.68 | 29.41 |
| dhTttH-yT_6WdPoz5dAEvg | happy_event | 29 | 20.46 | 17.38 | 18.45 | 0.00 | 62.17 | 28.64 |
| XtWPclE2Rs6IrWpB1mbQ_g | happy_event | 29 | 18.47 | 13.37 | 17.80 | 0.00 | 60.16 | 26.65 |
| CHjJZrBdQD28QvgZtchlzw | happy_event | 29 | 18.26 | 14.44 | 17.11 | 0.00 | 54.81 | 31.30 |
| 68123404 | happy_face | 29 | 33.14 | 34.76 | 19.47 | 0.00 | 72.19 | 27.99 |
| 68123521 | happy_face | 29 | 24.64 | 18.03 | 25.67 | 0.00 | 94.92 | 37.43 |
| 68123428 | happy_face | 29 | 24.50 | 24.06 | 17.81 | 0.00 | 66.18 | 27.96 |
| 68123436 | happy_face | 29 | 24.14 | 23.98 | 16.71 | 0.00 | 53.72 | 24.67 |
| 68123392 | happy_face | 29 | 23.81 | 22.73 | 21.42 | 0.00 | 83.96 | 28.01 |
| 68123496 | happy_face | 29 | 23.71 | 26.17 | 17.45 | 0.00 | 61.50 | 20.05 |
| 68123459 | happy_face | 29 | 23.40 | 21.31 | 19.91 | 0.00 | 66.67 | 23.39 |
| LT6YQ4czS9Wle5QjrZ76dQ | happy_face | 29 | 21.32 | 21.39 | 15.09 | 0.00 | 60.16 | 15.31 |
| 68123473 | happy_face | 29 | 19.56 | 10.03 | 18.24 | 0.00 | 77.54 | 21.39 |
| VB475CAWQ6yW-xyzrTOGtg | happy_face | 29 | 15.57 | 14.71 | 12.51 | 0.00 | 49.46 | 20.07 |
| EJxzD89zQIWuvnHndKmNrQ | happy_face | 29 | 14.79 | 12.03 | 13.70 | 0.00 | 48.61 | 18.72 |
| UQFSuTbWQUKQJqGiFd2QvQ | neutral | 29 | 28.46 | 26.71 | 22.47 | 0.00 | 93.58 | 33.32 |
| dLKNshU2RxqvASlOq7f2gQ | neutral | 29 | 27.91 | 21.39 | 19.94 | 0.00 | 78.88 | 28.07 |
| fuyzeCKyRsOAvWCy2OOOOQ | neutral | 29 | 26.91 | 28.02 | 16.88 | 0.00 | 60.65 | 26.01 |
| Frf7iP7GT_aL95nBFaKU-w | neutral | 29 | 26.58 | 18.72 | 23.08 | 0.00 | 80.61 | 40.63 |
| P2q4MEkKRyyNPJx1wYhG6Q | neutral | 29 | 26.16 | 28.66 | 16.25 | 0.00 | 50.80 | 24.76 |
| B1t1m5HfTISYMypanGkFjQ | neutral | 29 | 26.08 | 24.04 | 22.83 | 0.00 | 91.58 | 32.75 |
| EwwINeH0T1uZkgus22BfiA | neutral | 29 | 25.71 | 28.00 | 18.60 | 0.00 | 69.98 | 22.73 |
| W0ZV_Se1S82l7BxH80COsw | neutral | 29 | 24.28 | 24.69 | 16.49 | 0.00 | 67.34 | 17.92 |
| SqKk6SJMRrewSmtiTzbaTw | neutral | 29 | 23.51 | 18.00 | 18.73 | 0.00 | 66.66 | 30.70 |
| bcL3LuMfQZGFnySDSCLWRw | neutral | 29 | 23.29 | 21.34 | 17.53 | 0.00 | 78.21 | 25.40 |
| c_N8wYhAQ6msNyVXOxFo8A | neutral | 29 | 23.29 | 22.00 | 19.55 | 0.00 | 64.68 | 29.41 |
| E8Qvjgd3RjekOgggk3SSxA | neutral | 29 | 23.11 | 23.40 | 19.43 | 0.00 | 70.19 | 31.32 |
| PbsSxViGSl2KIrlJQaR3Ug | neutral | 29 | 22.98 | 23.39 | 14.13 | 0.00 | 52.14 | 19.97 |
| ZAalUXQ8SkK-VE0MJKv99A | neutral | 29 | 22.95 | 17.33 | 20.44 | 0.00 | 68.18 | 24.10 |
| O6DkP1siRIKIStjl14aOvA | neutral | 29 | 22.54 | 23.99 | 15.70 | 0.00 | 54.67 | 20.75 |
| aifqbTNmTuKFmyp-XTSeDw | neutral | 29 | 22.48 | 18.01 | 16.28 | 0.00 | 56.15 | 19.97 |
| JJC0nKjYQUq8CDE4SKfEhg | neutral | 29 | 22.33 | 18.59 | 21.70 | 0.00 | 100.93 | 17.38 |
| RfNUAiLJSY-CnMbNgjCwXg | neutral | 29 | 22.09 | 18.72 | 14.71 | 0.00 | 50.80 | 20.05 |
| IuQ8yteXR6Wh2d12i2XBfg | neutral | 29 | 21.96 | 14.04 | 20.99 | 0.00 | 64.17 | 34.76 |
| QI8UvWgASnSly3rve1F2DQ | neutral | 29 | 21.53 | 16.04 | 18.44 | 0.00 | 52.14 | 32.09 |
| fIRijcvdSnikbYnd4c-_yw | neutral | 29 | 21.53 | 17.81 | 22.10 | 0.00 | 77.99 | 36.62 |
| BXlUQXWNRk2K3XChhayt0A | neutral | 29 | 21.34 | 17.99 | 19.67 | 0.00 | 63.54 | 33.86 |
| FNANZHtvTAy4UHJT9xISnA | neutral | 29 | 21.28 | 20.05 | 13.81 | 0.00 | 50.66 | 16.67 |
| H84F-DisRR6pzyQiHydhQA | neutral | 29 | 21.27 | 13.37 | 20.90 | 0.00 | 59.32 | 33.08 |
| ae8mEXQiQ-OtshFPhUmtaA | neutral | 29 | 20.88 | 21.39 | 15.37 | 0.00 | 50.80 | 25.32 |
| aFt8UlJUS7WAxa3lTutG-g | neutral | 29 | 20.78 | 16.04 | 20.42 | 0.00 | 74.20 | 29.31 |
| UhDwyHuQSByzKUI5ODt3BA | neutral | 29 | 20.65 | 18.72 | 22.30 | 0.00 | 98.93 | 23.89 |
| DOMbfmMIQm26gMZFyHcNig | neutral | 29 | 20.64 | 21.37 | 15.04 | 0.00 | 45.34 | 24.68 |
| IxhoF2OrSg6G-S3bLLBuKg | neutral | 29 | 19.91 | 15.60 | 17.15 | 0.00 | 62.39 | 23.34 |
| aX7_5eB-SruGeFTptfKWlw | neutral | 29 | 19.79 | 14.61 | 20.26 | 0.00 | 70.85 | 24.74 |
| RCTBAs45RtexLbtA_5neYQ | neutral | 29 | 19.19 | 17.82 | 16.08 | 0.00 | 54.71 | 21.10 |
| edp0qJG3Sq-IylHfCZujlQ | neutral | 29 | 18.33 | 11.31 | 20.92 | 0.00 | 75.96 | 26.69 |
| LjXAg-VDTOmUx67OTpGqpA | neutral | 29 | 18.15 | 16.66 | 17.69 | 0.00 | 74.86 | 27.41 |
| Ve8nUpU4SQCgt1ipuRGFyw | neutral | 29 | 18.08 | 14.65 | 16.71 | 0.00 | 61.50 | 27.37 |
| RriA_iA-T8CtzcT6pDhKcA | neutral | 29 | 17.76 | 8.69 | 19.45 | 0.00 | 58.71 | 28.74 |
| MapBKrtrS4uB7abY_2SEYg | neutral | 29 | 17.55 | 17.82 | 15.51 | 0.00 | 55.70 | 23.36 |
| YMjbkdnMSqilocbDaFK_lQ | neutral | 29 | 17.43 | 8.02 | 20.29 | 0.00 | 62.83 | 23.41 |
| KSUr2ajwS32SGAk3E59kwQ | neutral | 29 | 16.93 | 10.69 | 17.13 | 0.00 | 51.47 | 25.41 |
| cEbHF7JfTyehqLWkti6wgQ | neutral | 29 | 16.80 | 17.83 | 14.42 | 0.00 | 46.79 | 24.43 |
| cBjegjXNSHOl-M9V9Z-duw | neutral | 29 | 16.78 | 13.37 | 15.58 | 0.00 | 50.67 | 27.41 |
| b_8Yg8CSQPyEae6CbFyV0Q | neutral | 29 | 16.71 | 9.94 | 17.18 | 0.00 | 62.01 | 29.41 |
| ScZovXGJRdO257M1YbYzOw | neutral | 29 | 16.46 | 6.68 | 21.63 | 0.00 | 69.07 | 24.51 |
| E9z6UYe2Qnu-gdsCpob12A | neutral | 29 | 15.90 | 10.00 | 15.71 | 0.00 | 57.49 | 23.44 |
| JbYJh1i-Q7CKzV1HlsBcmQ | neutral | 29 | 15.25 | 13.37 | 11.82 | 0.00 | 41.95 | 16.04 |
| a5wTdTZzRBWI8S5rtGpSnw | neutral | 29 | 15.11 | 12.58 | 16.01 | 0.00 | 68.19 | 21.98 |
| X9Z8xCu-TNe9rXbU-8Wkdg | neutral | 29 | 14.92 | 13.37 | 12.89 | 0.00 | 46.04 | 19.86 |
| dpBTFNYGTIaEfm1C3JlVWw | neutral | 29 | 14.59 | 13.33 | 14.90 | 0.00 | 48.70 | 20.66 |
| DsaJ56FjR0Cb14kA_GqTXw | neutral | 29 | 13.95 | 7.78 | 14.63 | 0.00 | 44.56 | 24.51 |
| L4xt7K7OTPSrmYAYSUplWQ | neutral | 29 | 13.46 | 5.35 | 16.58 | 0.00 | 61.50 | 20.72 |
| bOAV4sD3StiJa9IPuXGfmA | neutral | 29 | 12.17 | 10.70 | 12.60 | 0.00 | 46.73 | 16.05 |
| avk_faNVR-etdQf4CvXR0A | neutral_face | 29 | 28.72 | 27.97 | 16.31 | 0.00 | 60.16 | 21.39 |
| CHk-QJZ1ThGlvByAi3I_RQ | neutral_face | 29 | 27.93 | 24.03 | 23.91 | 0.00 | 92.91 | 35.53 |
| Ym_NeAeOS8GjRc7sHx7leQ | neutral_face | 29 | 25.62 | 29.41 | 19.79 | 0.00 | 64.17 | 32.07 |
| CRbbrjoCQ8epVIGIa9qcGQ | neutral_face | 29 | 24.99 | 22.73 | 19.36 | 0.00 | 82.89 | 21.31 |
| KUXNVvwXTg6bcOP9dbXl4Q | neutral_face | 29 | 24.88 | 19.34 | 18.81 | 0.00 | 61.50 | 23.40 |
| Jk-2DYfARdOZFHZl54GTYw | neutral_face | 29 | 24.28 | 17.38 | 22.54 | 0.00 | 86.23 | 28.61 |
| fSG5fxkDTPeS1y7Cz44blw | neutral_face | 29 | 23.45 | 21.14 | 20.12 | 0.00 | 65.51 | 28.10 |
| S5f18yxeTJ227K9DSyWbjw | neutral_face | 29 | 23.40 | 24.66 | 15.82 | 0.00 | 52.67 | 30.10 |
| EOpW2Zg0Sc-2GKMkPQ2J2Q | neutral_face | 29 | 23.39 | 20.01 | 20.95 | 0.00 | 67.51 | 34.09 |
| E37Nm1hER9WMwQvsa2Hflw | neutral_face | 29 | 22.42 | 14.71 | 22.02 | 0.00 | 70.85 | 38.11 |
| K2MSJLWFQ9SzRgId1rIUHA | neutral_face | 29 | 21.90 | 16.66 | 20.77 | 0.00 | 89.57 | 28.42 |
| QFVNirMFT5uK66NfTCL2cw | neutral_face | 29 | 20.52 | 16.71 | 18.91 | 0.00 | 62.83 | 28.58 |
| aVGF810aT3S69s0ZSZgX2Q | neutral_face | 29 | 19.65 | 14.71 | 16.88 | 0.00 | 62.48 | 21.34 |
| 68123416 | sad_face | 29 | 29.54 | 26.74 | 20.79 | 0.00 | 72.19 | 35.34 |
| 68123405 | sad_face | 29 | 28.27 | 25.40 | 16.93 | 0.00 | 60.00 | 20.66 |
| 68123458 | sad_face | 29 | 23.84 | 23.31 | 19.77 | 0.00 | 70.19 | 32.66 |
| 68123426 | sad_face | 29 | 22.50 | 21.39 | 17.58 | 0.00 | 69.04 | 18.05 |
| 68123497 | sad_face | 29 | 20.93 | 18.64 | 17.12 | 0.00 | 59.49 | 21.92 |
| 68123537 | sad_face | 29 | 20.25 | 21.34 | 17.38 | 0.00 | 56.20 | 28.74 |
| 68123524 | sad_face | 29 | 19.38 | 14.71 | 18.10 | 0.00 | 60.83 | 19.97 |
| 68123391 | sad_face | 29 | 17.36 | 10.70 | 19.00 | 0.00 | 73.53 | 23.99 |
| QGxFijjYTfWrvg-X02lKcw | sleep_related | 29 | 30.37 | 30.68 | 22.68 | 0.00 | 89.57 | 31.26 |
| XfzYJsixTLCkgWabGvqmlw | sleep_related | 29 | 27.54 | 25.40 | 20.39 | 0.00 | 79.30 | 27.34 |
| DJw0-xR_TCaB-_LfnL6lig | sleep_related | 29 | 24.89 | 21.39 | 19.80 | 0.00 | 81.55 | 28.67 |
| dIsJdajoT4msRkkJ_zfW3w | sleep_related | 29 | 24.28 | 16.04 | 22.66 | 0.00 | 80.21 | 29.40 |
| b1Q664ESSTG5H25GTXaraQ | sleep_related | 29 | 24.12 | 26.02 | 15.28 | 0.00 | 61.31 | 20.02 |
| MamyfpQXRqCkhsxuPo2UxQ | sleep_related | 29 | 22.73 | 12.03 | 26.47 | 0.00 | 96.26 | 34.09 |
| YaLqQjVwQz6vQerO40WDBg | sleep_related | 29 | 20.47 | 18.04 | 18.88 | 0.00 | 65.51 | 33.32 |
| A_4H9MYOSCi9sWd3eD8UHA | soldiers | 29 | 32.30 | 27.41 | 25.05 | 0.00 | 89.57 | 43.30 |
| DnxOjrfTQhy9XTxVLuLkQA | soldiers | 29 | 29.85 | 19.36 | 25.27 | 0.00 | 76.87 | 47.46 |
| C2BYNvtJTjOgDpgLvVllVQ | soldiers | 29 | 28.19 | 21.31 | 25.60 | 0.00 | 78.88 | 42.81 |
| A_-1OArYQ_adCPIKemPHdg | soldiers | 29 | 27.96 | 21.39 | 22.32 | 0.00 | 74.87 | 29.41 |
| VZYx7WlqSna6IT90T01LsQ | soldiers | 29 | 27.43 | 25.40 | 22.00 | 0.00 | 76.68 | 35.46 |
| JcPDoVJFSBOgXj8ah7sktg | soldiers | 29 | 26.18 | 31.34 | 24.15 | 0.00 | 65.51 | 45.32 |
| FJdnEtD7Sk2EI0szZnHvag | soldiers | 29 | 26.12 | 26.04 | 15.86 | 0.00 | 60.66 | 12.09 |
| WMKKOlK4QrGOs3Cn2b_lZg | soldiers | 29 | 22.14 | 23.66 | 19.29 | 0.00 | 60.64 | 34.68 |
| Xr4MjhfmTraeKHh0zeNi_Q | warfare | 29 | 34.24 | 40.11 | 20.64 | 0.00 | 67.00 | 38.00 |
| A0FBsiMtS76m71TF6zckvA | warfare | 29 | 27.29 | 22.73 | 23.61 | 0.00 | 83.55 | 38.77 |
| OHKQX4gnTWeT_PiEr1dDeg | warfare | 29 | 26.78 | 22.67 | 21.36 | 0.00 | 80.00 | 28.76 |
| ezkn-4dzQuS05frSm-jyGA | warfare | 29 | 26.60 | 22.00 | 23.34 | 0.00 | 83.34 | 35.52 |
| R0NAzO_VSdqYLe6zb_H3-Q | warfare | 29 | 25.09 | 24.11 | 20.28 | 0.00 | 66.84 | 28.08 |
| LUfNX6YAT-KEsiV3SxKq2w | warfare | 29 | 24.64 | 20.67 | 21.84 | 0.00 | 70.19 | 27.00 |
| NB3PTjWUR_SdWHVUuhnXBg | warfare | 29 | 24.51 | 19.31 | 24.46 | 0.00 | 96.26 | 21.02 |
| CLZddDIORpCOa5MK6Rsc7w | warfare | 29 | 24.19 | 20.05 | 23.10 | 0.00 | 77.54 | 26.75 |
| EZke_5L8R-y--ZMKEVT5qw | warfare | 29 | 23.74 | 20.05 | 21.52 | 0.00 | 64.84 | 37.43 |
| Onhyu_ssRze6tmryDPDhcw | warfare | 29 | 22.54 | 20.00 | 22.63 | 0.00 | 70.00 | 36.77 |
| KzR2IFB3TZOI8LzfUmb0Gw | warfare | 29 | 20.10 | 13.37 | 20.13 | 0.00 | 58.82 | 24.73 |
| ajpX0QFhSHSqvoYiV23Iag | warfare | 29 | 19.27 | 13.37 | 18.68 | 0.00 | 64.84 | 29.33 |

## 9. Conclusions & Interpretations

### Attentional capture by threat-related imagery

The ranked overview reveals a clear pattern: **threat-related categories dominate the high end of the dwell-time distribution**. The top 10 most-gazed-at images are overwhelmingly anxiety_inducing (5 of 10), with combat_vehicles, warfare, and soldiers also represented. This is consistent with attentional bias theories of PTSD, where threat-relevant stimuli preferentially capture and hold visual attention. Notably, this pattern emerges at the *individual image* level, not just at the category average, suggesting that specific high-salience images drive much of the effect.

### Neutral images cluster at the bottom

8 of the 10 least-gazed-at images are neutral, with mean dwell times of 12-16% — roughly half the dwell time of the top threat images. This confirms that the image set successfully differentiates emotional from non-emotional content at the behavioral level. The two non-neutral images in the bottom 10 (happy_face) suggest that some positive-valence stimuli may also fail to capture sustained attention.

### High within-image variability signals individual differences

The overall SD of dwell % across sessions is high (mean SD = 19.6%), indicating substantial between-participant variability in how long they look at any given image. The positive mean-SD correlation (r = 0.553, p < 0.001) means that images attracting more attention on average also show *more disagreement* between participants — precisely the pattern expected if PTSD status or trauma history modulates attentional engagement with threat stimuli. This variability is a promising signal for downstream PTSD vs. non-PTSD comparisons.

### Combat_vehicles and anxiety_inducing show the most extreme variability

All 6 high-variability outlier images (SD > 26.6%) come from combat_vehicles or anxiety_inducing categories. Some of these images have very high means with high SD, while others have moderate means but extreme SD. The latter pattern — where the SD exceeds the mean — indicates a bimodal response: some participants fixate heavily while others largely avoid the image. This bimodality is particularly interesting for group-level analyses, as it may reflect approach/avoidance differences tied to trauma exposure.

### Low-variability images are uniformly low-interest

The 3 low-variability outlier images (SD < 12.6%) are all low-mean neutral or happy_face images. Participants consistently show little interest in these stimuli, producing a floor effect with compressed variance. These images contribute minimal signal to between-group comparisons.

### Within-category heterogeneity

The box plots and violin plots reveal that not all images within a category behave identically. For example:
- **combat_vehicles** spans from 17.6% to 37.4% mean dwell — a 2.1x range within the same category
- **anxiety_inducing** spans from 22.2% to 37.9% mean dwell — a 1.7x range within the same category
- **neutral** spans from 12.2% to 28.5% mean dwell — a 2.3x range within the same category

This within-category heterogeneity suggests that image-level analysis (rather than category-level averaging) may capture effects that would otherwise be washed out by noisy or non-representative images within a category.

### Normality of per-image means supports parametric methods

The distribution of per-image mean dwell % passes the Shapiro-Wilk normality test (W = 0.989, p = 0.264), with low skewness (0.28) and near-zero excess kurtosis (0.10). This supports the use of parametric statistical methods (e.g., t-tests, ANOVA, linear mixed models) for group comparisons in subsequent analyses.

### Implications for downstream PTSD analyses

1. **Image-level modeling is warranted**: The large within-category spread and image-level variability suggest that collapsing to category means may lose important signal. Mixed models with random intercepts for image_id would preserve this information.
2. **High-variability threat images are prime candidates** for detecting PTSD-related attentional differences — their large between-participant spread likely reflects the very individual differences the study aims to capture.
3. **Floor effects in neutral images** should be considered when computing contrast scores (threat minus neutral), as the low-dwell neutral images may introduce noise rather than signal.
4. **The 0.0% dwell-time floor** (present in every image's minimum) indicates that some sessions recorded zero gaze on certain AOIs, likely reflecting momentary off-screen gaze or fixation on the competing image. This is structurally expected given the paired-image presentation format and does not represent missing data.

