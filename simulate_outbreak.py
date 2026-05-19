# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Main script for the disease outbreak simulation.
#
# __author__ = 'Edward Small'
# __project__ = 'Modelling a Disease Outbreak'
# __copyright__ = 'Copyright 2026, RMIT University'
# -------------------------------------------------

import sys

if sys.version_info < (3, 13):
    print(f"[ERROR] Python 3.13 or higher is required.")
    print(f"        You are running Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"        Please upgrade your Python installation and try again.")
    sys.exit(1)

from utils.timer import start, stop
from utils.simulation_utils import (
    setup,
    build_city,
    run_risk_solver,
    run_vaccine_program,
    run_visualiser
)


def main():
    """
    Entry point for the disease outbreak simulation.

    Runs each stage of the simulation in order:
        1. Load and validate config
        2. Build the contact graph
        3. Run the risk solver (Task B)
        4. Get eligible residents for vaccination
        5. Run the vaccine allocation program (Task D)
        6. Visualise results

    The timer wraps the entire program — use utils/timer.py
    to time individual steps for Task C analysis.
    """
    program_start = start()

    if len(sys.argv) != 2:
        print("Usage: python simulate_outbreak.py <config_file>.json")
        sys.exit(1)

    # Step 1 — load and validate config
    config = setup(sys.argv[1])

    # Step 2 — build the contact graph and assign patient zero
    city, graph, persons, patient_zero = build_city(config)

    # Step 3 — compute infection risk r_{i,T} for every resident (Task B)
    risk_scores, risk_table = run_risk_solver(config, graph, patient_zero, persons)

    # Step 4 — get eligible residents sorted by risk descending
    print(f"[4] Preparing eligible residents for vaccination...")
    eligible = city.get_eligible_residents()
    print(f"      Eligible residents : {len(eligible)}")
    if not config['run_vaccine']:
        print(f"      Task D will be skipped (run_vaccine=false in config).")
    print()

    # Step 5 — allocate antiviral doses optimally (Task D)
    vaccinated, total_benefit, total_used = run_vaccine_program(config, eligible)

    # Step 6 — visualise the outbreak and results (optional)
    run_visualiser(config, graph, persons, patient_zero, risk_scores, risk_table, vaccinated, eligible)

    elapsed = stop(program_start)
    print("==========================================")
    print("   Simulation complete.")
    print(f"   Total time: {elapsed:.4f}s")
    print("==========================================")


if __name__ == '__main__':
    main()
