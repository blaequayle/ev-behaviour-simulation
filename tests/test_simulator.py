import numpy as np
import pandas as pd


class TestSimulatePlugInCount:
    def test_single_driver_plugged_in(self, simulator):
        """Test with a single driver plugged in for a full day."""
        population = pd.DataFrame(
            {
                "plug_in_time": [pd.Timestamp("2023-01-01 00:00:00")],
                "plug_out_time": [pd.Timestamp("2023-01-01 23:59:59")],
            }
        )
        result = simulator.simulate_plug_in_count(population)
        assert result.sum() == 48  # 48 half-hour intervals in a day

    def test_single_driver_partial_day(self, simulator):
        """Test with a single driver plugged in for part of the day."""
        population = pd.DataFrame(
            {
                "plug_in_time": [pd.Timestamp("2023-01-01 06:00:00")],
                "plug_out_time": [pd.Timestamp("2023-01-01 12:00:00")],
            }
        )
        result = simulator.simulate_plug_in_count(population)
        assert result.sum() == 12  # 12 half-hour intervals from 6 to 12

    def test_multiple_drivers(self, simulator):
        """Test with multiple drivers plugged in at different times."""
        population = pd.DataFrame(
            {
                "plug_in_time": [
                    pd.Timestamp("2023-01-01 00:00:00"),
                    pd.Timestamp("2023-01-01 12:00:00"),
                ],
                "plug_out_time": [
                    pd.Timestamp("2023-01-01 06:00:00"),
                    pd.Timestamp("2023-01-01 18:00:00"),
                ],
            }
        )
        result = simulator.simulate_plug_in_count(population)
        assert result.sum() == 24  # 2 sets of 12 half-hour intervals

    def test_overnight_plug_in(self, simulator):
        """Test with a driver plugged in overnight, this should be wrapped
        and returned at the start of the 24 hour period."""
        population = pd.DataFrame(
            {
                "plug_in_time": [pd.Timestamp("2023-01-01 22:00:00")],
                "plug_out_time": [pd.Timestamp("2023-01-02 02:00:00")],
            }
        )
        result = simulator.simulate_plug_in_count(population)
        assert result.sum() == 8


class TestCalculateSocProfile:
    def test_basic_charging(self, simulator):
        """Test standard charging from start_hour to end_hour."""
        result = simulator.calculate_soc_profile(
            start_hour=6.0,
            end_hour=18.0,
            start_soc=0.2,
            end_soc=0.8,
        )

        assert isinstance(result, pd.Series)
        assert len(result) == 48
        assert not result.isna().any()
        assert max(result) == 0.8
        assert min(result) == 0.2

    def test_overnight_charging(self, simulator):
        """Test charging that wraps overnight (end_hour < start_hour)."""
        result = simulator.calculate_soc_profile(
            start_hour=22.0,
            end_hour=6.0,
            start_soc=0.3,
            end_soc=0.8,
        )

        assert isinstance(result, pd.Series)
        assert len(result) == 48
        assert (
            result[-1] < result[0]
        )  # Charge just before midnight should be less than just after

    def test_always_plugged_in(self, simulator):
        """Test for always plugged in (start_hour == end_hour)."""
        result = simulator.calculate_soc_profile(
            start_hour=0.0,
            end_hour=0.0,
            start_soc=0.5,
            end_soc=0.8,
        )

        assert isinstance(result, pd.Series)
        assert len(result) == 48
        assert not result.isna().any()
        assert np.allclose(result.values, 0.8)  # All values should be end_soc

    def test_output_series_index(self, simulator):
        """Test that output has correct index."""
        result = simulator.calculate_soc_profile(
            start_hour=8.0,
            end_hour=16.0,
            start_soc=0.1,
            end_soc=0.8,
        )

        expected_index = pd.timedelta_range(
            start="0h", end="23.5h", freq="30min"
        )
        assert isinstance(result.index, pd.TimedeltaIndex)
        assert len(result.index) == len(expected_index)

    def test_soc_within_valid_range(self, simulator):
        """Test that all SoC values are between start_soc and end_soc."""
        result = simulator.calculate_soc_profile(
            start_hour=9.0,
            end_hour=17.0,
            start_soc=0.5,
            end_soc=0.8,
        )

        assert (result >= 0.5).all()
        assert (result <= 0.8).all()

    def test_charging_phase_increases_soc(self, simulator):
        """Test that SoC increases during charging phase."""
        result = simulator.calculate_soc_profile(
            start_hour=6.0,
            end_hour=12.0,
            start_soc=0.4,
            end_soc=0.8,
        )

        charging_indices = pd.timedelta_range(
            start="6h", end="12h", freq="30min"
        )
        charging_values = result[charging_indices[:-1]]
        assert all(x > 0 for x in charging_values.diff()[1:])

    def test_discharging_phase_decreases_soc(self, simulator):
        """Test that SoC decreases during discharging phase."""
        result = simulator.calculate_soc_profile(
            start_hour=8.0,
            end_hour=16.0,
            start_soc=0.3,
            end_soc=0.8,
        )

        discharging_indices = pd.timedelta_range(
            start="16h", end="23.5h", freq="30min"
        )
        discharging_values = result[discharging_indices]
        assert all(x < 0 for x in discharging_values.diff()[1:])

    def test_linearity_of_charging(self, simulator):
        """Test that charging is linear."""
        result = simulator.calculate_soc_profile(
            start_hour=4.0,
            end_hour=8.0,
            start_soc=0.5,
            end_soc=0.8,
        )

        charging_indices = pd.timedelta_range(
            start="4h", end="8h", freq="30min"
        )
        charging_values = result[charging_indices]

        # Differences should be constant (linear)
        diffs = charging_values.diff()[1:]
        assert np.allclose(diffs.values, diffs.values[0], atol=1e-10)
