# -------------------------------------------------
# Task C — Empirical timing experiments.
#
# Generates runtime data for the four (algorithm, representation)
# combinations across varying n, |E|/density, T, and X, then plots
# the results. Output PNGs are written to visuals/task_c/.
#
# Not part of the submission deliverables — the report is what is
# marked. This script exists only to generate the report's plots.
# -------------------------------------------------

import csv
import os
import random
import statistics
from dataclasses import dataclass

import matplotlib.pyplot as plt

from graph.adjacency_list import AdjacencyList
from graph.adjacency_matrix import AdjacencyMatrix
from graph.vertex import Vertex
from transmission.monte_carlo import monte_carlo
from transmission.task_b import task_b
from utils.timer import start, stop


# --------------------------------------------------
# Output paths
# --------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "report", "figures")
os.makedirs(OUT_DIR, exist_ok=True)


# --------------------------------------------------
# Graph construction (deterministic, isolated from the
# global RNG so timing runs are reproducible).
# --------------------------------------------------
def make_graph(graph_type: str, n: int, m: int, seed: int,
               max_w: float = 0.05) -> tuple:
    """Builds either an AdjacencyList or AdjacencyMatrix with n
    vertices and exactly m random edges. Returns (graph, vertices).
    """
    g = AdjacencyList() if graph_type == "list" else AdjacencyMatrix()
    verts = [Vertex(i) for i in range(n)]
    for v in verts:
        g.add_vertex(v)

    rng = random.Random(seed)
    all_pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    max_m = len(all_pairs)
    if m > max_m:
        m = max_m
    selected = rng.sample(all_pairs, m)
    for i, j in selected:
        g.add_edge(verts[i], verts[j], rng.uniform(0.0002, max_w))
    return g, verts


# --------------------------------------------------
# Timed wrappers — return seconds, average over trials.
# Graph construction is NOT included in the measurement
# (matches the spec's tip).
# --------------------------------------------------
def time_dp(graph_type: str, n: int, m: int, T: int,
            trials: int = 3) -> float:
    times = []
    for k in range(trials):
        g, verts = make_graph(graph_type, n, m, seed=100 + k)
        t0 = start()
        task_b(g, verts[0], T)
        times.append(stop(t0))
    return statistics.mean(times)


def time_mc(graph_type: str, n: int, m: int, T: int, X: int,
            trials: int = 3) -> float:
    times = []
    for k in range(trials):
        g, verts = make_graph(graph_type, n, m, seed=100 + k)
        # Seed Python's global RNG so monte_carlo's random.random() is reproducible.
        random.seed(7 + k)
        t0 = start()
        monte_carlo(g, verts[0], T, X)
        times.append(stop(t0))
    return statistics.mean(times)


# --------------------------------------------------
# Experiments
# --------------------------------------------------
@dataclass
class Result:
    label: str
    xs: list
    ys: list


def experiment_vary_n(T: int = 8, X: int = 50, density: float = 0.3,
                      ns: tuple = (10, 20, 40, 60, 80, 120)) -> list:
    """Vary number of vertices, fix density and (T, X)."""
    print(f"\n=== Experiment 1: vary n (density={density}, T={T}, X={X}) ===")
    results = {label: ([], []) for label in
               ["DP-list", "DP-matrix", "MC-list", "MC-matrix"]}
    for n in ns:
        m = max(1, int(density * n * (n - 1) / 2))
        print(f"  n={n:>4}  m={m:>5}  ", end="", flush=True)
        for label, fn in [
            ("DP-list",   lambda: time_dp("list",   n, m, T)),
            ("DP-matrix", lambda: time_dp("matrix", n, m, T)),
            ("MC-list",   lambda: time_mc("list",   n, m, T, X)),
            ("MC-matrix", lambda: time_mc("matrix", n, m, T, X)),
        ]:
            t = fn()
            results[label][0].append(n)
            results[label][1].append(t)
            print(f"{label}={t*1000:.2f}ms  ", end="", flush=True)
        print()
    return [Result(label, xs, ys) for label, (xs, ys) in results.items()]


