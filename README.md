# Flam R&D Assignment: Parametric Curve Parameter Recovery

## 1. Problem

Recover the 3 unknown parameters $\theta$, $M$, and $X$ given points that lie on the following parametric curve.

$$
x(t) =
t\cos(\theta)
-
e^{M|t|}\sin(0.3t)\sin(\theta)
+
X
$$

$$
y(t) =
42
+
t\sin(\theta)
+
e^{M|t|}\sin(0.3t)\cos(\theta)
$$

with the constraints:

$$
0^\circ < \theta < 50^\circ
$$

$$
-0.05 < M < 0.05
$$

$$
0 < X < 100
$$

and

$$
6 < t < 60
$$

Points are sampled from this curve and provided in `xy_data.csv`. The rows are not assumed to be ordered according to the underlying parameter $t$.

The final recovered parameters are:

$$
\boxed{\theta = 30^\circ}
$$

$$
\boxed{M = 0.03}
$$

$$
\boxed{X = 55}
$$

---

## 2. Key Observation

The key observation is that the given curve can be viewed as a simple parametric curve that has been rotated by $\theta$ and then translated by $(X,42)$.

Define

$$
v(t) = e^{M|t|}\sin(0.3t)
$$

Then the parametric equation can be written as:

$$
\begin{bmatrix}
x-X \\
y-42
\end{bmatrix}
=
\begin{bmatrix}
\cos\theta & -\sin\theta \\
\sin\theta & \cos\theta
\end{bmatrix}
\begin{bmatrix}
t \\
v(t)
\end{bmatrix}
$$

This gives us a crucial simplification. Instead of treating all the $t_i$ values as additional unknowns, we can invert this transformation and recover them directly.

---

## 3. Recovering $t$ Without Knowing the Point Order

For a candidate value of $\theta$ and $X$, translate all observed points by $(-X,-42)$ and then rotate them by $-\theta$.

For a point $(x_i,y_i)$, define:

$$
u_i =
(x_i-X)\cos\theta
+
(y_i-42)\sin\theta
$$

$$
w_i =
-(x_i-X)\sin\theta
+
(y_i-42)\cos\theta
$$

Because this is the inverse of the original rotation:

$$
u_i = t_i
$$

and

$$
w_i =
e^{M|t_i|}\sin(0.3t_i)
$$

This is particularly useful because we no longer need to estimate each $t_i$ as a separate optimization variable.

The points can therefore be processed without relying on their original ordering in the dataset.

---

## 4. Optimization Objective

For candidate parameters

$$
(\theta,M,X)
$$

the recovered coordinates are:

$$
t_i=u_i
$$

and the model predicts:

$$
\hat w_i =
e^{M|u_i|}
\sin(0.3u_i)
$$

The residual for each point is:

$$
r_i =
w_i-\hat w_i
$$

The optimization objective is therefore:

$$
\min_{\theta,M,X}
\sum_i r_i^2
$$

subject to the parameter bounds specified in the assignment.

Therefore, the problem reduces to optimizing over only 3 unknown parameters.

---

## 5. Optimization Strategy

I implemented a two-stage optimization process.

### Stage 1: Global Search

The `scipy.optimize.differential_evolution` algorithm was first used to perform a bounded global search over the parameter space specified by the assignment:

- $0 \leq \theta \leq 50^\circ$
- $-0.05 \leq M \leq 0.05$
- $0 \leq X \leq 100$

This reduces dependence on an arbitrary initial guess and helps avoid getting stuck in a poor local solution.

### Stage 2: Local Refinement

The result from differential evolution is then supplied as the initial point for `scipy.optimize.least_squares`.

`least_squares` performs a local refinement of the parameters and improves the numerical accuracy of the final solution.

The overall process is:

1. Observed $(x,y)$ points.
2. Inverse translation + rotation.
3. Recover candidate $t$ values.
4. Evaluate model residuals.
5. Differential Evolution.
6. Least-Squares refinement.
7. Recover $\theta$, $M$, and $X$.

