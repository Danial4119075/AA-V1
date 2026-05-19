# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Timer utility for measuring algorithm runtime.
#
# __author__ = 'Edward Small'
# __project__ = 'Modelling a Disease Outbreak'
# __copyright__ = 'Copyright 2026, RMIT University'
# -------------------------------------------------

import time


def start() -> float:
    """
    Records the current time as the start of a timed section.

    Usage:
        start_time = start()
        # ... code to time ...
        elapsed = stop(start_time)

    @returns: The current time as a float (seconds since epoch).
    """
    return time.time()


def stop(start_time: float) -> float:
    """
    Computes the elapsed time since the given start time.

    @param start_time: The start time returned by start().
    @returns: Elapsed time in seconds as a float.
    """
    return time.time() - start_time