def experiment_vary_T(n: int = 60, X: int = 50, density: float = 0.3,
                      Ts: tuple = (2, 5, 10, 20, 40)) -> list:
    """Vary horizon T, fix everything else."""
    m = max(1, int(density * n * (n - 1) / 2))
    print(f"\n=== Experiment 2: vary T (n={n}, m={m}, X={X}) ===")
    results = {label: ([], []) for label in
               ["DP-list", "DP-matrix", "MC-list", "MC-matrix"]}
    for T in Ts:
        print(f"  T={T:>3}  ", end="", flush=True)
        for label, fn in [
            ("DP-list",   lambda: time_dp("list",   n, m, T)),
            ("DP-matrix", lambda: time_dp("matrix", n, m, T)),
            ("MC-list",   lambda: time_mc("list",   n, m, T, X)),
            ("MC-matrix", lambda: time_mc("matrix", n, m, T, X)),
        ]:
            t = fn()
            results[label][0].append(T)
            results[label][1].append(t)
            print(f"{label}={t*1000:.2f}ms  ", end="", flush=True)
        print()
    return [Result(label, xs, ys) for label, (xs, ys) in results.items()]


def experiment_vary_density(n: int = 60, T: int = 8, X: int = 50,
                            densities: tuple = (0.05, 0.1, 0.2, 0.4, 0.8)) -> list:
    """Vary edge density, fix n, T, X. Highlights list vs matrix."""
    print(f"\n=== Experiment 3: vary density (n={n}, T={T}, X={X}) ===")
    results = {label: ([], []) for label in
               ["DP-list", "DP-matrix", "MC-list", "MC-matrix"]}
    for d in densities:
        m = max(1, int(d * n * (n - 1) / 2))
        print(f"  d={d:.2f}  m={m:>5}  ", end="", flush=True)
        for label, fn in [
            ("DP-list",   lambda: time_dp("list",   n, m, T)),
            ("DP-matrix", lambda: time_dp("matrix", n, m, T)),
            ("MC-list",   lambda: time_mc("list",   n, m, T, X)),
            ("MC-matrix", lambda: time_mc("matrix", n, m, T, X)),
        ]:
            t = fn()
            results[label][0].append(d)
            results[label][1].append(t)
            print(f"{label}={t*1000:.2f}ms  ", end="", flush=True)
        print()
    return [Result(label, xs, ys) for label, (xs, ys) in results.items()]


def experiment_vary_X(n: int = 60, T: int = 8, density: float = 0.3,
                      Xs: tuple = (10, 30, 100, 300, 1000)) -> list:
    """Vary MC sample count X. DP doesn't depend on X — shown as
    a constant horizontal reference."""
    m = max(1, int(density * n * (n - 1) / 2))
    print(f"\n=== Experiment 4: vary X (n={n}, m={m}, T={T}) ===")
    # DP is X-independent, time once per representation
    dp_list_t   = time_dp("list",   n, m, T)
    dp_matrix_t = time_dp("matrix", n, m, T)
    print(f"  DP-list  ref={dp_list_t*1000:.2f}ms   "
          f"DP-matrix ref={dp_matrix_t*1000:.2f}ms")

    results = {
        "MC-list":   ([], []),
        "MC-matrix": ([], []),
        "DP-list":   ([], []),
        "DP-matrix": ([], []),
    }
    for X in Xs:
        print(f"  X={X:>5}  ", end="", flush=True)
        for label, fn in [
            ("MC-list",   lambda: time_mc("list",   n, m, T, X)),
            ("MC-matrix", lambda: time_mc("matrix", n, m, T, X)),
        ]:
            t = fn()
            results[label][0].append(X)
            results[label][1].append(t)
            print(f"{label}={t*1000:.2f}ms  ", end="", flush=True)
        results["DP-list"][0].append(X);   results["DP-list"][1].append(dp_list_t)
        results["DP-matrix"][0].append(X); results["DP-matrix"][1].append(dp_matrix_t)
        print()
    return [Result(label, xs, ys) for label, (xs, ys) in results.items()]


