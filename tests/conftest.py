import pytest
from py_mini_racer import MiniRacer


@pytest.fixture(scope="function")
def jsctx() -> MiniRacer:
    """Create a fresh JavaScript context for testing."""
    return MiniRacer()
