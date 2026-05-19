# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Visualisation utility for the disease outbreak simulation.
#
# __author__ = 'Edward Small'
# __project__ = 'Modelling a Disease Outbreak'
# __copyright__ = 'Copyright 2026, RMIT University'
# -------------------------------------------------

import math
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.patches import FancyArrowPatch

from graph.graph import Graph
from simulation.person import Person


# --------------------------------------------------
# Layout algorithms
# --------------------------------------------------

def _circle_layout(persons: list[Person]) -> dict[int, tuple[float, float]]:
    """
    Arranges nodes evenly around a circle.
    Best for small graphs (up to 15 nodes).

    @param persons: List of Person objects to position.
    @returns: A dictionary mapping person index to (x, y) position.
    """
    n = len(persons)
    positions = {}
    for i, person in enumerate(persons):
        angle = 2 * math.pi * i / n
        positions[person.index] = (math.cos(angle), math.sin(angle))
    return positions


def _grid_layout(persons: list[Person]) -> dict[int, tuple[float, float]]:
    """
    Arranges nodes in an evenly spaced grid.
    Best for medium graphs (16–50 nodes).

    @param persons: List of Person objects to position.
    @returns: A dictionary mapping person index to (x, y) position.
    """
    n = len(persons)
    cols = math.ceil(math.sqrt(n))
    positions = {}
    for i, person in enumerate(persons):
        row = i // cols
        col = i % cols
        positions[person.index] = (col / max(cols - 1, 1), -row / max(math.ceil(n / cols) - 1, 1))
    return positions


def _force_directed_layout(persons: list[Person],
                            graph: Graph,
                            iterations: int = 200) -> dict[int, tuple[float, float]]:
    """
    Computes a force-directed layout using a simple spring algorithm.
    Nodes repel each other and connected nodes attract each other.
    Best for large graphs (> 50 nodes).

    @param persons: List of Person objects to position.
    @param graph: The contact graph, used to determine edge connections.
    @param iterations: Number of simulation iterations. More iterations
                       produce a more stable layout at the cost of speed.
    @returns: A dictionary mapping person index to (x, y) position.
    """
    import random

    # Initialise positions randomly
    positions = {p.index: (random.uniform(-1, 1), random.uniform(-1, 1)) for p in persons}

    k = 1.0 / math.sqrt(len(persons))  # ideal spring length
    temperature = 1.0                   # controls max displacement per step

    for _ in range(iterations):
        displacement = {p.index: [0.0, 0.0] for p in persons}

        # Repulsive forces between all pairs
        for i, u in enumerate(persons):
            for v in persons[i + 1:]:
                dx = positions[u.index][0] - positions[v.index][0]
                dy = positions[u.index][1] - positions[v.index][1]
                dist = max(math.sqrt(dx ** 2 + dy ** 2), 0.001)
                force = k ** 2 / dist
                displacement[u.index][0] += (dx / dist) * force
                displacement[u.index][1] += (dy / dist) * force
                displacement[v.index][0] -= (dx / dist) * force
                displacement[v.index][1] -= (dy / dist) * force

        # Attractive forces along edges
        for u in persons:
            for neighbour, _ in graph.get_neighbours(u):
                dx = positions[u.index][0] - positions[neighbour.index][0]
                dy = positions[u.index][1] - positions[neighbour.index][1]
                dist = max(math.sqrt(dx ** 2 + dy ** 2), 0.001)
                force = dist ** 2 / k
                displacement[u.index][0] -= (dx / dist) * force
                displacement[u.index][1] -= (dy / dist) * force

        # Apply displacement with temperature clamping
        for p in persons:
            dx, dy = displacement[p.index]
            dist = max(math.sqrt(dx ** 2 + dy ** 2), 0.001)
            x, y = positions[p.index]
            positions[p.index] = (
                x + (dx / dist) * min(dist, temperature),
                y + (dy / dist) * min(dist, temperature)
            )

        temperature *= 0.95  # cool down

    # Normalise positions to [-1, 1]
    xs = [p[0] for p in positions.values()]
    ys = [p[1] for p in positions.values()]
    x_range = max(max(xs) - min(xs), 0.001)
    y_range = max(max(ys) - min(ys), 0.001)
    positions = {
        idx: (2 * (x - min(xs)) / x_range - 1, 2 * (y - min(ys)) / y_range - 1)
        for idx, (x, y) in positions.items()
    }
    return positions