# --------------------------------------------------
# Plotting
# --------------------------------------------------
STYLES = {
    "DP-list":   dict(marker="o", linestyle="-",  color="#1f77b4"),
    "DP-matrix": dict(marker="s", linestyle="-",  color="#ff7f0e"),
    "MC-list":   dict(marker="^", linestyle="--", color="#2ca02c"),
    "MC-matrix": dict(marker="D", linestyle="--", color="#d62728"),
}


def plot(results, xlabel: str, title: str, filename: str,
         logx: bool = False, logy: bool = True) -> str:
    plt.figure(figsize=(6.5, 4.5))
    for r in results:
        plt.plot(r.xs, r.ys, label=r.label, **STYLES[r.label])
    plt.xlabel(xlabel)
    plt.ylabel("Mean runtime (s)")
    plt.title(title)
    if logx: plt.xscale("log")
    if logy: plt.yscale("log")
    plt.grid(True, which="both", linestyle=":", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    path = os.path.join(OUT_DIR, filename)
    plt.savefig(path, dpi=130)
    plt.close()
    return path


# --------------------------------------------------
# CSV dump — handy for the report appendix and for
# re-plotting without re-running experiments.
# --------------------------------------------------
def dump_csv(results, xlabel: str, filename: str) -> str:
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([xlabel] + [r.label for r in results])
        if results:
            for i, x in enumerate(results[0].xs):
                writer.writerow([x] + [r.ys[i] for r in results])
    return path


# --------------------------------------------------
# Main
# --------------------------------------------------
def plot_grid(results_list, configs, filename: str) -> str:
    """Render four experiments as a 2x2 grid in one figure."""
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    for ax, (results, cfg) in zip(axes.flat, zip(results_list, configs)):
        xlabel, title, logx, logy = cfg
        for r in results:
            ax.plot(r.xs, r.ys, label=r.label, markersize=5, **STYLES[r.label])
        ax.set_xlabel(xlabel, fontsize=9)
        ax.set_ylabel("Runtime (s)", fontsize=9)
        ax.set_title(title, fontsize=10)
        if logx: ax.set_xscale("log")
        if logy: ax.set_yscale("log")
        ax.grid(True, which="both", linestyle=":", alpha=0.5)
        ax.tick_params(labelsize=8)
    axes[0, 0].legend(fontsize=8, loc="lower right")
    plt.tight_layout()
    path = os.path.join(OUT_DIR, filename)
    plt.savefig(path, dpi=140)
    plt.close()
    return path


if __name__ == "__main__":
    r1 = experiment_vary_n()
    dump_csv(r1, "n", "exp1_vary_n.csv")
    plot(r1, "Number of residents (n)",
         "Runtime vs n  (density=0.30, T=8, X=50)",
         "exp1_vary_n.png", logx=True, logy=True)

    r2 = experiment_vary_T()
    dump_csv(r2, "T", "exp2_vary_T.csv")
    plot(r2, "Planning horizon T (days)",
         "Runtime vs T  (n=60, density=0.30, X=50)",
         "exp2_vary_T.png", logx=False, logy=True)

    r3 = experiment_vary_density()
    dump_csv(r3, "density", "exp3_vary_density.csv")
    plot(r3, "Edge density  m / (n choose 2)",
         "Runtime vs density  (n=60, T=8, X=50)",
         "exp3_vary_density.png", logx=False, logy=True)

    r4 = experiment_vary_X()
    dump_csv(r4, "X", "exp4_vary_X.csv")
    plot(r4, "Monte Carlo simulations X",
         "Runtime vs X  (n=60, density=0.30, T=8)",
         "exp4_vary_X.png", logx=True, logy=True)

    # Combined 2x2 figure for the 2-page report.
    plot_grid(
        [r1, r2, r3, r4],
        [
            ("n",       "(a) vs n   (d=0.3, T=8, X=50)",       True,  True),
            ("T",       "(b) vs T   (n=60, d=0.3, X=50)",      False, True),
            ("density", "(c) vs density   (n=60, T=8, X=50)",  False, True),
            ("X",       "(d) vs X   (n=60, d=0.3, T=8)",       True,  True),
        ],
        "task_c_combined.png",
    )

    print(f"\nAll plots written to {OUT_DIR}")
