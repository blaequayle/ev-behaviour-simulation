from datetime import datetime
from enum import Enum

import numpy as np


class DriverType(Enum):
    AVERAGE_UK = "Average UK"
    INTELLIGENT_OCTOPUS_AVG = "Intelligent Octopus Average"
    INFREQUENT_CHARGING = "Infrequent Charging"
    INFREQUENT_DRIVING = "Infrequent Driving"
    SCHEUDULED_CHARGING = "Scheduled charging"
    ALWAYS_PLUGGED_IN = "Always plugged-in"


archetypes = {
    DriverType.AVERAGE_UK: {
        "proportion": 0.4,
        "plug_in_time": datetime(2025, 11, 17, 18, 0, 0),
        "plug_out_time": datetime(2025, 11, 18, 7, 0, 0),
        "soc_start": lambda n: np.random.normal(0.68, 0.05, size=n),
        "soc_end": 0.8,
    },
    DriverType.INTELLIGENT_OCTOPUS_AVG: {
        "proportion": 0.3,
        "plug_in_time": datetime(2025, 11, 17, 18, 0, 0),
        "plug_out_time": datetime(2025, 11, 18, 7, 0, 0),
        "soc_start": lambda n: np.random.normal(0.52, 0.05, size=n),
        "soc_end": 0.8,
    },
    DriverType.INFREQUENT_CHARGING: {
        "proportion": 0.1,
        "plug_in_time": datetime(2025, 11, 17, 18, 0, 0),
        "plug_out_time": datetime(2025, 11, 18, 7, 0, 0),
        "soc_start": lambda n: np.random.normal(0.18, 0.05, size=n),
        "soc_end": 0.8,
    },
    DriverType.INFREQUENT_DRIVING: {
        "proportion": 0.1,
        "plug_in_time": datetime(2025, 11, 17, 18, 0, 0),
        "plug_out_time": datetime(2025, 11, 18, 7, 0, 0),
        "soc_start": lambda n: np.random.normal(0.73, 0.05, size=n),
        "soc_end": 0.8,
    },
    DriverType.SCHEUDULED_CHARGING: {
        "proportion": 0.09,
        "plug_in_time": datetime(2025, 11, 17, 22, 0, 0),
        "plug_out_time": datetime(2025, 11, 18, 9, 0, 0),
        "soc_start": lambda n: np.random.normal(0.68, 0.05, size=n),
        "soc_end": 0.8,
    },
    DriverType.ALWAYS_PLUGGED_IN: {
        "proportion": 0.01,
        "plug_in_time": datetime(2025, 11, 17, 0, 0, 0),
        "plug_out_time": datetime(2025, 11, 18, 0, 0, 0),
        "soc_start": lambda n: np.random.normal(0.68, 0.05, size=n),
        "soc_end": 0.8,
    },
}