def _choose_layout(persons: list[Person],
                   graph: Graph) -> dict[int, tuple[float, float]]:
    """
    Selects and applies the most appropriate layout algorithm based on
    the number of nodes in the graph.

    - Small  (≤ 15 nodes) : circle layout
    - Medium (16–50 nodes): grid layout
    - Large  (> 50 nodes) : force-directed layout

    @param persons: List of Person objects to position.
    @param graph: The contact graph.
    @returns: A dictionary mapping person index to (x, y) position.
    """
    n = len(persons)
    if n <= 15:
        return _circle_layout(persons)
    elif n <= 50:
        return _grid_layout(persons)
    else:
        return _force_directed_layout(persons, graph)


# --------------------------------------------------
# Network subplot (top left)
# --------------------------------------------------

def _get_axis_limits(positions: dict[int, tuple[float, float]], padding: float = 0.2) -> tuple[float, float, float, float]:
    """
    Computes axis limits from node positions with padding.

    @param positions: A dictionary mapping node index to (x, y) position.
    @param padding: Extra space around the outermost nodes.
    @returns: A tuple of (xmin, xmax, ymin, ymax).
    """
    xs = [x for x, y in positions.values()]
    ys = [y for x, y in positions.values()]
    return min(xs) - padding, max(xs) + padding, min(ys) - padding, max(ys) + padding


def _draw_network(ax: plt.Axes,
                  graph: Graph,
                  persons: list[Person],
                  patient_zero: Person,
                  positions: dict[int, tuple[float, float]]) -> None:
    """
    Draws the contact network on the given axes.

    Nodes are coloured by infection state (red = patient zero, grey scale
    by vulnerability for healthy residents). Edges are drawn with thickness
    and colour proportional to their transmission weight. Edge weight labels
    are shown only for small graphs (≤ 15 nodes).

    @param ax: The matplotlib Axes to draw on.
    @param graph: The contact graph.
    @param persons: List of all Person objects.
    @param patient_zero: The patient zero Person object.
    @param positions: A dictionary mapping person index to (x, y) position.
    @returns: None
    """
    show_labels = len(persons) <= 15
    norm = Normalize(vmin=0, vmax=1)
    cmap = plt.cm.YlOrRd

    # Draw edges
    drawn_edges = set()
    for person in persons:
        for neighbour, weight in graph.get_neighbours(person):
            edge_key = tuple(sorted((person.index, neighbour.index)))
            if edge_key in drawn_edges:
                continue
            drawn_edges.add(edge_key)

            x1, y1 = positions[person.index]
            x2, y2 = positions[neighbour.index]
            colour = cmap(norm(weight))
            lw = 1 + 3 * weight

            ax.plot([x1, x2], [y1, y2], color=colour, linewidth=lw, zorder=1, alpha=0.7)

            if show_labels:
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                ax.text(mx, my, f"{weight:.2f}", fontsize=6,
                        ha='center', va='center',
                        bbox=dict(boxstyle='round,pad=0.1', fc='white', alpha=0.6, ec='none'))

    # Draw nodes
    for person in persons:
        x, y = positions[person.index]
        if person.index == patient_zero.index:
            colour = '#e63946'
            edgecolour = '#9b1c2a'
        else:
            grey = 0.85 - 0.5 * person.vulnerability
            colour = (grey, grey, grey)
            edgecolour = '#444444'

        circle = plt.Circle((x, y), 0.06, color=colour, ec=edgecolour, lw=1.5, zorder=2)
        ax.add_patch(circle)

        label = f"P{person.index}"
        ax.text(x, y, label, fontsize=7, ha='center', va='center',
                fontweight='bold', color='white' if person.index == patient_zero.index else '#222222',
                zorder=3)

    # Colourbar for edge weights
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm, ax=ax, fraction=0.03, pad=0.04, label='Transmission probability')

    # Legend
    patient_patch = mpatches.Patch(color='#e63946', label='Patient zero')
    healthy_patch = mpatches.Patch(color='#aaaaaa', label='Healthy (darker = more vulnerable)')
    ax.legend(handles=[patient_patch, healthy_patch], loc='upper right', fontsize=7)

    # Set consistent axis limits
    xmin, xmax, ymin, ymax = _get_axis_limits(positions)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    ax.set_title('Contact Network', fontsize=11, fontweight='bold', pad=10)
    ax.set_aspect('equal')
    ax.axis('off')


