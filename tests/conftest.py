import pytest

from simulator import EVBehaviourSimulator


@pytest.fixture
def simulator():
    """Create a simulator instance for testing."""
    return EVBehaviourSimulator(population_size=100)
