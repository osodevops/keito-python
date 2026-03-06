from __future__ import annotations

from typing import Any, Optional, cast

from keito.core.http_client import AsyncHttpClient, HttpClient
from keito.core.pagination import AsyncPageIterator, SyncPageIterator
from keito.core.raw_response import AsyncWithRawResponse, WithRawResponse
from keito.core.request_options import RequestOptions
from keito.types.client_model import ClientCreate, ClientModel
from keito.types.common import PaymentTerm

_PATH = "/api/v2/clients"


class ClientsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http
        self.with_raw_response = WithRawResponse(self, http)

    def _fetch_page(
        self, *, params: dict[str, Any], request_options: Optional[RequestOptions] = None
    ) -> dict[str, Any]:
        response = self._http.request("GET", _PATH, params=params, request_options=request_options)
        return cast(dict[str, Any], response.json())

    def list(
        self,
        *,
        is_active: Optional[bool] = None,
        updated_since: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> SyncPageIterator[ClientModel]:
        params: dict[str, Any] = {
            "is_active": is_active,
            "updated_since": updated_since,
            "per_page": per_page,
        }
        if page is not None:
            params["page"] = page

        return SyncPageIterator(
            fetch_page=self._fetch_page,
            params=params,
            item_key="clients",
            model_cls=ClientModel,
            request_options=request_options,
        )

    def get(self, id: str, *, request_options: Optional[RequestOptions] = None) -> ClientModel:
        response = self._http.request("GET", f"{_PATH}/{id}", request_options=request_options)
        return ClientModel.model_validate(response.json())

    def create(
        self,
        *,
        name: str,
        address: Optional[str] = None,
        currency: Optional[str] = None,
        payment_terms: Optional[PaymentTerm] = None,
        payment_days: Optional[int] = None,
        tax: Optional[float] = None,
        tax2: Optional[float] = None,
        discount: Optional[float] = None,
        is_active: Optional[bool] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> ClientModel:
        body = ClientCreate(
            name=name,
            address=address,
            currency=currency,
            payment_terms=payment_terms,
            payment_days=payment_days,
            tax=tax,
            tax2=tax2,
            discount=discount,
            is_active=is_active,
        )
        response = self._http.request(
            "POST", _PATH, json=body.model_dump(exclude_none=True), request_options=request_options
        )
        return ClientModel.model_validate(response.json())

    def update(
        self,
        id: str,
        *,
        name: Optional[str] = None,
        address: Optional[str] = None,
        currency: Optional[str] = None,
        payment_terms: Optional[PaymentTerm] = None,
        payment_days: Optional[int] = None,
        tax: Optional[float] = None,
        tax2: Optional[float] = None,
        discount: Optional[float] = None,
        is_active: Optional[bool] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> ClientModel:
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if address is not None:
            body["address"] = address
        if currency is not None:
            body["currency"] = currency
        if payment_terms is not None:
            body["payment_terms"] = payment_terms.value
        if payment_days is not None:
            body["payment_days"] = payment_days
        if tax is not None:
            body["tax"] = tax
        if tax2 is not None:
            body["tax2"] = tax2
        if discount is not None:
            body["discount"] = discount
        if is_active is not None:
            body["is_active"] = is_active

        response = self._http.request("PATCH", f"{_PATH}/{id}", json=body, request_options=request_options)
        return ClientModel.model_validate(response.json())


class AsyncClientsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http
        self.with_raw_response = AsyncWithRawResponse(self, http)

    async def _fetch_page(
        self, *, params: dict[str, Any], request_options: Optional[RequestOptions] = None
    ) -> dict[str, Any]:
        response = await self._http.request("GET", _PATH, params=params, request_options=request_options)
        return cast(dict[str, Any], response.json())

    def list(
        self,
        *,
        is_active: Optional[bool] = None,
        updated_since: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> AsyncPageIterator[ClientModel]:
        params: dict[str, Any] = {
            "is_active": is_active,
            "updated_since": updated_since,
            "per_page": per_page,
        }
        if page is not None:
            params["page"] = page

        return AsyncPageIterator(
            fetch_page=self._fetch_page,
            params=params,
            item_key="clients",
            model_cls=ClientModel,
            request_options=request_options,
        )

    async def get(self, id: str, *, request_options: Optional[RequestOptions] = None) -> ClientModel:
        response = await self._http.request("GET", f"{_PATH}/{id}", request_options=request_options)
        return ClientModel.model_validate(response.json())

    async def create(
        self,
        *,
        name: str,
        address: Optional[str] = None,
        currency: Optional[str] = None,
        payment_terms: Optional[PaymentTerm] = None,
        payment_days: Optional[int] = None,
        tax: Optional[float] = None,
        tax2: Optional[float] = None,
        discount: Optional[float] = None,
        is_active: Optional[bool] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> ClientModel:
        body = ClientCreate(
            name=name,
            address=address,
            currency=currency,
            payment_terms=payment_terms,
            payment_days=payment_days,
            tax=tax,
            tax2=tax2,
            discount=discount,
            is_active=is_active,
        )
        response = await self._http.request(
            "POST", _PATH, json=body.model_dump(exclude_none=True), request_options=request_options
        )
        return ClientModel.model_validate(response.json())

    async def update(
        self,
        id: str,
        *,
        name: Optional[str] = None,
        address: Optional[str] = None,
        currency: Optional[str] = None,
        payment_terms: Optional[PaymentTerm] = None,
        payment_days: Optional[int] = None,
        tax: Optional[float] = None,
        tax2: Optional[float] = None,
        discount: Optional[float] = None,
        is_active: Optional[bool] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> ClientModel:
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if address is not None:
            body["address"] = address
        if currency is not None:
            body["currency"] = currency
        if payment_terms is not None:
            body["payment_terms"] = payment_terms.value
        if payment_days is not None:
            body["payment_days"] = payment_days
        if tax is not None:
            body["tax"] = tax
        if tax2 is not None:
            body["tax2"] = tax2
        if discount is not None:
            body["discount"] = discount
        if is_active is not None:
            body["is_active"] = is_active

        response = await self._http.request("PATCH", f"{_PATH}/{id}", json=body, request_options=request_options)
        return ClientModel.model_validate(response.json())