# --------------------------------------------------
# Representation subplot (top right)
# --------------------------------------------------

def _draw_adjacency_list(ax: plt.Axes,
                         graph: Graph,
                         persons: list[Person],
                         patient_zero: Person) -> None:
    """
    Renders the adjacency list representation as a text-based diagram
    on the given axes, showing each vertex and its chain of neighbours.

    @param ax: The matplotlib Axes to draw on.
    @param graph: The contact graph.
    @param persons: List of all Person objects.
    @param patient_zero: The patient zero Person object.
    @returns: None
    """
    ax.set_title('Adjacency List', fontsize=11, fontweight='bold', pad=10)
    ax.axis('off')

    max_display = 20
    display_persons = persons[:max_display]
    truncated = len(persons) > max_display

    line_height = 1.0 / (len(display_persons) + 2)
    y = 1.0 - line_height

    for person in display_persons:
        neighbours = graph.get_neighbours(person)
        chain = ' -> '.join([f"(P{n.index}, {w:.2f})" for n, w in neighbours]) if neighbours else 'None'
        text = f"P{person.index} | {chain}"
        ax.text(0.02, y, text, fontsize=7, va='center',
                fontfamily='monospace', transform=ax.transAxes,
                color='#e63946' if person.state else '#222222')
        y -= line_height

    if truncated:
        ax.text(0.02, y, f"... ({len(persons) - max_display} more vertices not shown)",
                fontsize=7, va='center', fontfamily='monospace',
                color='#888888', transform=ax.transAxes)


def _draw_adjacency_matrix(ax: plt.Axes,
                            graph: Graph,
                            persons: list[Person]) -> None:
    """
    Renders the adjacency matrix representation as a heatmap on the
    given axes. Cell colour intensity reflects edge weight.
    Cell values are overlaid as text for small graphs (≤ 15 nodes).

    @param ax: The matplotlib Axes to draw on.
    @param graph: The contact graph.
    @param persons: List of all Person objects.
    @returns: None
    """
    ax.set_title('Adjacency Matrix', fontsize=11, fontweight='bold', pad=10)

    n = len(persons)
    matrix = [[graph.get_edge_weight(persons[i], persons[j]) for j in range(n)] for i in range(n)]

    im = ax.imshow(matrix, cmap='YlOrRd', vmin=0, vmax=1, aspect='auto')
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label='Transmission probability')

    labels = [f"P{p.index}" for p in persons]
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))

    x_labels = ax.set_xticklabels(labels, fontsize=7, rotation=45, ha='right')
    y_labels = ax.set_yticklabels(labels, fontsize=7)

    for i, person in enumerate(persons):
        colour = '#e63946' if person.state else 'black'
        x_labels[i].set_color(colour)
        y_labels[i].set_color(colour)

    if n <= 15:
        for i in range(n):
            for j in range(n):
                val = matrix[i][j]
                if val > 0:
                    ax.text(j, i, f"{val:.2f}", ha='center', va='center',
                            fontsize=6, color='black' if val < 0.6 else 'white')


# --------------------------------------------------
# Risk network subplot (middle left)
# --------------------------------------------------

