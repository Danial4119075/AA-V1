# Task C — Empirical Analysis (Report, 2 pages)

Let *n* = |V|, *m* = |E|, *T* = horizon, *X* = MC simulations, deg(*v*) = degree of *v*.

## 1. Algorithm Complexity Analysis (2 marks)

| Algorithm × Representation | Complexity | Dominant operation |
|---|---|---|
| (a) **MC × Matrix** | **O(X · T² · n²)** | row scan in `get_neighbours()` (line 6 Alg. 1) — *n* cells per call, ignoring zeros |
| (b) **MC × List**   | **O(X · T² · (n + m))** | linked-list traversal — ∑ deg(*v*) = 2*m* per inner day |
| (c) **DP × Matrix** | **O(T · n²)**            | row scan in the neighbour-product loop (line 8 Alg. 2) |
| (d) **DP × List**   | **O(T · (n + m))**       | linked-list traversal in the same loop |

Monte Carlo pays an extra *XT* factor: *X* fresh simulations are launched at each of the *T* outer days, and each re-plays *t* ∈ [1,*t*] days from scratch (∑ *t* ≈ *T*²/2 inner-day passes). The DP fills the table column-by-column reading only the previous column, so it visits each edge once per day rather than once per day-per-simulation. Swapping representations only changes the neighbour-loop cost: O(*n*) per vertex for matrix versus O(deg(*v*)) for list — lists dominate on sparse graphs, the gap closes at full density.

## 2. Empirical Design (2 marks)

Four free parameters drive the runtime: **n, m (or density d = m / C(n,2)), T, X**. I vary one per plot and hold the others fixed so each plot isolates one asymptotic dimension. Other simulation parameters (`max_transmission_prob`, vulnerability/dosage ranges, graph seed) do not appear in the complexity, so they stay at default values.

| Exp | Vary | Hold | What it isolates |
|---|---|---|---|
| (a) | *n* ∈ {10, 20, 40, 60, 80, 120}   | d = 0.30, T = 8, X = 50 | Scaling with population size |
| (b) | *T* ∈ {2, 5, 10, 20, 40}           | n = 60, d = 0.30, X = 50 | DP linear-in-*T* vs MC quadratic-in-*T* |
| (c) | *d* ∈ {0.05, 0.1, 0.2, 0.4, 0.8}   | n = 60, T = 8, X = 50   | Matrix density-independence vs list density-dependence |
| (d) | *X* ∈ {10, 30, 100, 300, 1000}     | n = 60, d = 0.30, T = 8 | MC linear-in-*X*; DP independent |

Each point is the mean of **3 trials on independent random graphs** (graph seeds 100/101/102; MC noise seeds 7/8/9), timed with `utils/timer.py` inside the sweep driver `task_c_analysis.py`. Only the algorithm call is timed — graph construction is excluded per the spec tip. Plots use log axes when the swept parameter spans more than one decade so polynomial slopes appear as straight lines.

## 3. Empirical Analysis (2.5 marks)

![Runtime of all four (algorithm, representation) combinations across the four sweeps.](figures/task_c_combined.png){width=78%}

**(a) vs n.** Straight log-log lines of slope ≈ 2 across all four series — at d = 0.30, *m* ≈ 0.15*n*² so even DP-list is dominated by an *n*² term. DP and MC clusters are separated by ~150× (within an order of magnitude of the predicted XT = 400). Within each cluster matrix is ~1.7× slower than list, smaller than the naive 1/d ≈ 3.3× because the matrix's contiguous row loop benefits from CPU cache locality.

**(b) vs T.** DP grows linearly (T ×4 ⇒ time ×4). MC bends upward: MC-list grows 222 → 1878 ms over T = 10 → 40 (×8.4), close to the predicted T² = ×16, slightly sub-quadratic due to fixed per-day overhead. The *T*² blow-up dominates regardless of representation.

**(c) vs density.** Matrix curves are nearly flat (the row scan visits *n* cells regardless of zeros); list curves rise linearly with *m*. List–matrix gap is ~5× at d = 0.05 and shrinks to ~1.3× at d = 0.80 — the textbook crossover where ∑ deg(*v*) approaches *n*².

**(d) vs X.** Both MC variants are slope-1 log-log lines (linear in *X*); DP lines are flat at ~0.9 ms (list) / ~1.7 ms (matrix). At X = 1000 the MC error on cyclic networks is still 1–2 % per cell vs the exact DP, so *X* is rarely cut below the hundreds — locking in a 100×+ slowdown at any useful accuracy.

## 4. Reflection (1.5 marks)

Results match §1: every slope agrees with the dominant complexity term within constant factors, and the qualitative features (matrix density-independence, MC quadratic in *T*, DP independent of *X*) are visible at a glance. Minor deviations: MC is slightly sub-quadratic in *T* due to fixed per-day RNG/bookkeeping overhead; at small *n* DP-matrix is only marginally slower than DP-list because contiguous rows are more cache-friendly than linked lists.

**Recommendation for Metropolis.** The city is large, sparsely connected, modest *T*. Cost ordering: DP-list (O(*Tm*)) ≪ DP-matrix (O(*Tn*²)) ≪ MC-list (O(*XT*²*m*)) ≪ MC-matrix (O(*XT*²*n*²)). **DP-list wins on every axis** — exact, *X*-free, linear in *T*, scales with *m* not *n*². At n = 60, d = 0.05 it ran ~145× faster than MC-list (*sub-second per day vs minutes at city scale*) and ~3.5× faster than DP-matrix. **Daily updates to weights/connections do not change this**: the DP recurrence is structural, generalises to time-varying *w*<sub>ij,t</sub> at the same O(*Tm*) cost, and is a sub-second per-day job at city scale; MC gains nothing from incremental updates either. MC only overtakes DP when the model itself outgrows a closed-form recurrence (heterogeneous incubation, agent memory) and exact computation becomes intractable.

\newpage
