"""Regression coverage for the installed SDK's public documentation contract."""

import importlib.metadata
import inspect
import io
import json

import httpx
import pytest

import keito
from keito import AsyncKeito, Keito, KeitoForbiddenError, KeitoServerError
from keito.types import Source
from tests.test_expenses import _EXPENSE_JSON


@pytest.mark.parametrize(
    "base_url",
    [
        None,
        "https://app.keito.ai",
        "https://app.keito.ai/",
        "https://app.keito.ai/api/v2",
        "https://app.keito.ai/api/v2/",
    ],
)
def test_base_url_reaches_one_v2_path(base_url):
    seen = []

    def respond(request):
        seen.append(request)
        return httpx.Response(200, json={"expenses": [], "page": 1, "total_pages": 0})

    options = {} if base_url is None else {"base_url": base_url}
    with (
        httpx.Client(transport=httpx.MockTransport(respond)) as transport,
        Keito(api_key="synthetic-key", account_id="synthetic-account", httpx_client=transport, **options) as client,
    ):
        assert list(client.expenses.list()) == []
    assert str(seen[0].url) == "https://app.keito.ai/api/v2/expenses?page=1"
    assert seen[0].headers["Authorization"] == "Bearer synthetic-key"
    assert seen[0].headers["Keito-Account-Id"] == "synthetic-account"


@pytest.mark.parametrize(
    "base_url",
    [
        "https://user:secret@example.test",
        "https://example.test?secret=x",
        "https://example.test#fragment",
        "file:///tmp/sdk",
    ],
)
def test_invalid_base_urls_fail_before_credentials_can_be_sent(base_url):
    with pytest.raises(ValueError, match="base_url"):
        Keito(api_key="synthetic-key", account_id="synthetic-account", base_url=base_url)


def test_version_and_user_agent_match_installed_distribution(httpx_mock):
    assert keito.__version__ == importlib.metadata.version("keito")
    httpx_mock.add_response(json={"expenses": [], "page": 1, "total_pages": 0})
    with Keito(api_key="synthetic-key", account_id="synthetic-account") as client:
        list(client.expenses.list())
    assert httpx_mock.get_request().headers["User-Agent"] == f"keito-python/{keito.__version__}"


@pytest.mark.parametrize("resource", ["expenses", "time_entries"])
@pytest.mark.parametrize("source", [Source.AGENT, "agent"])
def test_list_source_strings_and_enums_have_identical_wire_values(httpx_mock, resource, source):
    httpx_mock.add_response(json={resource: [], "page": 1, "total_pages": 0})
    with Keito(api_key="synthetic-key", account_id="synthetic-account") as client:
        assert list(getattr(client, resource).list(source=source)) == []
    assert httpx_mock.get_request().url.params["source"] == "agent"


@pytest.mark.parametrize("resource", ["expenses", "time_entries"])
def test_invalid_source_is_rejected_before_a_request(resource):
    with Keito(api_key="synthetic-key", account_id="synthetic-account") as client, pytest.raises(ValueError):
        getattr(client, resource).list(source="not-a-source")


def test_expense_get_update_preserves_null_and_delete(httpx_mock):
    httpx_mock.add_response(method="GET", json={**_EXPENSE_JSON, "units": 1.25, "currency": "GBP"})
    httpx_mock.add_response(method="PATCH", json={**_EXPENSE_JSON, "notes": None})
    httpx_mock.add_response(method="DELETE", json={"success": True})
    with Keito(api_key="synthetic-key", account_id="synthetic-account") as client:
        expense = client.expenses.get("expense-1")
        assert expense.units == 1.25
        assert expense.currency == "GBP"
        updated = client.expenses.update("expense-1", notes=None, metadata=None, attach_receipt_to_invoice=False)
        assert updated.notes is None
        assert client.expenses.delete("expense-1") is None
    requests = httpx_mock.get_requests()
    assert requests[0].url.path == "/api/v2/expenses/expense-1"
    assert json.loads(requests[1].content) == {"notes": None, "metadata": None, "attach_receipt_to_invoice": False}