def _draw_risk_network(ax: plt.Axes,
                       graph: Graph,
                       persons: list[Person],
                       patient_zero: Person,
                       positions: dict[int, tuple[float, float]],
                       risk_scores: list[float]) -> None:
    """
    Draws the contact network with nodes coloured by infection risk score
    r_{i,T}. Edges are drawn in plain grey — the focus is on node risk.
    Patient zero is shown in red. All other nodes are coloured on a
    yellow-to-dark-red scale by their risk score.

    @param ax: The matplotlib Axes to draw on.
    @param graph: The contact graph.
    @param persons: List of all Person objects.
    @param patient_zero: The patient zero Person object.
    @param positions: A dictionary mapping person index to (x, y) position.
    @param risk_scores: A list of floats where risk_scores[i] is the
                        infection risk for vertex V_i at day T.
    @returns: None
    """
    norm = Normalize(vmin=0, vmax=1)
    cmap = plt.cm.YlOrRd

    # Draw edges in plain grey
    drawn_edges = set()
    for person in persons:
        for neighbour, _ in graph.get_neighbours(person):
            edge_key = tuple(sorted((person.index, neighbour.index)))
            if edge_key in drawn_edges:
                continue
            drawn_edges.add(edge_key)
            x1, y1 = positions[person.index]
            x2, y2 = positions[neighbour.index]
            ax.plot([x1, x2], [y1, y2], color='#cccccc', linewidth=0.8,
                    zorder=1, alpha=0.6)

    # Draw nodes coloured by risk score
    for person in persons:
        x, y = positions[person.index]

        if person.index == patient_zero.index:
            colour = '#e63946'
            edgecolour = '#9b1c2a'
            text_colour = 'white'
        else:
            risk = risk_scores[person.index]
            colour = cmap(norm(risk))
            edgecolour = '#444444'
            text_colour = 'white' if risk > 0.5 else '#222222'

        circle = plt.Circle((x, y), 0.06, color=colour, ec=edgecolour,
                             lw=1.5, zorder=2)
        ax.add_patch(circle)

        ax.text(x, y, f"P{person.index}", fontsize=7, ha='center', va='center',
                fontweight='bold', color=text_colour, zorder=3)

    # Colourbar for risk scores
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm, ax=ax, fraction=0.03, pad=0.04, label='Infection risk r_{i,T}')

    # Legend
    patient_patch = mpatches.Patch(color='#e63946', label='Patient zero')
    risk_patch = mpatches.Patch(color='#c45c00', label='Residents (darker = higher risk)')
    ax.legend(handles=[patient_patch, risk_patch], loc='upper right', fontsize=7)

    # Set consistent axis limits
    xmin, xmax, ymin, ymax = _get_axis_limits(positions)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    ax.set_title('Infection Risk Network', fontsize=11, fontweight='bold', pad=10)
    ax.set_aspect('equal')
    ax.axis('off')


# --------------------------------------------------
# Risk table subplot (middle right) — full DP table
# --------------------------------------------------

def _draw_risk_table(ax: plt.Axes,
                     persons: list[Person],
                     patient_zero: Person,
                     risk_scores: list[float],
                     risk_table: list[list[float]] | None = None) -> None:
    """
    Renders the full infection risk table r_{i,t} as a heatmap if the
    full table is available and the graph is small enough. Falls back to
    a simple sorted text list for larger graphs.

    For small graphs (≤ 15 nodes) with a full table:
        Rows = vertices sorted by final risk descending
        Columns = days 0 to T
        Cells coloured yellow to dark red by risk value
        Cell values overlaid as text

    @param ax: The matplotlib Axes to draw on.
    @param persons: List of all Person objects.
    @param patient_zero: The patient zero Person object.
    @param risk_scores: Final column risk_scores[i] = r_{i,T}.
    @param risk_table: Full T+1 x n risk table, or None if unavailable.
    @returns: None
    """
    ax.set_title('Infection Risk Table r_{i,t}', fontsize=11, fontweight='bold', pad=10)

    show_full = risk_table is not None and len(persons) <= 15

    if show_full:
        T = len(risk_table) - 1
        n = len(persons)

        # Sort persons by final risk descending
        sorted_persons = sorted(persons, key=lambda p: risk_scores[p.index], reverse=True)

        # Build matrix: rows = persons, cols = days
        matrix = [[risk_table[t][p.index] for t in range(T + 1)] for p in sorted_persons]

        im = ax.imshow(matrix, cmap='YlOrRd', vmin=0, vmax=1, aspect='auto')
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label='Infection risk r_{i,t}')

        row_labels = [f"P{p.index}" for p in sorted_persons]
        col_labels = [f"t={t}" for t in range(T + 1)]
        ax.set_yticks(range(n))
        ax.set_xticks(range(T + 1))
        ax.set_yticklabels(row_labels, fontsize=7)
        ax.set_xticklabels(col_labels, fontsize=7, rotation=45, ha='right')

        # Colour patient zero label red
        for i, person in enumerate(sorted_persons):
            colour = '#e63946' if person.index == patient_zero.index else 'black'
            ax.get_yticklabels()[i].set_color(colour)

        # Overlay values
        for i in range(n):
            for t in range(T + 1):
                val = matrix[i][t]
                ax.text(t, i, f"{val:.2f}", ha='center', va='center',
                        fontsize=6, color='black' if val < 0.6 else 'white')

    else:
        # Fallback — simple text list sorted by risk descending
        ax.axis('off')
        eligible = [p for p in persons if p.index != patient_zero.index]
        eligible.sort(key=lambda p: risk_scores[p.index], reverse=True)

        max_display = 20
        display = eligible[:max_display]
        truncated = len(eligible) > max_display

        line_height = 1.0 / (len(display) + 3)
        y = 1.0 - line_height

        ax.text(0.02, y, f"{'Vertex':<10}  {'Risk r_{i,T}':>12}",
                fontsize=7, va='center', fontfamily='monospace',
                fontweight='bold', transform=ax.transAxes, color='#222222')
        y -= line_height * 0.6
        ax.plot([0.02, 0.98], [y, y], color='#cccccc', linewidth=0.8,
                transform=ax.transAxes)
        y -= line_height * 0.4

        for person in display:
            risk = risk_scores[person.index]
            row = f"P{person.index:<8}  {risk:>12.4f}"
            ax.text(0.02, y, row, fontsize=7, va='center',
                    fontfamily='monospace', transform=ax.transAxes,
                    color='#444444')
            y -= line_height

        if truncated:
            ax.text(0.02, y,
                    f"... ({len(eligible) - max_display} more residents not shown)",
                    fontsize=7, va='center', fontfamily='monospace',
                    color='#888888', transform=ax.transAxes)


