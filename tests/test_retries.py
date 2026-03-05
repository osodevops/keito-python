import httpx
import pytest
from pytest_httpx import HTTPXMock

from keito import Keito, KeitoServerError, KeitoTimeoutError
from keito.types import User

_USER_JSON = {
    "id": "user_123",
    "email": "test@example.com",
    "is_active": True,
    "roles": [],
    "created_at": "2026-03-05T10:00:00Z",
    "updated_at": "2026-03-05T10:00:00Z",
}


def test_retries_on_500(httpx_mock: HTTPXMock):
    client = Keito(api_key="kto_test", account_id="acc_test", max_retries=2)

    # First two fail, third succeeds
    httpx_mock.add_response(status_code=500)
    httpx_mock.add_response(status_code=500)
    httpx_mock.add_response(json=_USER_JSON)

    user = client.users.me()
    assert user.id == "user_123"
    assert len(httpx_mock.get_requests()) == 3


def test_retries_on_502(httpx_mock: HTTPXMock):
    client = Keito(api_key="kto_test", account_id="acc_test", max_retries=1)

    httpx_mock.add_response(status_code=502)
    httpx_mock.add_response(json=_USER_JSON)

    user = client.users.me()
    assert user.id == "user_123"


def test_exhausted_retries_raises(httpx_mock: HTTPXMock):
    client = Keito(api_key="kto_test", account_id="acc_test", max_retries=1)

    httpx_mock.add_response(status_code=500)
    httpx_mock.add_response(status_code=500)

    with pytest.raises(KeitoServerError):
        client.users.me()


def test_no_retry_on_post(httpx_mock: HTTPXMock):
    client = Keito(api_key="kto_test", account_id="acc_test", max_retries=2)

    httpx_mock.add_response(status_code=500)

    with pytest.raises(KeitoServerError):
        client.time_entries.create(
            project_id="p",
            task_id="t",
            spent_date="2026-01-01",
            hours=1,
        )

    # POST should not retry — only 1 request
    assert len(httpx_mock.get_requests()) == 1


def test_max_retries_zero(httpx_mock: HTTPXMock):
    client = Keito(api_key="kto_test", account_id="acc_test", max_retries=0)

    httpx_mock.add_response(status_code=503)

    with pytest.raises(KeitoServerError):
        client.users.me()

    assert len(httpx_mock.get_requests()) == 1
