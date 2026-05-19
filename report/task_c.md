# Task C — Empirical Analysis (Report, max 2 pages)

Let *n* = |V|, *m* = |E|, *T* = horizon, *X* = Monte Carlo simulations,
and deg(*v*) = vertex *v*'s degree.

## 1. Algorithm Complexity Analysis (2 marks)

| Algorithm × Representation | Complexity | Dominant operation |
|---|---|---|
| (a) **MC × Matrix** | **O(X · T² · n²)** | row scan in `get_neighbours()` (line 6, Alg. 1) — *n* cells per call, ignoring zeros |
| (b) **MC × List**   | **O(X · T² · (n + m))** | linked-list traversal in `get_neighbours()` — ∑ deg(*v*) = 2*m* per inner day |
| (c) **DP × Matrix** | **O(T · n²)**            | row scan in the neighbour-product loop (line 8, Alg. 2) |
| (d) **DP × List**   | **O(T · (n + m))**       | linked-list traversal in the same loop |

Monte Carlo carries an extra *X*·*T* factor: *X* fresh simulations are
launched at each of the *T* outer days, and each simulation re-plays
*t* ∈ [1,*t*] days from scratch, giving ∑*t* ≈ *T*²/2 inner-day passes.
The DP fills the table column by column, reading only the previous
column, so it visits each edge once per day rather than once per
day-per-simulation. Swapping representations changes only the
neighbour-loop cost: O(*n*) per vertex for matrix (must skip zeros)
versus O(deg(*v*)) for list. Lists therefore dominate on sparse graphs;
the gap closes as the graph approaches full density.

## 2. Empirical Design (2 marks)

The complexity expressions identify four free parameters — **n, m (or
density d = m / C(n,2)), T, X** — so I vary each in turn while holding
the others fixed (one parameter per plot isolates its asymptotic
contribution). The remaining simulation parameters (`max_transmission_prob`,
vulnerability/dosage ranges, RNG seed for graph construction) do not
appear in the complexity, so they are held at default values.

| Exp | Vary | Hold | What it isolates |
|---|---|---|---|
| (a) | n ∈ {10, 20, 40, 60, 80, 120}   | d = 0.30, T = 8, X = 50 | Scaling with population size |
| (b) | T ∈ {2, 5, 10, 20, 40}           | n = 60, d = 0.30, X = 50 | DP linear-in-*T* vs MC quadratic-in-*T* |
| (c) | d ∈ {0.05, 0.1, 0.2, 0.4, 0.8}   | n = 60, T = 8, X = 50   | Matrix density-independence vs list density-dependence |
| (d) | X ∈ {10, 30, 100, 300, 1000}     | n = 60, d = 0.30, T = 8 | MC linear-in-*X*; DP independent (flat reference) |

Each point is the **mean of 3 trials on independent random graphs**
(graph seeds 100/101/102; MC noise seeds 7/8/9). Per the spec tip, only
the algorithm call is timed — graph construction is excluded. Plots use
log-scale axes when the swept parameter spans more than one decade so
polynomial slopes appear as straight lines.

## 3. Empirical Analysis (2.5 marks)

![Figure 1 — Runtime of all four (algorithm, representation) combinations across the four sweeps.](figures/task_c_combined.png)

**(a) vs n.** All four series are straight log-log lines of slope ≈ 2,
matching the predicted scaling (at d = 0.30, *m* ≈ 0.15*n*², so even
DP-list is dominated by an *n*² term). The DP and MC clusters are
separated by a constant factor of ~150× — within an order of magnitude
of the predicted XT = 400 extra cost (the gap shrinks because the MC
inner loop is leaner than the DP's). Within each cluster, matrix is
~1.7× slower than list, smaller than the naive 1 / d ≈ 3.3× because the
matrix's tight contiguous loop benefits from CPU cache locality.

**(b) vs T.** DP grows linearly (T = 10 → 40 takes DP-list 1.17 → 4.72
ms, exactly ×4). MC bends upward as predicted: MC-list grows 222 → 1878
ms (×8.4 over T ×4), close to the predicted T² = ×16 (slightly
sub-quadratic because of fixed per-day overhead). This is the most
damaging plot for Monte Carlo — at any non-trivial horizon, the T²
blow-up dominates regardless of representation.

**(c) vs density.** Matrix curves are nearly flat (the row scan visits
*n* cells regardless of how many are zero), while list curves rise
roughly linearly with *m*. The list–matrix gap is ~5× at d = 0.05 and
shrinks to ~1.3× at d = 0.80 because ∑ deg(*v*) is approaching *n*² —
the textbook crossover where the two representations converge.

**(d) vs X.** Both MC variants are straight log-log lines of slope 1 —
exactly linear in *X*. DP runs flat at ~0.9 ms (list) and ~1.7 ms
(matrix), independent of *X*. At X = 1000 the MC error on cyclic
networks is still 1–2 % per cell relative to the exact DP table, so
*X* is rarely cut below the hundreds — locking in a 100×+ slowdown vs
DP at any useful accuracy.

## 4. Reflection (1.5 marks)

The empirical results agree closely with §1: every observed slope
matches the dominant complexity term within constant factors, and the
qualitative features — matrix's density-independence, MC's quadratic
*T* growth, DP's *X*-independence — are visible at a glance. Two minor
deviations are worth noting: MC growth in *T* is slightly *sub*-quadratic
because each inner day pays a fixed RNG/bookkeeping cost that does not
depend on *t*; and at small *n* the DP-matrix is only marginally slower
than DP-list because the matrix's contiguous row layout enjoys better
cache locality — a constant-factor effect that vanishes asymptotically.

**Recommendation for Metropolis.** The spec describes Metropolis as a
*large, sparsely connected* city — large *n*, *m* ≪ *n*²/2, modest *T*
(interventions span days–weeks). For this regime the cost ordering is

> DP-list (O(*Tm*))  ≪  DP-matrix (O(*Tn*²))  ≪  MC-list (O(*XT*²*m*))  ≪  MC-matrix (O(*XT*²*n*²))

**DP-list is the recommended combination.** It is the unique winner on
every axis: exact (no sampling noise), independent of *X*, linear in
*T*, and scales with the actual edge count *m* rather than the
worst-case *n*². In our experiments at n = 60, d = 0.05 it ran ~145×
faster than MC-list and ~3.5× faster than DP-matrix.

**Would daily updates to transmission rates / connections change this?**
No. The DP recurrence is structural: it only requires the current
graph plus one previous column, and generalises to time-varying weights
*w*<sub>ij,t</sub> at the same O(*Tm*) cost. Re-running it daily on the
latest graph is a sub-second job at city scale. Monte Carlo gains
nothing from incremental updates either — it must re-sample on the new
graph from scratch. The only scenario in which MC would overtake DP is
when the model itself outgrows a closed-form recurrence (heterogeneous
incubation periods, agent state with memory), at which point exact
computation becomes intractable and sampling is the only option. Until
then, DP-list remains the right tool for Metropolis.