# --------------------------------------------------
# Severed network subplot (bottom left)
# --------------------------------------------------

def _draw_severed_network(ax: plt.Axes,
                          graph: Graph,
                          persons: list[Person],
                          patient_zero: Person,
                          positions: dict[int, tuple[float, float]],
                          vaccinated: list[Person]) -> None:
    """
    Draws the contact network with vaccinated nodes highlighted in blue
    and their edges shown as dashed grey lines (severed). Nodes that are
    now unreachable from patient zero due to vaccination are shown in green
    (protected). Patient zero is shown in red.

    @param ax: The matplotlib Axes to draw on.
    @param graph: The contact graph.
    @param persons: List of all Person objects.
    @param patient_zero: The patient zero Person object.
    @param positions: A dictionary mapping person index to (x, y) position.
    @param vaccinated: List of Person objects who have been vaccinated.
    @returns: None
    """
    vaccinated_indices = {p.index for p in vaccinated}

    # Find nodes still reachable from patient zero after vaccination
    reachable = set()
    stack = [patient_zero.index]
    while stack:
        current = stack.pop()
        if current in reachable:
            continue
        reachable.add(current)
        for neighbour, _ in graph.get_neighbours(persons[current]):
            if neighbour.index not in vaccinated_indices and neighbour.index not in reachable:
                stack.append(neighbour.index)

    # Draw edges
    drawn_edges = set()
    for person in persons:
        for neighbour, weight in graph.get_neighbours(person):
            edge_key = tuple(sorted((person.index, neighbour.index)))
            if edge_key in drawn_edges:
                continue
            drawn_edges.add(edge_key)

            x1, y1 = positions[person.index]
            x2, y2 = positions[neighbour.index]

            if person.index in vaccinated_indices or neighbour.index in vaccinated_indices:
                ax.plot([x1, x2], [y1, y2], color='#cccccc', linewidth=1,
                        linestyle='--', zorder=1, alpha=0.5)
            else:
                ax.plot([x1, x2], [y1, y2], color='#457b9d', linewidth=1.5,
                        zorder=1, alpha=0.7)

    # Draw nodes
    for person in persons:
        x, y = positions[person.index]

        if person.index == patient_zero.index:
            colour = '#e63946'
            edgecolour = '#9b1c2a'
            text_colour = 'white'
        elif person.index in vaccinated_indices:
            colour = '#1d3557'
            edgecolour = '#0a1e36'
            text_colour = 'white'
        elif person.index not in reachable:
            colour = '#2dc653'
            edgecolour = '#1a7a33'
            text_colour = 'white'
        else:
            grey = 0.85 - 0.5 * person.vulnerability
            colour = (grey, grey, grey)
            edgecolour = '#444444'
            text_colour = '#222222'

        circle = plt.Circle((x, y), 0.06, color=colour, ec=edgecolour, lw=1.5, zorder=2)
        ax.add_patch(circle)

        ax.text(x, y, f"P{person.index}", fontsize=7, ha='center', va='center',
                fontweight='bold', color=text_colour, zorder=3)

    # Legend
    patient_patch = mpatches.Patch(color='#e63946', label='Patient zero')
    vaccinated_patch = mpatches.Patch(color='#1d3557', label='Vaccinated (edges severed)')
    protected_patch = mpatches.Patch(color='#2dc653', label='Protected (unreachable)')
    exposed_patch = mpatches.Patch(color='#aaaaaa', label='Still exposed')
    ax.legend(handles=[patient_patch, vaccinated_patch, protected_patch, exposed_patch],
              loc='upper right', fontsize=7)

    xmin, xmax, ymin, ymax = _get_axis_limits(positions)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    ax.set_title('Contact Network After Vaccination', fontsize=11, fontweight='bold', pad=10)
    ax.set_aspect('equal')
    ax.axis('off')


