from __future__ import annotations

import os
from typing import Optional

import httpx

from keito.core.api_error import KeitoAuthError
from keito.core.http_client import AsyncHttpClient, HttpClient
from keito.helpers.outcomes import AsyncOutcomesHelper, OutcomesHelper
from keito.resources.clients import AsyncClientsResource, ClientsResource
from keito.resources.contacts import AsyncContactsResource, ContactsResource
from keito.resources.expenses import AsyncExpensesResource, ExpensesResource
from keito.resources.invoices import AsyncInvoicesResource, InvoicesResource
from keito.resources.projects import AsyncProjectsResource, ProjectsResource
from keito.resources.reports import AsyncReportsResource, ReportsResource
from keito.resources.tasks import AsyncTasksResource, TasksResource
from keito.resources.time_entries import AsyncTimeEntriesResource, TimeEntriesResource
from keito.resources.users import AsyncUsersResource, UsersResource


class Keito:
    """Synchronous Keito API client."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        account_id: Optional[str] = None,
        base_url: str = "https://app.keito.io",
        timeout: float = 60.0,
        max_retries: int = 2,
        httpx_client: Optional[httpx.Client] = None,
    ) -> None:
        resolved_api_key = api_key or os.environ.get("KEITO_API_KEY")
        resolved_account_id = account_id or os.environ.get("KEITO_ACCOUNT_ID")

        if not resolved_api_key:
            raise KeitoAuthError(
                body={"error": "missing_api_key", "error_description": "No api_key provided and KEITO_API_KEY not set"}
            )
        if not resolved_account_id:
            raise KeitoAuthError(
                body={
                    "error": "missing_account_id",
                    "error_description": "No account_id provided and KEITO_ACCOUNT_ID not set",
                }
            )

        self._http = HttpClient(
            api_key=resolved_api_key,
            account_id=resolved_account_id,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            httpx_client=httpx_client,
        )

        self.time_entries = TimeEntriesResource(self._http)
        self.expenses = ExpensesResource(self._http)
        self.projects = ProjectsResource(self._http)
        self.clients = ClientsResource(self._http)
        self.contacts = ContactsResource(self._http)
        self.tasks = TasksResource(self._http)
        self.users = UsersResource(self._http)
        self.invoices = InvoicesResource(self._http)
        self.reports = ReportsResource(self._http)
        self.outcomes = OutcomesHelper(self.time_entries)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Keito:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncKeito:
    """Asynchronous Keito API client."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        account_id: Optional[str] = None,
        base_url: str = "https://app.keito.io",
        timeout: float = 60.0,
        max_retries: int = 2,
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        resolved_api_key = api_key or os.environ.get("KEITO_API_KEY")
        resolved_account_id = account_id or os.environ.get("KEITO_ACCOUNT_ID")

        if not resolved_api_key:
            raise KeitoAuthError(
                body={"error": "missing_api_key", "error_description": "No api_key provided and KEITO_API_KEY not set"}
            )
        if not resolved_account_id:
            raise KeitoAuthError(
                body={
                    "error": "missing_account_id",
                    "error_description": "No account_id provided and KEITO_ACCOUNT_ID not set",
                }
            )

        self._http = AsyncHttpClient(
            api_key=resolved_api_key,
            account_id=resolved_account_id,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            httpx_client=httpx_client,
        )

        self.time_entries = AsyncTimeEntriesResource(self._http)
        self.expenses = AsyncExpensesResource(self._http)
        self.projects = AsyncProjectsResource(self._http)
        self.clients = AsyncClientsResource(self._http)
        self.contacts = AsyncContactsResource(self._http)
        self.tasks = AsyncTasksResource(self._http)
        self.users = AsyncUsersResource(self._http)
        self.invoices = AsyncInvoicesResource(self._http)
        self.reports = AsyncReportsResource(self._http)
        self.outcomes = AsyncOutcomesHelper(self.time_entries)

    async def close(self) -> None:
        await self._http.close()

    async def __aenter__(self) -> AsyncKeito:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