def test_receipt_upload_download_and_delete_use_the_existing_expense(httpx_mock):
    metadata = {
        "receipt_file_name": "receipt.pdf",
        "receipt_file_size": 4,
        "receipt_content_type": "application/pdf",
        "receipt_url": "/api/v2/expenses/expense-1/receipt",
    }
    httpx_mock.add_response(method="POST", status_code=201, json=metadata)
    httpx_mock.add_response(method="GET", content=b"%PDF", headers={"Content-Type": "application/pdf"})
    httpx_mock.add_response(method="DELETE", json={"success": True})
    with Keito(api_key="synthetic-key", account_id="synthetic-account") as client:
        uploaded = client.expenses.upload_receipt(
            "expense-1", file=io.BytesIO(b"%PDF"), filename="receipt.pdf", content_type="application/pdf"
        )
        assert uploaded.receipt_file_size == 4
        assert client.expenses.download_receipt("expense-1") == b"%PDF"
        assert client.expenses.delete_receipt("expense-1") is None
    upload = httpx_mock.get_requests()[0]
    assert upload.url.path == "/api/v2/expenses/expense-1/receipt"
    assert upload.headers["Content-Type"].startswith("multipart/form-data; boundary=")
    assert b'name="file"; filename="receipt.pdf"' in upload.content
    assert b"Content-Type: application/pdf" in upload.content
    assert b"%PDF" in upload.content


def test_receipt_upload_does_not_replay_even_with_an_idempotency_header(httpx_mock):
    httpx_mock.add_response(status_code=500)
    with (
        Keito(api_key="synthetic-key", account_id="synthetic-account", max_retries=2) as client,
        pytest.raises(KeitoServerError),
    ):
        client.expenses.upload_receipt(
            "expense-1",
            file=b"%PDF",
            filename="receipt.pdf",
            content_type="application/pdf",
            request_options={"additional_headers": {"Idempotency-Key": "synthetic-upload-1"}},
        )
    assert len(httpx_mock.get_requests()) == 1


def test_expense_permissions_are_not_swallowed(httpx_mock):
    httpx_mock.add_response(status_code=403, json={"error": "forbidden", "error_description": "Expense is locked"})
    with (
        Keito(api_key="synthetic-key", account_id="synthetic-account") as client,
        pytest.raises(KeitoForbiddenError, match="Expense is locked"),
    ):
        client.expenses.get("expense-1")


def test_patch_without_idempotency_key_is_not_replayed(httpx_mock):
    httpx_mock.add_response(status_code=500)
    with (
        Keito(api_key="synthetic-key", account_id="synthetic-account", max_retries=2) as client,
        pytest.raises(KeitoServerError),
    ):
        client.time_entries.stop_timer("entry-1")
    assert len(httpx_mock.get_requests()) == 1


def test_json_mutation_with_idempotency_key_can_retry_the_identical_request(httpx_mock):
    httpx_mock.add_response(status_code=429, headers={"Retry-After": "0"})
    httpx_mock.add_response(json=_EXPENSE_JSON)
    with Keito(api_key="synthetic-key", account_id="synthetic-account", max_retries=1) as client:
        client.expenses.update(
            "expense-1",
            notes="corrected",
            request_options={"additional_headers": {"Idempotency-Key": "expense-update-001"}},
        )
    requests = httpx_mock.get_requests()
    assert len(requests) == 2
    assert requests[0].content == requests[1].content == b'{"notes":"corrected"}'
    assert requests[0].headers["Idempotency-Key"] == requests[1].headers["Idempotency-Key"]


@pytest.mark.parametrize("file", [b"", b"x" * (9 * 1024 * 1024 + 1)])
def test_receipt_upload_size_failures_do_not_send_a_request(file):
    with (
        Keito(api_key="synthetic-key", account_id="synthetic-account") as client,
        pytest.raises(ValueError, match="9 MiB"),
    ):
        client.expenses.upload_receipt("expense-1", file=file, filename="r.pdf", content_type="application/pdf")


