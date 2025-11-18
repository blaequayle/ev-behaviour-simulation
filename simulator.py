from dataclasses import dataclass, field
from datetime import time
from itertools import count

import numpy as np
import pandas as pd

from archetypes import DriverType, archetypes

id_counter = count()


@dataclass
class EVDriver:
    driver_type: DriverType
    plug_in_time: time
    plug_out_time: time
    soc_start: float
    soc_end: float
    driver_id: int = field(default_factory=lambda: next(id_counter))


@dataclass
class EVBehaviourSimulator:
    """Simulator for creating a population of EV drivers based on archetypes."""

    population_size: int = 5000
    driver_types: dict = field(default_factory=lambda: archetypes)

    def _create_ev_driver(
        self,
        driver_type: DriverType,
        driver_params: dict,
        size: int,
        i: int,
    ) -> EVDriver:
        return EVDriver(
            driver_type=driver_type,
            plug_in_time=driver_params["plug_in_time"],
            plug_out_time=driver_params["plug_out_time"],
            soc_start=driver_params["soc_start"](size)[i],
            soc_end=driver_params["soc_end"],
        )

    def create_population(self) -> pd.DataFrame:
        """Create a population of users based on archetype proportions."""
        population = []
        for driver_type, params in self.driver_types.items():
            number_of_users = int(params["proportion"] * self.population_size)
            for i in range(number_of_users):
                population.append(
                    self._create_ev_driver(
                        driver_type, params, number_of_users, i
                    )
                )
        return pd.DataFrame(population)

    def simulate_plug_in_count(self, population: pd.DataFrame) -> pd.Series:
        """Generate count of number of drivers plugged in during each interval."""

        intervals = pd.timedelta_range(start="0h", end="23.5h", freq="30min")
        counts = pd.Series(0, index=intervals)

        for _, driver in population.iterrows():
            start = pd.Timedelta(
                hours=driver["plug_in_time"].hour,
                minutes=driver["plug_in_time"].minute,
                seconds=driver["plug_in_time"].second,
            )
            end = pd.Timedelta(
                hours=driver["plug_out_time"].hour,
                minutes=driver["plug_out_time"].minute,
                seconds=driver["plug_out_time"].second,
            )

            if end < start:  # Handle overnight charging
                mask = (counts.index >= start) | (counts.index < end)
            elif end == start:  # Handle always plugged in
                mask = np.ones_like(counts, dtype=bool)
            else:
                mask = (counts.index >= start) & (counts.index < end)

            counts[mask] += 1
        return counts

    def calculate_soc_profile(
        self,
        start_hour: float,
        end_hour: float,
        start_soc: float,
        end_soc: float,
    ) -> pd.Series:
        """Generate 24 hour state of charge profile with:
        - linear charging from start_hour to end_hour
        - linear discharging from end_hour to next day's start_hour
        """

        intervals = np.arange(0, 24, 0.5)
        n = len(intervals)
        # Build 0–48 time series
        t = np.concatenate([intervals, intervals + 24])
        end_hour = (
            float(end_hour)
            if end_hour >= start_hour
            else float(end_hour) + 24.0
        )
        start_hour_next = start_hour + 24.0
        # Define SoC array to populate
        soc = np.full(t.shape, np.nan, dtype=float)

        if end_hour == start_hour:
            # need to handle always plugged in case
            soc[:] = end_soc
        else:
            # Charging: start_hour to end_hour
            charge_mask = (t >= start_hour) & (t <= end_hour)
            if np.any(charge_mask):
                soc[charge_mask] = start_soc + (
                    (t[charge_mask] - start_hour) / (end_hour - start_hour)
                ) * (end_soc - start_soc)

            # Discharging: end_hour to start_hour_next
            discharge_mask = (t >= end_hour) & (t <= start_hour_next)
            if np.any(discharge_mask):
                soc[discharge_mask] = end_soc - (
                    (t[discharge_mask] - end_hour)
                    / (start_hour_next - end_hour)
                ) * (end_soc - start_soc)

        first_half = soc[:n]
        second_half = soc[n:]
        result_array = np.where(~np.isnan(first_half), first_half, second_half)

        return pd.Series(
            result_array,
            index=pd.timedelta_range(start="0h", end="23.5h", freq="30min"),
        )

    def simulate_state_of_charge(self, population: pd.DataFrame) -> np.ndarray:
        """Generate state of charge profiles for the population."""
        profiles = []
        for _, row in population.iterrows():
            profile = self.calculate_soc_profile(
                start_hour=row["plug_in_time"].hour,
                end_hour=row["plug_out_time"].hour,
                start_soc=row["soc_start"],
                end_soc=row["soc_end"],
            )
            profiles.append(profile)

        return np.column_stack(profiles)


def main():
    simulator = EVBehaviourSimulator()
    population = simulator.create_population()
    plug_in_percentage = simulator.simulate_plug_in_count(population)
    state_of_charge = simulator.simulate_state_of_charge(population)


if __name__ == "__main__":
    main()