# --------------------------------------------------
# Vaccination DP table subplot (bottom right)
# --------------------------------------------------

def _draw_vaccination_summary(ax: plt.Axes,
                               vaccinated: list[Person],
                               eligible: list[Person],
                               total_doses: int) -> None:
    """
    Renders a text-based table summarising the vaccination program results.
    Shows each vaccinated person's dosage requirement and benefit score
    (infection risk), sorted by benefit descending. A summary row at the
    bottom shows total doses used and total benefit achieved.

    @param ax: The matplotlib Axes to draw on.
    @param vaccinated: List of vaccinated Person objects.
    @param eligible: Full list of eligible Person objects (unused, kept for interface consistency).
    @param total_doses: Total doses available (for summary).
    @returns: None
    """
    ax.set_title('Vaccination Program Summary', fontsize=11, fontweight='bold', pad=10)
    ax.axis('off')

    sorted_vaccinated = sorted(vaccinated, key=lambda p: p.benefit, reverse=True)
    total_benefit = sum(p.benefit for p in vaccinated)
    total_used = sum(p.dosage_requirement for p in vaccinated)

    max_display = 20
    display = sorted_vaccinated[:max_display]
    truncated = len(sorted_vaccinated) > max_display

    line_height = 1.0 / (min(len(display), max_display) + 5)
    y = 1.0 - line_height

    # Header
    ax.text(0.02, y, f"{'Vertex':<8} {'Dosage':<8} {'Benefit (Risk)':>14}",
            fontsize=7, va='center', fontfamily='monospace',
            fontweight='bold', transform=ax.transAxes, color='#222222')
    y -= line_height * 0.6
    ax.plot([0.02, 0.98], [y, y], color='#cccccc', linewidth=0.8, transform=ax.transAxes)
    y -= line_height * 0.4

    for person in display:
        row = f"P{person.index:<6}  {person.dosage_requirement:<8} {person.benefit:>14.4f}"
        ax.text(0.02, y, row, fontsize=7, va='center',
                fontfamily='monospace', transform=ax.transAxes,
                color='#1d3557')
        y -= line_height

    if truncated:
        ax.text(0.02, y, f"... ({len(sorted_vaccinated) - max_display} more not shown)",
                fontsize=7, va='center', fontfamily='monospace',
                color='#888888', transform=ax.transAxes)
        y -= line_height

    # Summary divider and totals
    y -= line_height * 0.5
    ax.plot([0.02, 0.98], [y, y], color='#cccccc', linewidth=0.8, transform=ax.transAxes)
    y -= line_height * 0.8
    ax.text(0.02, y, f"Total vaccinated : {len(vaccinated)}",
            fontsize=7, va='center', fontfamily='monospace',
            fontweight='bold', transform=ax.transAxes, color='#222222')
    y -= line_height
    ax.text(0.02, y, f"Total doses used : {total_used} / {total_doses}",
            fontsize=7, va='center', fontfamily='monospace',
            fontweight='bold', transform=ax.transAxes, color='#222222')
    y -= line_height
    ax.text(0.02, y, f"Total benefit    : {total_benefit:.4f}",
            fontsize=7, va='center', fontfamily='monospace',
            fontweight='bold', transform=ax.transAxes, color='#222222')


