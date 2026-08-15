# ===== Flam R&D Assignment — Order-Independent Curve Parameter Recovery =====
import numpy as np
import pandas as pd
from scipy.optimize import least_squares, differential_evolution

THETA_MIN, THETA_MAX = np.radians(0.0), np.radians(50.0)
M_MIN, M_MAX = -0.05, 0.05
X_MIN, X_MAX = 0.0, 100.0

df = pd.read_csv("xy_data.csv")
x = df["x"].to_numpy(dtype=float)
y = df["y"].to_numpy(dtype=float)

def uv(theta, X, x, y):
    """Inverse-rotate a data point by -theta to recover its own (t, v)."""
    u = (x - X) * np.cos(theta) + (y - 42) * np.sin(theta)
    w = -(x - X) * np.sin(theta) + (y - 42) * np.cos(theta)
    return u, w

def residuals(params, x, y):
    theta, M, X = params
    u, w = uv(theta, X, x, y)
    pred_w = np.exp(M * np.abs(u)) * np.sin(0.3 * u)
    return w - pred_w

def objective(params, x, y):
    return np.sum(residuals(params, x, y) ** 2)

bounds = [(THETA_MIN, THETA_MAX), (M_MIN, M_MAX), (X_MIN, X_MAX)]
result_de = differential_evolution(objective, bounds, args=(x, y), seed=42,
                                    tol=1e-12, maxiter=2000, popsize=40, polish=True)
theta0, M0, X0 = result_de.x

res = least_squares(residuals, x0=[theta0, M0, X0], args=(x, y),
                     bounds=([THETA_MIN, M_MIN, X_MIN], [THETA_MAX, M_MAX, X_MAX]))
theta, M, X = res.x

u, w = uv(theta, X, x, y)
print(f"theta = {np.degrees(theta):.4f} deg")
print(f"M     = {M:.6f}")
print(f"X     = {X:.4f}")
print(f"Recovered t range: [{u.min():.3f}, {u.max():.3f}] (should be inside [6,60])")
print(f"Fraction inside [6,60]: {np.mean((u>=6)&(u<=60)):.4f}")

resid = w - np.exp(M*np.abs(u))*np.sin(0.3*u)
print(f"Mean residual: {np.mean(np.abs(resid)):.6f}")

t_uniform = np.linspace(6, 60, 2000)
v_uniform = np.exp(M*np.abs(t_uniform))*np.sin(0.3*t_uniform)
x_pred = t_uniform*np.cos(theta) - v_uniform*np.sin(theta) + X
y_pred = 42 + t_uniform*np.sin(theta) + v_uniform*np.cos(theta)
l1 = [min(np.abs(x_pred-xi)+np.abs(y_pred-yi)) for xi, yi in zip(x, y)]
print(f"Mean L1 distance: {np.mean(l1):.6f}")

print(f"\nDesmos string:")
print(f"\\left(t*\\cos({theta:.5f})-e^{{{M:.5f}\\left|t\\right|}}\\cdot\\sin(0.3t)\\sin({theta:.5f})+{X:.5f},42+t*\\sin({theta:.5f})+e^{{{M:.5f}\\left|t\\right|}}\\cdot\\sin(0.3t)\\cos({theta:.5f})\\right)")
