"""Install the built wheel in an isolated environment and exercise its public contract.

Run after ``python -m build`` (which builds the wheel from the sdist).
No credentials or production requests are used.
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import venv


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=pathlib.Path)
    args = parser.parse_args()
    wheel = args.wheel.resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="keito-wheel-smoke-") as temp:
        root = pathlib.Path(temp)
        venv.EnvBuilder(with_pip=True).create(root / "venv")
        python = root / "venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        subprocess.run([str(python), "-m", "pip", "install", "--disable-pip-version-check", str(wheel)], check=True)
        smoke = textwrap.dedent("""
            import asyncio
            import importlib.metadata
            import inspect
            import json
            import pathlib
            import sys
            import httpx
            import keito
            from keito import AsyncKeito, Keito, KeitoAuthError, KeitoApiError
            from keito.types import ExpenseReceipt, ExpenseUpdate, Source

            assert pathlib.Path(keito.__file__).is_relative_to(pathlib.Path(sys.prefix))
            assert keito.__version__ == importlib.metadata.version("keito")
            requests = []
            expense = {
                "id":"expense-1", "user_id":"user-1", "project_id":"project-1",
                "expense_category_id":"category-1", "user":{"id":"user-1"},
                "project":{"id":"project-1"}, "expense_category":{"id":"category-1"},
                "spent_date":"2026-10-30", "total_cost":12.5, "units":1.25,
                "source":"api", "currency":"GBP",
                "created_at":"2026-10-30T10:00:00Z", "updated_at":"2026-10-30T10:00:00Z"
            }
            entry = {
                "id":"entry-1", "user_id":"user-1", "project_id":"project-1", "task_id":"task-1",
                "user":{"id":"user-1"}, "project":{"id":"project-1"}, "task":{"id":"task-1"},
                "spent_date":"2026-10-30", "hours":1, "is_running":False, "source":"api",
                "created_at":"2026-10-30T10:00:00Z", "updated_at":"2026-10-30T10:00:00Z"
            }
            def respond(request):
                requests.append(request)
                assert request.url.host == "app.keito.ai"
                assert "/api/v2/api/v2" not in request.url.path
                assert request.headers["Authorization"] == "Bearer synthetic-wheel-key"
                assert request.headers["Keito-Account-Id"] == "synthetic-wheel-account"
                assert request.headers["User-Agent"] == "keito-python/" + keito.__version__
                if request.url.path.endswith("/receipt"):
                    if request.method == "GET": return httpx.Response(200, content=b"%PDF")
                    if request.method == "POST":
                        assert request.headers["Content-Type"].startswith("multipart/form-data; boundary=")
                        assert b'name="file"' in request.content
                        return httpx.Response(201, json={"receipt_file_name":"r.pdf", "receipt_file_size":4,
                            "receipt_content_type":"application/pdf",
                            "receipt_url":"/api/v2/expenses/expense-1/receipt"})
                    return httpx.Response(200, json={"success":True})
                if request.url.path.endswith("/time_entries") and request.method == "GET":
                    assert request.url.params["source"] == "agent"
                    return httpx.Response(200, json={"time_entries":[], "page":1, "total_pages":0})
                if "/time_entries" in request.url.path: return httpx.Response(200, json=entry)
                if request.method == "DELETE": return httpx.Response(200, json={"success":True})
                return httpx.Response(200, json=expense)

            options = {"api_key":"synthetic-wheel-key", "account_id":"synthetic-wheel-account"}
            with httpx.Client(transport=httpx.MockTransport(respond)) as transport:
                with Keito(httpx_client=transport, **options) as client:
                    assert client.expenses.get("expense-1").currency == "GBP"
                    assert client.expenses.update("expense-1", notes=None).units == 1.25
                    receipt = client.expenses.upload_receipt(
                        "expense-1", file=b"%PDF", filename="r.pdf", content_type="application/pdf")
                    assert receipt.receipt_file_size == 4
                    assert client.expenses.download_receipt("expense-1") == b"%PDF"
                    client.expenses.delete_receipt("expense-1")
                    client.expenses.delete("expense-1")
                    assert list(client.time_entries.list(source="agent")) == []
                    timer = client.time_entries.start_timer(
                        project_id="project-1", task_id="task-1", spent_date="2026-10-30")
                    client.time_entries.stop_timer(timer.id)
                    client.time_entries.restart_timer(timer.id)

            async def check_async():
                async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as transport:
                    async with AsyncKeito(
                        base_url="https://app.keito.ai/api/v2/", httpx_client=transport, **options) as client:
                        iterator = client.time_entries.list(source=Source.AGENT)
                        assert not inspect.isawaitable(iterator)
                        assert [row async for row in iterator] == []
                        assert (await client.expenses.get("expense-1")).id == "expense-1"
                        assert await client.expenses.download_receipt("expense-1") == b"%PDF"
            asyncio.run(check_async())
            print("Installed wheel public-contract smoke passed for keito " + keito.__version__)
        """)
        subprocess.run([str(python), "-I", "-c", smoke], cwd=root, check=True)


if __name__ == "__main__":
    main()
