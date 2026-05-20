# Task D — Antiviral Allocation (Report, max 2 pages)

Let *n* be the number of eligible residents, *C* the total dose
budget, *c*<sub>i</sub> resident *i*'s dose requirement and
*b*<sub>i</sub> = *r*<sub>i,T</sub> their infection-risk benefit.

## 1. Algorithm Design (1 mark)

The problem is **0/1 knapsack with real-valued benefits and a
fewest-doses tiebreak**, solved by top-down dynamic programming.

**Table.** A 2-D memo of size (*n*+1) × (*C*+1) where each cell stores
a pair:

> `memo[i][c] = (best_benefit, min_doses_to_achieve_best_benefit)`

`memo[i][c]` answers: *what is the best (benefit, doses) attainable
using the first *i* eligible residents under a remaining capacity of
*c**?* The tuple form captures the tiebreak inside the cell, so the
recurrence never needs a second pass to break ties.

**Base cases.** `solve(0, c) = solve(i, 0) = (0.0, 0)` — with no
residents left or no capacity left, no doses are given and no benefit
is earned.

**Recurrence.** For each `(i, c)` with `i ≥ 1` and `c ≥ 1`:

```
skip = solve(i − 1, c)                               # don't vaccinate person i
take = solve(i − 1, c − c_i) + (b_i, c_i)            # if c_i ≤ c
memo[i][c] = take  if  take.benefit  >  skip.benefit                 (strictly better)
             OR  (take.benefit == skip.benefit  AND  take.doses < skip.doses)
             else skip
```

This is plain lexicographic max of (benefit, −doses). Floating-point
comparisons use a 1e−12 tolerance — benefits are probabilities in [0,1]
and sums stay well below *n*, so double-precision rounding is bounded
several orders of magnitude below the tolerance.

**Top-down (not bottom-up).** I memoise only the `(i, c)` cells
actually reached from `(n, C)`. On instances where per-person costs
are large, this is far fewer than the *nC* cells a bottom-up fill
would touch — which the Case 6 unit test rewards explicitly.

**Backtracking.** After `solve(n, C)`, walk *i* from *n* down to 1 and
**replay the same skip-vs-take comparison** on the cached cells,
deducting *c*<sub>i</sub> from a running capacity whenever the
take-branch wins. Routing all lookups through `solve()` keeps the
*i* = 0 / *c* = 0 base cases uniform without ever indexing into
unmemoised cells.

## 2. Complexity (1 mark)

| Resource | Bound | Where it comes from |
|---|---|---|
| Time      | **O(*nC*)** | At most *nC* unique `(i, c)` cells (1 per memo slot); each does O(1) work plus two recursive calls that are themselves O(1) due to memoisation. Backtracking is an additional O(*n*). |
| Space     | **O(*nC*)** | The memo dominates; the recursion stack adds O(*n*). |