# --------------------------------------------------
# Main visualise function
# --------------------------------------------------

def visualise(graph: Graph,
              persons: list[Person],
              patient_zero: Person,
              graph_type: str,
              filename: str,
              risk_scores: list[float] | None = None,
              risk_table: list[list[float]] | None = None,
              vaccinated: list[Person] | None = None,
              eligible: list[Person] | None = None,
              total_doses: int = 0) -> None:
    """
    Produces a visualisation of the disease outbreak simulation and saves
    it as a PDF to the visuals/ folder.

    The layout adapts based on available data:
        1x2 grid — contact network + graph representation (always shown)
        2x2 grid — adds risk network + full risk table (if risk_scores provided)
        3x2 grid — adds severed network + vaccination summary (if vaccinated provided)

    @param graph: The contact graph.
    @param persons: List of all Person objects in the simulation.
    @param patient_zero: The patient zero Person object.
    @param graph_type: The graph representation type — 'list' or 'matrix'.
    @param filename: The filename (without extension) to save the visual as.
    @param risk_scores: Optional final column of risk scores r_{i,T}.
    @param risk_table: Optional full T+1 x n risk table for heatmap display.
    @param vaccinated: Optional list of vaccinated Person objects.
    @param eligible: Optional full list of eligible persons.
    @param total_doses: Total doses available.
    @returns: None
    """
    import os

    positions = _choose_layout(persons, graph)

    # Determine grid size based on available data
    if vaccinated is not None and risk_scores is not None:
        fig, axes = plt.subplots(3, 2, figsize=(22, 26))
        fig.subplots_adjust(hspace=0.35, wspace=0.3)
        ax_network  = axes[0][0]
        ax_repr     = axes[0][1]
        ax_risk     = axes[1][0]
        ax_risk_tbl = axes[1][1]
        ax_severed  = axes[2][0]
        ax_summary  = axes[2][1]
    elif risk_scores is not None:
        fig, axes = plt.subplots(2, 2, figsize=(22, 18))
        fig.subplots_adjust(hspace=0.35, wspace=0.3)
        ax_network  = axes[0][0]
        ax_repr     = axes[0][1]
        ax_risk     = axes[1][0]
        ax_risk_tbl = axes[1][1]
        ax_severed  = None
        ax_summary  = None
    else:
        fig, (ax_network, ax_repr) = plt.subplots(1, 2, figsize=(18, 9))
        fig.subplots_adjust(wspace=0.3)
        ax_risk     = None
        ax_risk_tbl = None
        ax_severed  = None
        ax_summary  = None

    fig.suptitle('Disease Outbreak — Metropolis Contact Network',
                 fontsize=14, fontweight='bold')

    # Row 1 — contact network and graph representation
    _draw_network(ax_network, graph, persons, patient_zero, positions)
    if graph_type == 'list':
        _draw_adjacency_list(ax_repr, graph, persons, patient_zero)
    else:
        _draw_adjacency_matrix(ax_repr, graph, persons)

    # Row 2 — risk network and full risk table
    if risk_scores is not None:
        _draw_risk_network(ax_risk, graph, persons, patient_zero, positions, risk_scores)
        _draw_risk_table(ax_risk_tbl, persons, patient_zero, risk_scores, risk_table)

    # Row 3 — severed network and vaccination summary
    if vaccinated is not None and risk_scores is not None:
        _draw_severed_network(ax_severed, graph, persons, patient_zero, positions, vaccinated)
        _draw_vaccination_summary(ax_summary, vaccinated, eligible or [], total_doses)

    plt.tight_layout(pad=2.0)

    # Save to visuals/ folder as PDF
    os.makedirs('visuals', exist_ok=True)
    filepath = os.path.join('visuals', f"{filename}.pdf")
    plt.savefig(filepath, bbox_inches='tight')
    print(f"      Visual saved to '{filepath}'.")
    plt.close()
