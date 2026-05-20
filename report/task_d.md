# Task D — Antiviral Allocation (Report, 2 pages)

Let *n* = eligible residents, *C* = total dose budget, *c*<sub>i</sub> = dose requirement, *b*<sub>i</sub> = *r*<sub>i,T</sub> = infection-risk benefit.

## 1. Algorithm Design (1 mark)

0/1 knapsack with real-valued benefits and a fewest-doses tiebreak, solved by **top-down memoisation**. A 2-D memo of size (*n* + 1) × (*C* + 1) stores per cell `memo[i][c] = (best_benefit, min_doses_to_achieve_best_benefit)` — the tuple captures the tiebreak inside the cell so no second pass is needed.

**Base cases.** `solve(0, c) = solve(i, 0) = (0.0, 0)`.

**Recurrence.** For *i* ≥ 1, *c* ≥ 1:

```
skip = solve(i − 1, c)                          # don't vaccinate person i
take = solve(i − 1, c − c_i) + (b_i, c_i)       # if c_i ≤ c
memo[i][c] = take  if  take.benefit > skip.benefit              (strictly better)
                       OR (take.benefit == skip.benefit AND take.doses < skip.doses)
             else skip
```

Plain lexicographic max of (benefit, −doses). Float tolerance 1e−12 — benefits are probabilities in [0, 1] with sums below *n*, well above double-precision rounding noise.

**Top-down (not bottom-up):** memoising only the cells reached from (*n*, *C*) is far fewer than *nC* on instances with large per-person costs (Case 6 test rewards this).

**Backtracking.** Walk *i* from *n* down to 1, replaying the same skip-vs-take comparison through `solve()` (not raw memo lookups) and deducting *c*<sub>i</sub> from a running capacity whenever take wins. Routing through `solve()` keeps the *i* = 0 / *c* = 0 base cases uniform without indexing into unmemoised cells.

## 2. Complexity (1 mark)

**Time O(*nC*)**, **space O(*nC*)**. At most *nC* unique (*i*, *c*) cells, each O(1) work plus two memoised recursive calls. Backtracking adds O(*n*); recursion stack adds O(*n*). Pseudo-polynomial: linear in *C* but independent of how large individual *c*<sub>i</sub> are. Exponentially faster than brute force's O(2<sup>*n*</sup>) whenever *C* < 2<sup>*n*</sup>/*n* — always true for realistic intervention budgets.

## 3. Extension 1 — Triage by *K* vulnerability tiers (2 marks)

Partition residents into tiers *T*<sub>1</sub> (most vulnerable) … *T*<sub>K</sub> (least). *T*<sub>k</sub> must be allocated optimally before any dose is spent on *T*<sub>k+1</sub>.

**Modification.** Run the same DP *K* times in cascade, threading the remaining capacity through:

```
remaining = C;  selected = []
for k = 1 to K do
    subset_k, _, used_k, _ = task_d(T_k, remaining)
    selected += subset_k;  remaining -= used_k
return selected
```

**Complexity.** Each call is O(|*T*<sub>k</sub>| · *C*) in the worst case. Summing: O((|*T*<sub>1</sub>| + … + |*T*<sub>K</sub>|) · *C*) = **O(*nC*)** — same class as the un-triaged DP (the extra *K* is hidden in constants because per-tier capacity strictly decreases).

**Counterexample — why ignoring vulnerability hurts.** *C* = 4 with three residents:

| Resident | Tier | *b* | *c* |
|---|---|---|---|
| *V*<sub>A</sub> | 1 (highly vulnerable — would die if infected) | 0.50 | 4 |
| *V*<sub>B</sub> | 2 (low vulnerability) | 0.60 | 2 |
| *V*<sub>C</sub> | 2 (low vulnerability) | 0.55 | 2 |

Plain knapsack picks {*V*<sub>B</sub>, *V*<sub>C</sub>}: benefit 1.15, 4 doses, **V<sub>A</sub> left unprotected**. Triaged DP picks *V*<sub>A</sub> first (only feasible tier-1 choice): benefit 0.50, 4 doses, tier 2 receives nothing. The plain knapsack has higher aggregate *r*<sub>T</sub>-benefit yet leaves the only resident who would die exposed — triage restores clinical priority at the cost of some aggregate risk-reduction, exactly the trade-off the model should make explicit.

## 4. Extension 2 — Interdependent vaccinations (2 marks)

**Why independence is required for the DP.** The DP's optimal substructure relies on the marginal contribution of vaccinating *i* being a constant *b*<sub>i</sub>, regardless of who else is in the subset. That is what lets `memo[i][c]` be a function of (*i*, *c*) alone. If *b*<sub>i</sub> depends on who else was vaccinated, different partial solutions reaching the same (*i*, *c*) state would credit person *i* with different benefits later, so the "best" cell value depends on history rather than state.

**Counterexample.** Contact chain *V*<sub>0</sub> → *V*<sub>1</sub> → *V*<sub>2</sub> with high weights and *r*<sub>1,T</sub> = *r*<sub>2,T</sub> = 0.95. Assume vaccinating a resident drops every neighbour's *r*<sub>T</sub> to ≈ 0 (the neighbour's only exposure pathway is blocked). Costs *c*<sub>V1</sub> = *c*<sub>V2</sub> = 1, budget *C* = 1.

- DP sees benefits (0.95, 0.95) and costs (1, 1) — either choice equal → reports benefit 0.95.
- True benefit of vaccinating *V*<sub>1</sub>: *V*<sub>1</sub> protected (0.95) **and** *V*<sub>2</sub>'s residual risk → 0 (saving another 0.95) → true total ≈ **1.90**.
- True benefit of vaccinating *V*<sub>2</sub>: *V*<sub>2</sub> alone protected; *V*<sub>1</sub> stays at 0.95 → true total ≈ **0.95**.

Vaccinating *V*<sub>1</sub> is twice as good as *V*<sub>2</sub>, yet the independent-benefit DP treats them as tied because it cannot see the herd-effect interaction.

**Why the true problem is significantly harder.** The benefit becomes a set function *B*(*S*) — each evaluation requires re-running the Task B risk DP on the residual graph induced by *S*. Consequences: *(i)* `memo[i][c]` no longer captures enough state — optimal substructure would need to encode the entire vaccinated subset so far (2<sup>n</sup> states); *(ii)* per-evaluation cost balloons (one Task B re-run, O(*Tm*) each), giving brute force O(2<sup>*n*</sup> · *Tm*); *(iii)* under the independent-cascade model used here *B* is monotone non-decreasing and submodular, so the problem is exactly **submodular maximisation under a knapsack constraint** — NP-hard, with a tight (1 − 1/*e*) ≈ 0.632 greedy approximation and no polynomial-time exact algorithm unless P = NP. The independent-benefit knapsack we solve is therefore a *relaxation*: cheap and exact within its abstraction, blind to the herd-effect amplification that drives most of the real-world value of vaccination.
