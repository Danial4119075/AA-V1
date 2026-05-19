# Task B — Infection Risk DP (Report)

## 1. Pseudo-code (1 mark)

```
Algorithm  TaskB(G, s, T)
Require:   Graph G = (V, E); source s; horizon T
Ensure:    Risk table where table[t][i] = r_{t,i}

 1: table ← (T + 1) × |V| array initialised to 0.0
 2: table[0][s.index] ← 1.0                       // base case: only s is infected
 3: for each day t = 1 to T do
 4:     prev ← table[t − 1]
 5:     curr ← table[t]
 6:     for each vertex V_i ∈ V do
 7:         escape ← 1 − prev[i]                  // P(V_i still healthy entering day t)
 8:         for each neighbour V_j of V_i do
 9:             escape ← escape · (1 − prev[j] · w_{ij})
10:         curr[i] ← 1 − escape
11:     curr[s.index] ← 1.0                       // patient zero is infected ∀ t
12: return table
```

Each column `t` is read from `table[t − 1]` and written to `table[t]`, so the
within-column iteration order over vertices does not matter — every value used
on line 9 has already been finalised on the previous day. Line 11 is defensive:
the recurrence already preserves `r_{t,s} = 1` whenever `prev[s] = 1`, but the
explicit assignment matches the Monte Carlo baseline and guards against
floating-point drift.

---

## 2. Limitations of the recurrence (3 marks)

### (a) The structural property that makes the recurrence approximate

The recurrence

```
r_{t,i} = 1 − (1 − r_{t-1,i}) · Π_{V_j ∈ N(V_i)} (1 − r_{t-1,j} · w_{ij})
```

multiplies one factor `(1 − r_{t-1,j} · w_{ij})` per neighbour. Treating these
factors as multiplicatively combinable is equivalent to assuming that the events
"`V_j` is infected by the end of day `t − 1`" are **mutually independent across
all neighbours `V_j` of `V_i`**.

In any non-trivial contact network this independence is false, because the
neighbours of `V_i` share infection history through two distinct mechanisms:

- **Shared upstream paths (cycles, multiple routes from the source).**
  When more than one path connects the source to a single vertex, the same
  upstream infection event is counted along each path as if it were independent.
- **Back-flow on undirected edges.**
  In an undirected contact graph, a downstream neighbour `V_j` of `V_i` can
  only have become infected *via* `V_i`. The recurrence still includes
  `(1 − r_{t-1,j} · w_{ij})` as if `V_j` were an independent potential
  infector of `V_i`.

Computing `r_{t,i}` exactly would require tracking the full joint distribution
over the `2^{|V|}` possible infection configurations of the network at each
time step. The recurrence trades that exponential cost for polynomial cost by
factorising the joint distribution into a product of marginals — and that
factorisation is the source of the error.

### (b) Specific term producing the error in Figure 5

Figure 5 shows the chain `V_0 — V_1 — V_2` with weights `w_{01} = 0.8` and
`w_{12} = 0.6`, with `V_0` as patient zero. Running the recurrence:

| `t` | `r_{t, V_0}` | `r_{t, V_1}` | `r_{t, V_2}` |
|----:|-------------:|-------------:|-------------:|
| 0   | 1.000        | 0.000        | 0.000        |
| 1   | 1.000        | 0.800        | 0.000        |
| 2   | 1.000        | 0.960        | 0.480        |
| 3   | 1.000        | **0.9943**   | 0.7795       |

Expanding the recurrence for `V_1` at `t = 3`:

```
r_{3, V_1} = 1 − (1 − 0.96) · (1 − 1.0 · 0.8) · (1 − 0.48 · 0.6)
           = 1 −  0.04       ·  0.20          ·  0.712
           = 0.9943
```

The **true** infection risk is `1 − (1 − w_{01})^3 = 1 − 0.2^3 = 0.992`,
because `V_2` was infected only through `V_1` — every scenario in which
`V_2 → V_1` "back-transmits" on day 3 is one in which `V_1` was already
infected first, so the back-transmission delivers no new infection events
to `V_1`.

The error is concentrated in the term

> **`(1 − r_{2, V_2} · w_{12}) = (1 − 0.48 · 0.6) = 0.712`**

which treats `V_2` as an independent potential source of infection for `V_1`,
ignoring that the entire `r_{2, V_2} = 0.48` mass arose from `V_1`'s own
earlier infections. This factor shrinks the escape product from the true
`0.2³ = 0.008` to the computed `0.005696`, which **over-estimates** the
infection risk (`0.9943` instead of `0.992`).

### (c) Graph class on which the recurrence is exact

The recurrence gives an exact answer on graphs that are **stars centred at the
source** — every non-source vertex has the source `V_0` as its sole neighbour.
Isolated vertices disconnected from `V_0` may also be present; they trivially
stay at `r_{t,i} = 0` for all `t`.

**Justification.** For any leaf `V_i ∈ N(V_0)`:

- `N(V_i) = {V_0}`, so the neighbour product reduces to a single factor.
- `r_{t-1, V_0} = 1` for all `t ≥ 1`, so that factor is `(1 − 1 · w_{0i}) = (1 − w_{0i})`.

The recurrence becomes

```
r_{t, V_i} = 1 − (1 − r_{t-1, V_i}) · (1 − w_{0i})
```

which unrolls to the exact closed form `r_{t, V_i} = 1 − (1 − w_{0i})^t` — the
probability that the source fails `t` independent daily transmission attempts
against `V_i`. Both failure modes identified in (a) are absent: there is no
cycle (the graph is a tree of depth one) and no back-flow (the only neighbour
each leaf sees is the source itself, whose risk is fixed at 1, so the
"independent neighbour" assumption is vacuously satisfied).

Note that the exact class is meaningfully narrower than "trees" or "acyclic
graphs": part (b) showed the recurrence is already approximate on the
three-vertex path `V_0 — V_1 — V_2`, which is itself a tree. Once any
non-source vertex has degree greater than one, back-flow becomes possible and
the independence assumption breaks.