---

## 6. Results

The optimization recovers:

| Parameter | Recovered value |
|---|---:|
| $\theta$ | $30.0000^\circ$ |
| $M$ | $0.030000$ |
| $X$ | $55.0000$ |

The recovered $t$ values are within the expected assignment range.

The fitted curve also produces a very small residual, indicating that the recovered parameters closely reproduce the supplied data.

---

## 7. Validation

Once the parameters are fitted, the curve can be reconstructed on a uniform grid:

$$
t \in [6,60]
$$

using 2000 uniformly spaced samples.

The reconstructed curve is:

$$
x_{\mathrm{pred}}(t)
=
t\cos\theta
-
e^{M|t|}\sin(0.3t)\sin\theta
+
X
$$

$$
y_{\mathrm{pred}}(t)
=
42
+
t\sin\theta
+
e^{M|t|}\sin(0.3t)\cos\theta
$$

As an additional validation measure, the implementation computes the mean nearest-point L1 distance from the supplied points to the uniformly sampled reconstruction of the fitted curve.

The current implementation obtains a mean L1 distance of approximately:

$$
\boxed{0.010}
$$

This provides a numerical indication of how closely the reconstructed curve matches the supplied data.

---

## 8. Why This Approach

A direct optimization approach could treat every point's $t_i$ as an additional optimization variable. For a large dataset, this would turn the problem into a high-dimensional optimization problem with potentially thousands of variables.

However, the inverse rotation gives us a way to recover each $t_i$ directly, so these values do not need to be included in the optimization.

Instead of solving for:

$$
\theta,M,X,t_1,t_2,\ldots,t_n
$$

we only need to search over:

$$
\boxed{\theta,M,X}
$$

This greatly simplifies the problem and also makes the solution independent of the ordering of the input points.

---

## 9. Interactive Explanation

An interactive visualization was created to demonstrate the underlying geometry.

The interactive lets you explore different parameter values and shows how applying the inverse transformation makes the hidden curve structure visible.

The main idea demonstrated by the visualization is:

```text
Observed curve
      |
      | inverse translation
      v
Centered curve
      |
      | inverse rotation
      v
Underlying curve
```

The visualization demonstrates how the observed curve can be transformed back to its underlying representation by first undoing the translation and then undoing the rotation.

### Point Inspector

The interactive explainer also allows individual data points to be inspected.

Clicking a point displays its transformation through the fitted model:

$$
(x_i,y_i)

ightarrow
(u_i,w_i)

ightarrow
(t_i,v(t_i))
$$

For the selected point, the visualization shows:

- the original $(x_i,y_i)$ coordinates
- the inverse-transformed coordinates $(u_i,w_i)$
- the recovered parameter $t_i=u_i$
- the model value $v(t_i)$
- the residual $w_i-v(t_i)$
- the corresponding point-level L1 distance

This provides a concrete example of the main idea used in the solution: **each point can be transformed independently, so the original ordering of the dataset is not required.**

**[Open the Interactive Curve Explainer](https://shivanipkulkarni.github.io/flam-curve-fit/interactive_explainer.html)**

---

## 10. Reproducing the Result

Clone the repository and install the required dependencies:

```bash
pip install numpy pandas scipy
```

Then run:

```bash
python fit.py
```

The script prints:

- recovered $\theta$
- recovered $M$
- recovered $X$
- recovered $t$ range
- fraction of recovered points inside the expected $t$ range
- mean residual
- mean L1 distance
- a Desmos-compatible representation of the fitted curve

---

## 11. Final Answer

The recovered unknown parameters are:

$$
\boxed{
\theta=30^\circ,\qquad
M=0.03,\qquad
X=55
}
$$

The solution is based on recognizing that the observed shape can be represented as a one-dimensional parametric curve that has been rotated and translated. By applying the inverse transformation, the individual $t_i$ values can be recovered directly, reducing the parameter recovery problem to a bounded 3-variable optimization.