def test_multipart_boundary_is_owned_by_httpx_even_with_custom_content_type(httpx_mock):
    httpx_mock.add_response(
        status_code=201,
        json={
            "receipt_file_name": "r.pdf",
            "receipt_file_size": 4,
            "receipt_content_type": "application/pdf",
            "receipt_url": "/api/v2/expenses/expense-1/receipt",
        },
    )
    with Keito(api_key="synthetic-key", account_id="synthetic-account") as client:
        client.expenses.upload_receipt(
            "expense-1",
            file=b"%PDF",
            filename="r.pdf",
            content_type="application/pdf",
            request_options={"additional_headers": {"content-type": "application/json"}},
        )
    assert httpx_mock.get_request().headers["Content-Type"].startswith("multipart/form-data; boundary=")


def test_binary_reader_with_short_reads_is_uploaded_completely(httpx_mock):
    class ShortReader(io.BytesIO):
        def read(self, size=-1):
            return super().read(min(size, 2))

    httpx_mock.add_response(status_code=201, json={"receipt_url": "/api/v2/expenses/expense-1/receipt"})
    with Keito(api_key="synthetic-key", account_id="synthetic-account") as client:
        client.expenses.upload_receipt(
            "expense-1", file=ShortReader(b"%PDFdata"), filename="r.pdf", content_type="application/pdf"
        )
    assert b"%PDFdata" in httpx_mock.get_request().content


def test_expense_update_rejects_empty_unknown_and_immutable_fields():
    from pydantic import ValidationError

    with Keito(api_key="synthetic-key", account_id="synthetic-account") as client:
        with pytest.raises(ValueError, match="At least one"):
            client.expenses.update("expense-1")
        for body in [
            {"user_id": "someone-else"},
            {"entry_type": "refund"},
            {"source": "web"},
            {"project_id": None},
            {"spent_date": None},
            {"billable": None},
        ]:
            with pytest.raises(ValidationError):
                client.expenses.update("expense-1", **body)


@pytest.mark.asyncio
async def test_async_documented_flow_keeps_lazy_iteration_and_receipt_bytes(httpx_mock):
    httpx_mock.add_response(method="GET", json={"expenses": [], "page": 1, "total_pages": 0})
    httpx_mock.add_response(method="GET", json=_EXPENSE_JSON)
    httpx_mock.add_response(
        method="POST",
        status_code=201,
        json={
            "receipt_file_name": "r.pdf",
            "receipt_file_size": 4,
            "receipt_content_type": "application/pdf",
            "receipt_url": "/api/v2/expenses/expense-1/receipt",
        },
    )
    httpx_mock.add_response(method="GET", content=b"%PDF")
    async with AsyncKeito(
        api_key="synthetic-key", account_id="synthetic-account", base_url="https://app.keito.ai/api/v2/"
    ) as client:
        iterator = client.expenses.list(source="agent")
        assert not inspect.isawaitable(iterator)
        assert [item async for item in iterator] == []
        assert (await client.expenses.get("expense-1")).id == "exp_123"
        await client.expenses.upload_receipt(
            "expense-1", file=b"%PDF", filename="r.pdf", content_type="application/pdf"
        )
        assert await client.expenses.download_receipt("expense-1") == b"%PDF"
    assert all(request.url.host == "app.keito.ai" for request in httpx_mock.get_requests())


def test_outcome_annotations_allow_explicit_api_source_without_changing_legacy_default(httpx_mock):
    from tests.test_time_entries import _ENTRY_JSON

    httpx_mock.add_response(json=_ENTRY_JSON)
    httpx_mock.add_response(json=_ENTRY_JSON)
    with Keito(api_key="synthetic-key", account_id="synthetic-account") as client:
        arguments = dict(project_id="p", task_id="t", spent_date="2026-10-30", outcome_type="example")
        client.outcomes.log(**arguments, source="api")
        client.outcomes.log(**arguments)
    first, legacy = [json.loads(request.content) for request in httpx_mock.get_requests()]
    assert first["source"] == "api"
    assert legacy["source"] == "agent"
    assert first["hours"] == 0
    assert first["metadata"] == {"outcome_type": "example", "outcome_quantity": 1, "outcome_success": True}
