import pytest

from keito import Keito


@pytest.fixture
def client(httpx_mock):
    return Keito(api_key="kto_test_key", account_id="acc_test_123")