This is **pseudo-polynomial**: linear in the dose budget *C* but
independent of how large the individual *c*<sub>i</sub> happen to be.
Compared to brute force's O(2<sup>*n*</sup>), the DP is exponentially
faster in *n* whenever *C* < 2<sup>*n*</sup>/*n*, which holds for any
realistic intervention budget.

## 3. Extension 1 — Triage by *K* vulnerability tiers (2 marks)

**Setup.** Partition the eligible residents into *K* tiers,
*T*<sub>1</sub> (most vulnerable) … *T*<sub>K</sub> (least). Tier
*T*<sub>k</sub> must be allocated optimally before any dose is spent
on tier *T*<sub>k+1</sub>.

**Modification.** Run the same DP *K* times in cascade, threading the
remaining capacity through each tier:

```
remaining ← C
for k = 1 to K do
    subset_k, benefit_k, used_k, _ ← task_d(T_k, remaining)
    remaining ← remaining − used_k
return ⋃ subset_k
```

Each call uses the unchanged single-tier DP above; only the input
list and capacity differ.

**Complexity.** Each call is O(|*T*<sub>k</sub>| · *C*) in the worst
case (remaining ≤ *C*). Summing,

> O((|*T*<sub>1</sub>| + … + |*T*<sub>K</sub>|) · *C*) = **O(*nC*)**

— same asymptotic class as the un-triaged DP. The extra *K* factor is
hidden in constants because the per-tier capacity strictly decreases.

**Counterexample — why ignoring vulnerability is dangerous.**
Consider C = 4 and three eligible residents:

| Resident | Tier | Benefit *b* | Cost *c* |
|---|---|---|---|
| V<sub>A</sub> | 1 (highly vulnerable — would die if infected) | 0.50 | 4 |
| V<sub>B</sub> | 2 (low vulnerability) | 0.60 | 2 |
| V<sub>C</sub> | 2 (low vulnerability) | 0.55 | 2 |

- **Plain knapsack** picks {V<sub>B</sub>, V<sub>C</sub>}: total
  benefit 1.15, all 4 doses used, **V<sub>A</sub> left unprotected**.
- **Triaged DP** picks V<sub>A</sub> first (only feasible tier-1
  choice): benefit 0.50, 4 doses used; tier 2 receives nothing.

The plain knapsack has higher aggregate *r*<sub>T</sub>-benefit, yet
it leaves the only resident who would die if infected exposed. Triage
restores clinical priority at the cost of some aggregate infection
risk — exactly the trade-off the model should make explicit.

## 4. Extension 2 — Interdependent vaccinations (2 marks)

**Why independence is needed for the DP to be valid.** The DP's
optimal substructure relies on the marginal contribution of
vaccinating person *i* being a **constant** *b*<sub>i</sub>, regardless
of who else is in the chosen subset. That is what lets us define
`memo[i][c]` as a function of *(i, c)* alone. If *b*<sub>i</sub>
depends on which *other* residents are vaccinated, then the value of
the subproblem "first *i* residents, capacity *c*" is no longer
well-defined — different partial solutions reaching the same `(i, c)`
state would credit person *i* with different benefits later, so the
"best" cell value depends on its history, not just its state.

**Counterexample.** Consider the contact chain V<sub>0</sub> →
V<sub>1</sub> → V<sub>2</sub> with high transmission weights and
*r*<sub>1,T</sub> = *r*<sub>2,T</sub> = 0.95. Assume vaccinating a
resident drops every neighbour's *r*<sub>T</sub> to roughly 0 (the
neighbour's only exposure pathway is now blocked). Costs:
*c*<sub>V1</sub> = *c*<sub>V2</sub> = 1. Budget *C* = 1.

- **The DP** sees benefits (0.95, 0.95) and costs (1, 1) and either
  choice is equally good — reported benefit 0.95.
- **True benefit of vaccinating V<sub>1</sub>:** V<sub>1</sub> is
  protected (0.95) *and* V<sub>2</sub>'s residual risk collapses to ≈ 0
  (saving another 0.95) → **true total ≈ 1.90**.
- **True benefit of vaccinating V<sub>2</sub>:** V<sub>2</sub> alone
  is protected; V<sub>1</sub> stays at 0.95 → **true total ≈ 0.95**.

The DP cannot tell these two options apart because it does not see the
herd-effect interaction. Vaccinating V<sub>1</sub> is twice as good as
vaccinating V<sub>2</sub>, yet under the independent-benefit
abstraction they are tied.

**Why the true problem is significantly harder.** The benefit
function `B(S) = Σ_{i ∉ S} r_{i,T}^{vaccinated S}` is a **set
function**, not a sum of per-element terms — each call requires
re-running the Task B risk DP on the residual graph induced by *S*. So:

1. **State explodes.** `memo[i][c]` no longer captures enough. To
   recover optimal substructure, the state would need to encode the
   *entire vaccinated subset so far*, giving 2<sup>*n*</sup> states.
2. **Per-evaluation cost balloons.** Evaluating any candidate subset
   requires an O(*Tm*) Task B run on the modified graph, so brute-force
   becomes O(2<sup>*n*</sup> · *Tm*).
3. **Theoretical hardness.** The set function is monotone non-decreasing
   and (under the independent-cascade model used here) submodular, so
   the problem is exactly **submodular maximisation under a knapsack
   constraint** — known to be NP-hard, with a tight (1 − 1/e) ≈ 0.632
   approximation achievable by greedy and no polynomial-time exact
   algorithm unless P = NP.

The independent-benefit knapsack we solve is therefore a
*relaxation*: cheap and exact within its abstraction, but blind to
the herd-effect amplification that drives most of the real-world
value of vaccination.
