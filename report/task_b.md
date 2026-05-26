# Task B — Infection Risk DP (Report, 1 page)

## 1. Pseudo-code (1 mark)

```
Algorithm  TaskB(G, s, T)
Require:   Graph G = (V, E); source s; horizon T
Ensure:    Risk table where table[t][i] = r_{t,i}

 1: table ← (T + 1) × |V| array initialised to 0.0
 2: table[0][s.index] ← 1.0                       // base case: only s is infected
 3: for each day t = 1 to T do
 4:     prev ← table[t − 1];  curr ← table[t]
 5:     for each vertex V_i ∈ V do
 6:         escape ← 1 − prev[i]
 7:         for each neighbour V_j of V_i do
 8:             escape ← escape · (1 − prev[j] · w_{ij})
 9:         curr[i] ← 1 − escape
10:     curr[s.index] ← 1.0     // pin patient zero (recurrence preserves it; defensive)
11: return table
```

## 2. Limitations of the recurrence (3 marks)

**(a) Structural property.** *Intuitively, the recurrence double-counts certain infection scenarios because it treats each neighbour as an independent source of infection when in fact those neighbours often share the same upstream cause — or, in undirected graphs, are themselves infected only through V<sub>i</sub>.* Formally, the neighbour product treats the events "*V*<sub>j</sub> is infected by *t* − 1" as **mutually independent across all *j* ∈ *N*(*V*<sub>i</sub>)**. That independence fails on any non-trivial graph through *(i)* shared upstream paths — different routes from the source to two neighbours of *V*<sub>i</sub> share infection events that get double-counted — and *(ii)* undirected back-flow — a downstream neighbour *V*<sub>j</sub> of *V*<sub>i</sub> can only have been infected *via* *V*<sub>i</sub>, yet appears in *V*<sub>i</sub>'s product as if it were an independent infector. Exact computation would need the full joint over 2<sup>|V|</sup> infection states; the recurrence trades that for polynomial cost by factorising into marginals.

**(b) Figure 5, *V*<sub>1</sub> at *t* = 3.** On the chain *V*<sub>0</sub> — *V*<sub>1</sub> — *V*<sub>2</sub> with *w*<sub>01</sub> = 0.8, *w*<sub>12</sub> = 0.6, the recurrence yields *r*<sub>3,V1</sub> = 1 − (1 − 0.96)(1 − 1.0·0.8)(1 − 0.48·0.6) = 1 − 0.04·0.2·**0.712** = **0.9943** *(the approximation the recurrence reports)*. The true risk is 1 − (1 − 0.8)<sup>3</sup> = **0.992** *(the exact probability that V<sub>1</sub> is infected by day 3, obtained from the closed-form single-edge cascade)*, because *V*<sub>2</sub> was infected *only* through *V*<sub>1</sub>, so any "back-transmission" *V*<sub>2</sub> → *V*<sub>1</sub> happens only in scenarios where *V*<sub>1</sub> is already infected. The offending term **(1 − *r*<sub>2,V2</sub> · *w*<sub>12</sub>) = 0.712** acts as if *V*<sub>2</sub> could infect *V*<sub>1</sub> via paths that don't actually exist in the true process — *V*<sub>2</sub>'s 0.48 probability mass was *generated* by *V*<sub>1</sub> at *t* = 1, so it cannot independently re-infect *V*<sub>1</sub>. This spuriously shrinks the escape product and so **over-estimates** the risk by 0.0023 absolute (0.9943 vs 0.992).

**(c) Exact class.** The recurrence is exact on **stars centred at the source** (every non-source vertex has *V*<sub>0</sub> as its sole neighbour; isolated vertices may also be present). On such a graph each leaf's product collapses to a single factor (1 − 1 · *w*<sub>0i</sub>) = (1 − *w*<sub>0i</sub>), and the recurrence unrolls to the exact closed form *r*<sub>t,Vi</sub> = 1 − (1 − *w*<sub>0i</sub>)<sup>t</sup> — the probability of failing *t* independent daily transmission attempts. Both failure modes from (a) are absent: no cycle, and no back-flow (the only neighbour each leaf sees is the source itself, whose risk is fixed at 1). The class is strictly narrower than "trees": (b) showed the recurrence is already approximate on the three-vertex path, which is itself a tree, so once any non-source vertex has degree > 1 back-flow becomes possible and the assumption breaks.

\newpage
