"""MQGT Dashboard Package

Unified falsification dashboard and joint constraint fusion.
"""

__version__ = "0.1.0"

from mqgtdashboard.fusion import (
    load_channel_bounds,
    load_all_channel_bounds,
    compute_joint_exclusion,
    generate_dashboard_json,
)

__all__ = [
    "__version__",
    "load_channel_bounds",
    "load_all_channel_bounds",
    "compute_joint_exclusion",
    "generate_dashboard_json",
]
