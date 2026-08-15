# Flam R&D/AI Assignment — Parametric Curve Parameter Recovery

## Data note
The original xy_data.csv link in the assignment was inaccessible. Used a
publicly available dataset matching the same format (Kaggle:
tejasindukuri/flam-dataset) as the closest available substitute.

## Key insight
The equations decouple into a rotation + translation:
(x-X, y-42) = R(theta) * (t, v),  where v = e^(M|t|)*sin(0.3t)

The dataset rows are NOT ordered by t, so instead of guessing t per row,
I inverted the rotation: rotating any data point by -theta recovers that
point's own t directly, with no ordering assumption needed:

u_i = (x_i-X)*cos(theta) + (y_i-42)*sin(theta)   [ = t_i ]
w_i = -(x_i-X)*sin(theta) + (y_i-42)*cos(theta)  [ = v_i ]

Fitting reduces to a 3-parameter joint optimization requiring
w_i ≈ e^(M*u_i)*sin(0.3*u_i) at every point — no latent per-point
unknowns. Used differential_evolution (global) + least_squares (polish).

## Validation
- 100% of recovered t values land inside the required (6, 60) range
- Mean residual ~0.000003
- Mean L1 distance (data vs. fitted curve): ~0.01

## Result
theta = 30.0000 deg
M     = 0.030000
X     = 55.0000

Desmos: \left(t*\cos(0.52360)-e^{0.03000\left|t\right|}\cdot\sin(0.3t)\sin(0.52360)+55.00000,42+t*\sin(0.52360)+e^{0.03000\left|t\right|}\cdot\sin(0.3t)\cos(0.52360)\right)
