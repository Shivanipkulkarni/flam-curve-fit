# Flam R&D/AI Assignment — Parametric Curve Parameter Recovery

## Method
The equations decouple into a rotation + translation:
x - X = t*cos(theta) - v*sin(theta)
y - 42 = t*sin(theta) + v*cos(theta), where v = e^(M|t|)*sin(0.3t)

This means theta and M can be fit from the y-equation alone (X-independent),
then X solved in closed form. Steps: (1) coarse grid search over theta,M,
(2) refine with scipy least_squares on y only, (3) closed-form X,
(4) final joint 3-parameter polish, (5) validate via uniform-resample L1
distance — the same metric used for grading.

## Result
theta = <paste your value>, M = <paste your value>, X = <paste your value>

Desmos: <paste your Desmos string here>
