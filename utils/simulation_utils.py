# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Utility functions for the disease outbreak simulation.
#
# __author__ = 'Edward Small'
# __project__ = 'Modelling a Disease Outbreak'
# __copyright__ = 'Copyright 2026, RMIT University'
# -------------------------------------------------

import json
import sys

from simulation.city import City
from simulation.person import Person
from graph.graph import Graph
from utils.config_validator import validate_config


def print_banner() -> None:
    """
    Prints the simulation banner to the console.

    @returns: None
    """
    print("==========================================")
    print("   Graph Algorithms in Action")
    print("   Modelling a Disease Outbreak")
    print("   COSC2123/3119 — RMIT University")
    print("==========================================")
    print()


def load_config(config_path: str) -> dict:
    """
    Loads and parses a JSON config file from the given path.

    @param config_path: Path to the JSON config file.
    @returns: A dictionary containing the config parameters.
    """
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Config file not found: '{config_path}'")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Could not parse config file: {e}")
        sys.exit(1)


def setup(config_path: str) -> dict:
    """
    Loads, parses, and validates the simulation config file.
    Exits with a clear error message if the config is invalid.

    @param config_path: Path to the JSON config file.
    @returns: A validated configuration dictionary.
    """
    print_banner()
    print(f"[1] Reading config from '{config_path}'...")
    config = load_config(config_path)

    errors = validate_config(config)
    if errors:
        print("\n[ERROR] Invalid config file. Please fix the following:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("      Config loaded and validated successfully.")
    print()
    return config


def build_city(config: dict) -> tuple[City, Graph, list[Person], Person]:
    """
    Builds the contact graph from the config parameters.
    Creates Person objects, generates edges, and assigns patient zero.

    @param config: The validated simulation config dictionary.
    @returns: A tuple of (city, graph, persons, patient_zero).
    """
    print(f"[2] Building contact graph...")
    print(f"      Graph type           : {config['graph_type']}")
    print(f"      Residents            : {config['num_residents']}")
    print(f"      Edges                : {config['num_edges']}")
    print(f"      Max transmission prob: {config['max_transmission_prob']}")
    print(f"      Seed                 : {config['seed']}")
    print()

    city = City(
        seed=config['seed'],
        num_residents=config['num_residents'],
        num_edges=config['num_edges'],
        max_transmission_prob=config['max_transmission_prob'],
        vulnerability_range=tuple(config['vulnerability_range']),
        dosage_range=tuple(config['dosage_range']),
        graph_type=config['graph_type']
    )

    graph = city.get_graph()
    persons = city.get_persons()
    patient_zero = city.get_patient_zero()

    print(f"      Graph built successfully.")
    print(f"      Vertices    : {graph.num_vertices()}")
    print(f"      Edges       : {graph.num_edges()}")
    print(f"      Patient zero: {patient_zero}")
    print()

    if config['print_struct']:
        print("      Graph structure:")
        print()
        print(graph)
        print()

    return city, graph, persons, patient_zero


def run_risk_solver(config: dict,
                    graph: Graph,
                    patient_zero: Person,
                    persons: list[Person]) -> tuple[list[float] | None, list[list[float]] | None]:
    """
    Runs the selected risk solver to compute infection risk r_{i,T}
    for every resident at day T. Updates each person's probability
    of infection (and benefit score) from the results.

    Returns (None, None) if the selected solver is not yet implemented.

    @param config: The validated simulation config dictionary.
    @param graph: The contact graph.
    @param patient_zero: The patient zero Person object.
    @param persons: List of all Person objects.
    @returns: A tuple of (risk_scores, risk_table) where risk_scores[i]
              is the final risk for vertex V_i, and risk_table is the
              full T+1 x n table. Both are None if not implemented.
    """
    print(f"[3] Running risk solver ({config['risk_solver']})...")
    print(f"      Planning horizon : {config['time_horizon']} days")

    risk_scores = None
    risk_table = None

    if config['risk_solver'] == 'monte_carlo':
        from transmission.monte_carlo import monte_carlo
        print(f"      Simulations      : {config['simulations']}")
        risk_table = monte_carlo(graph, patient_zero, config['time_horizon'], config['simulations'])
        risk_scores = risk_table[config['time_horizon']]

    elif config['risk_solver'] == 'task_b':
        from transmission.task_b import task_b
        risk_table = task_b(graph, patient_zero, config['time_horizon'])
        risk_scores = risk_table[config['time_horizon']]

    if risk_scores is not None:
        for person in persons:
            person.set_prob_of_infection(risk_scores[person.index])
        print(f"      Risk scores computed successfully.")
    else:
        print(f"      Risk solver returned no results.")

    print()
    return risk_scores, risk_table


def run_vaccine_program(config: dict,
                        eligible: list[Person]) -> tuple[list[Person], float, int] | tuple[None, None, None]:
    """
    Runs the selected vaccine allocation program to determine which
    residents should receive antiviral doses.

    Returns (None, None, None) if run_vaccine is False in config,
    or if the selected strategy is not yet implemented.

    @param config: The validated simulation config dictionary.
    @param eligible: A list of Person objects eligible for vaccination,
                     sorted by benefit descending.
    @returns: A tuple of (vaccinated, total_benefit, total_used),
              or (None, None, None) if skipped or not implemented.
    """
    if not config['run_vaccine']:
        print(f"[5] Vaccine allocation program: skipped (run_vaccine=false).")
        print(f"      Set 'run_vaccine': true in config to enable Task D.")
        print()
        return None, None, None

    print(f"[5] Running vaccine allocation program ({config['vaccine_strategy']})...")

    if config['vaccine_strategy'] == 'task_d':
        from treatment.task_d import task_d
        vaccinated, total_benefit, total_used, _ = task_d(eligible, config['total_doses'])

    else:
        from treatment.vaccination_program import brute_force_vaccination
        vaccinated, total_benefit, total_used, _ = brute_force_vaccination(eligible, config['total_doses'])

    if vaccinated is not None:
        print(f"      Vaccinated    : {len(vaccinated)} residents")
        print(f"      Total benefit : {total_benefit:.4f}")
        print(f"      Doses used    : {total_used} / {config['total_doses']}")
    else:
        print(f"      Vaccine program returned no results.")

    print()
    return vaccinated, total_benefit, total_used


def run_visualiser(config: dict,
                   graph: Graph,
                   persons: list[Person],
                   patient_zero: Person,
                   risk_scores: list[float] | None,
                   risk_table: list[list[float]] | None,
                   vaccinated: list[Person] | None,
                   eligible: list[Person] | None) -> None:
    """
    Generates and saves the visualisation PDF if enabled in config.

    @param config: The validated simulation config dictionary.
    @param graph: The contact graph.
    @param persons: List of all Person objects.
    @param patient_zero: The patient zero Person object.
    @param risk_scores: List of infection risk scores, or None.
    @param risk_table: Full risk table, or None.
    @param vaccinated: List of vaccinated Person objects, or None.
    @param eligible: List of eligible Person objects for DP table, or None.
    @returns: None
    """
    if not config['visualise']:
        return

    print(f"[6] Visualising contact network...")
    from utils.visualise import visualise
    visualise(
        graph,
        persons,
        patient_zero,
        config['graph_type'],
        config['visual_filename'],
        risk_scores,
        risk_table,
        vaccinated,
        eligible,
        config['total_doses']
    )
    print()
