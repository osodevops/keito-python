from __future__ import annotations

from typing import Any, Optional

from keito.core.http_client import AsyncHttpClient, HttpClient
from keito.core.pagination import AsyncPageIterator, SyncPageIterator
from keito.core.request_options import RequestOptions
from keito.types.contact import Contact, ContactCreate

_PATH = "/api/v2/contacts"


class ContactsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def _fetch_page(
        self, *, params: dict[str, Any], request_options: Optional[RequestOptions] = None
    ) -> dict[str, Any]:
        response = self._http.request("GET", _PATH, params=params, request_options=request_options)
        return response.json()

    def list(
        self,
        *,
        client_id: Optional[str] = None,
        updated_since: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> SyncPageIterator[Contact]:
        params: dict[str, Any] = {
            "client_id": client_id,
            "updated_since": updated_since,
            "per_page": per_page,
        }
        if page is not None:
            params["page"] = page

        return SyncPageIterator(
            fetch_page=self._fetch_page,
            params=params,
            item_key="contacts",
            model_cls=Contact,
            request_options=request_options,
        )

    def create(
        self,
        *,
        client_id: str,
        first_name: str,
        last_name: Optional[str] = None,
        title: Optional[str] = None,
        email: Optional[str] = None,
        phone_office: Optional[str] = None,
        phone_mobile: Optional[str] = None,
        fax: Optional[str] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> Contact:
        body = ContactCreate(
            client_id=client_id,
            first_name=first_name,
            last_name=last_name,
            title=title,
            email=email,
            phone_office=phone_office,
            phone_mobile=phone_mobile,
            fax=fax,
        )
        response = self._http.request(
            "POST", _PATH, json=body.model_dump(exclude_none=True), request_options=request_options
        )
        return Contact.model_validate(response.json())


class AsyncContactsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def _fetch_page(
        self, *, params: dict[str, Any], request_options: Optional[RequestOptions] = None
    ) -> dict[str, Any]:
        response = await self._http.request("GET", _PATH, params=params, request_options=request_options)
        return response.json()

    def list(
        self,
        *,
        client_id: Optional[str] = None,
        updated_since: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> AsyncPageIterator[Contact]:
        params: dict[str, Any] = {
            "client_id": client_id,
            "updated_since": updated_since,
            "per_page": per_page,
        }
        if page is not None:
            params["page"] = page

        return AsyncPageIterator(
            fetch_page=self._fetch_page,
            params=params,
            item_key="contacts",
            model_cls=Contact,
            request_options=request_options,
        )

    async def create(
        self,
        *,
        client_id: str,
        first_name: str,
        last_name: Optional[str] = None,
        title: Optional[str] = None,
        email: Optional[str] = None,
        phone_office: Optional[str] = None,
        phone_mobile: Optional[str] = None,
        fax: Optional[str] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> Contact:
        body = ContactCreate(
            client_id=client_id,
            first_name=first_name,
            last_name=last_name,
            title=title,
            email=email,
            phone_office=phone_office,
            phone_mobile=phone_mobile,
            fax=fax,
        )
        response = await self._http.request(
            "POST", _PATH, json=body.model_dump(exclude_none=True), request_options=request_options
        )
        return Contact.model_validate(response.json())
