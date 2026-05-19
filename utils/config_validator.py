# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Utility functions for validating the config file.
#
# __author__ = 'Edward Small'
# __project__ = 'Modelling a Disease Outbreak'
# __copyright__ = 'Copyright 2026, RMIT University'
# -------------------------------------------------


def validate_config(config: dict) -> list[str]:
    """
    Validates the simulation config dictionary.

    Checks that all required keys are present, that values are of the
    correct type, and that all constraints are satisfied. Returns a list
    of error messages — one per violation. An empty list means the config
    is valid.

    @param config: The configuration dictionary loaded from the JSON file.
    @returns: A list of error message strings. Empty if the config is valid.
    """
    errors = []

    # -------------------------
    # Check for required keys
    # -------------------------
    required_keys = [
        'seed',
        'num_residents',
        'num_edges',
        'max_transmission_prob',
        'vulnerability_range',
        'dosage_range',
        'graph_type',
        'risk_solver',
        'time_horizon',
        'simulations',
        'total_doses',
        'run_vaccine',
        'vaccine_strategy',
        'visualise',
        'visual_filename',
        'print_struct'
    ]

    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required config key: '{key}'.")

    # If any keys are missing, return early — further checks may crash
    if errors:
        return errors

    # -------------------------
    # seed
    # -------------------------
    if not isinstance(config['seed'], int):
        errors.append(f"'seed' must be an integer, got {type(config['seed']).__name__}.")

    # -------------------------
    # num_residents
    # -------------------------
    if not isinstance(config['num_residents'], int):
        errors.append(f"'num_residents' must be an integer, got {type(config['num_residents']).__name__}.")
    elif config['num_residents'] <= 0:
        errors.append(f"'num_residents' must be greater than 0, got {config['num_residents']}.")

    # -------------------------
    # num_edges
    # -------------------------
    if not isinstance(config['num_edges'], int):
        errors.append(f"'num_edges' must be an integer, got {type(config['num_edges']).__name__}.")
    elif config['num_edges'] <= 0:
        errors.append(f"'num_edges' must be greater than 0, got {config['num_edges']}.")
    else:
        n = config['num_residents']
        max_edges = n * (n - 1) // 2
        if config['num_edges'] > max_edges:
            errors.append(f"'num_edges' must be at most {max_edges} for {n} residents, got {config['num_edges']}.")

    # -------------------------
    # max_transmission_prob
    # -------------------------
    if not isinstance(config['max_transmission_prob'], (int, float)):
        errors.append(f"'max_transmission_prob' must be a float, got {type(config['max_transmission_prob']).__name__}.")
    elif not (0.0002 <= config['max_transmission_prob'] <= 1.0):
        errors.append(f"'max_transmission_prob' must be in [0.0002, 1.0], got {config['max_transmission_prob']}.")

    # -------------------------
    # vulnerability_range
    # -------------------------
    vr = config['vulnerability_range']
    if not isinstance(vr, list) or len(vr) != 2:
        errors.append(f"'vulnerability_range' must be a list of two values, got {vr}.")
    else:
        if not all(isinstance(v, (int, float)) for v in vr):
            errors.append(f"'vulnerability_range' values must be numeric, got {vr}.")
        elif not all(v > 0 for v in vr):
            errors.append(f"'vulnerability_range' values must be positive, got {vr}.")
        elif vr[0] >= vr[1]:
            errors.append(f"'vulnerability_range' min must be less than max, got {vr}.")

    # -------------------------
    # dosage_range
    # -------------------------
    dr = config['dosage_range']
    if not isinstance(dr, list) or len(dr) != 2:
        errors.append(f"'dosage_range' must be a list of two values, got {dr}.")
    else:
        if not all(isinstance(d, int) for d in dr):
            errors.append(f"'dosage_range' values must be integers, got {dr}.")
        elif not all(d > 0 for d in dr):
            errors.append(f"'dosage_range' values must be positive, got {dr}.")
        elif dr[0] >= dr[1]:
            errors.append(f"'dosage_range' min must be less than max, got {dr}.")

    # -------------------------
    # graph_type
    # -------------------------
    if not isinstance(config['graph_type'], str):
        errors.append(f"'graph_type' must be a string, got {type(config['graph_type']).__name__}.")
    elif config['graph_type'] not in ('list', 'matrix'):
        errors.append(f"'graph_type' must be 'list' or 'matrix', got '{config['graph_type']}'.")

    # -------------------------
    # risk_solver
    # -------------------------
    if not isinstance(config['risk_solver'], str):
        errors.append(f"'risk_solver' must be a string, got {type(config['risk_solver']).__name__}.")
    elif config['risk_solver'] not in ('monte_carlo', 'task_b'):
        errors.append(f"'risk_solver' must be 'monte_carlo' or 'task_b', got '{config['risk_solver']}'.")

    # -------------------------
    # time_horizon
    # -------------------------
    if not isinstance(config['time_horizon'], int):
        errors.append(f"'time_horizon' must be an integer, got {type(config['time_horizon']).__name__}.")
    elif config['time_horizon'] <= 0:
        errors.append(f"'time_horizon' must be greater than 0, got {config['time_horizon']}.")

    # -------------------------
    # simulations
    # -------------------------
    if not isinstance(config['simulations'], int):
        errors.append(f"'simulations' must be an integer, got {type(config['simulations']).__name__}.")
    elif config['simulations'] <= 0:
        errors.append(f"'simulations' must be greater than 0, got {config['simulations']}.")

    # -------------------------
    # total_doses
    # -------------------------
    if not isinstance(config['total_doses'], int):
        errors.append(f"'total_doses' must be an integer, got {type(config['total_doses']).__name__}.")
    elif config['total_doses'] <= 0:
        errors.append(f"'total_doses' must be greater than 0, got {config['total_doses']}.")

    # -------------------------
    # run_vaccine
    # -------------------------
    if not isinstance(config['run_vaccine'], bool):
        errors.append(f"'run_vaccine' must be a boolean, got {type(config['run_vaccine']).__name__}.")

    # -------------------------
    # vaccine_strategy
    # -------------------------
    if not isinstance(config['vaccine_strategy'], str):
        errors.append(f"'vaccine_strategy' must be a string, got {type(config['vaccine_strategy']).__name__}.")
    elif config['vaccine_strategy'] not in ('brute_force', 'task_d'):
        errors.append(f"'vaccine_strategy' must be 'brute_force' or 'task_d', got '{config['vaccine_strategy']}'.")

    # -------------------------
    # visualise
    # -------------------------
    if not isinstance(config['visualise'], bool):
        errors.append(f"'visualise' must be a boolean, got {type(config['visualise']).__name__}.")

    # -------------------------
    # visual_filename
    # -------------------------
    if not isinstance(config['visual_filename'], str):
        errors.append(f"'visual_filename' must be a string, got {type(config['visual_filename']).__name__}.")
    elif not config['visual_filename'].strip():
        errors.append(f"'visual_filename' must not be empty.")

    # -------------------------
    # print_struct
    # -------------------------
    if not isinstance(config['print_struct'], bool):
        errors.append(f"'print_struct' must be a boolean, got {type(config['print_struct']).__name__}.")

    return errors
