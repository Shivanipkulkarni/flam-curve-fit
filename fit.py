# ===== Flam R&D Assignment — Order-Independent Curve Parameter Recovery =====
import numpy as np
import pandas as pd
from scipy.optimize import least_squares, differential_evolution


THETA_MIN, THETA_MAX = np.radians(0.0), np.radians(50.0)
M_MIN, M_MAX = -0.05, 0.05
X_MIN, X_MAX = 0.0, 100.0


def uv(theta, X, x, y):
    """Inverse-rotate data points by -theta to recover their (t, v) coordinates."""
    u = (x - X) * np.cos(theta) + (y - 42) * np.sin(theta)
    w = -(x - X) * np.sin(theta) + (y - 42) * np.cos(theta)
    return u, w


def residuals(params, x, y):
    """Residual between the inverse-transformed data and the curve model."""
    theta, M, X = params
    u, w = uv(theta, X, x, y)
    pred_w = np.exp(M * np.abs(u)) * np.sin(0.3 * u)
    return w - pred_w


def objective(params, x, y):
    """Squared-residual objective used by differential evolution."""
    return np.sum(residuals(params, x, y) ** 2)


def main():
    # -------------------------------------------------------------------------
    # 1. Load supplied data
    # -------------------------------------------------------------------------
    df = pd.read_csv("xy_data.csv")
    x = df["x"].to_numpy(dtype=float)
    y = df["y"].to_numpy(dtype=float)

    # -------------------------------------------------------------------------
    # 2. Global optimization
    # -------------------------------------------------------------------------
    bounds = [
        (THETA_MIN, THETA_MAX),
        (M_MIN, M_MAX),
        (X_MIN, X_MAX),
    ]

    result_de = differential_evolution(
        objective,
        bounds,
        args=(x, y),
        seed=42,
        tol=1e-12,
        maxiter=2000,
        popsize=40,
        polish=True,
    )

    theta0, M0, X0 = result_de.x

    # -------------------------------------------------------------------------
    # 3. Local least-squares refinement
    # -------------------------------------------------------------------------
    result_ls = least_squares(
        residuals,
        x0=[theta0, M0, X0],
        args=(x, y),
        bounds=(
            [THETA_MIN, M_MIN, X_MIN],
            [THETA_MAX, M_MAX, X_MAX],
        ),
    )

    theta, M, X = result_ls.x

    # -------------------------------------------------------------------------
    # 4. Recover t values and inspect the fit
    # -------------------------------------------------------------------------
    u, w = uv(theta, X, x, y)

    print(f"theta = {np.degrees(theta):.4f} deg")
    print(f"M     = {M:.6f}")
    print(f"X     = {X:.4f}")

    print(
        f"Recovered t range: "
        f"[{u.min():.3f}, {u.max():.3f}] "
        f"(should be inside [6,60])"
    )
    print(f"Fraction inside [6,60]: {np.mean((u >= 6) & (u <= 60)):.4f}")

    resid = w - np.exp(M * np.abs(u)) * np.sin(0.3 * u)
    print(f"Mean residual: {np.mean(np.abs(resid)):.6f}")

    # -------------------------------------------------------------------------
    # 5. Reconstruct the fitted curve on a uniform t grid
    # -------------------------------------------------------------------------
    t_uniform = np.linspace(6, 60, 2000)
    v_uniform = np.exp(M * np.abs(t_uniform)) * np.sin(0.3 * t_uniform)

    x_pred = (
        t_uniform * np.cos(theta)
        - v_uniform * np.sin(theta)
        + X
    )
    y_pred = (
        42
        + t_uniform * np.sin(theta)
        + v_uniform * np.cos(theta)
    )

    # Mean nearest-point L1 distance from each supplied point
    # to the uniformly sampled reconstructed curve.
    l1 = [
        np.min(np.abs(x_pred - xi) + np.abs(y_pred - yi))
        for xi, yi in zip(x, y)
    ]
    print(f"Mean L1 distance: {np.mean(l1):.6f}")

    # -------------------------------------------------------------------------
    # 6. Generate a Desmos-compatible representation
    # -------------------------------------------------------------------------
    print("\nDesmos string:")
    print(
        f"\\left("
        f"t*\\cos({theta:.5f})"
        f"-e^{{{M:.5f}\\left|t\\right|}}"
        f"\\cdot\\sin(0.3t)\\sin({theta:.5f})"
        f"+{X:.5f},"
        f"42+t*\\sin({theta:.5f})"
        f"+e^{{{M:.5f}\\left|t\\right|}}"
        f"\\cdot\\sin(0.3t)\\cos({theta:.5f})"
        f"\\right)"
    )


if __name__ == "__main__":
    main()
