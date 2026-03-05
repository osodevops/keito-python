from __future__ import annotations

from typing import Any, Callable, Awaitable, Generic, Iterator, List, Optional, TypeVar

from keito.core.request_options import RequestOptions

T = TypeVar("T")


class SyncPageIterator(Generic[T]):
    """Lazily paginates through all pages, yielding individual items."""

    def __init__(
        self,
        *,
        fetch_page: Callable[..., dict[str, Any]],
        params: dict[str, Any],
        item_key: str,
        model_cls: type[T],
        request_options: Optional[RequestOptions] = None,
    ) -> None:
        self._fetch_page = fetch_page
        self._params = dict(params)
        self._item_key = item_key
        self._model_cls = model_cls
        self._request_options = request_options
        self._current_page = 0
        self._total_pages: Optional[int] = None
        self._buffer: List[T] = []
        self._buffer_index = 0
        self._exhausted = False

        # Pagination metadata (set after first page fetch)
        self.total_entries: Optional[int] = None
        self.total_pages: Optional[int] = None
        self.per_page: Optional[int] = None
        self.page: Optional[int] = None
        self.items: List[T] = []

    def _fetch_next_page(self) -> bool:
        if self._exhausted:
            return False

        if self._total_pages is not None and self._current_page >= self._total_pages:
            self._exhausted = True
            return False

        self._current_page += 1
        self._params["page"] = self._current_page

        data = self._fetch_page(params=self._params, request_options=self._request_options)

        self._total_pages = data.get("total_pages", 1)
        self.total_entries = data.get("total_entries")
        self.total_pages = self._total_pages
        self.per_page = data.get("per_page")
        self.page = self._current_page

        raw_items = data.get(self._item_key, [])
        page_items = [self._model_cls.model_validate(item) if isinstance(item, dict) else item for item in raw_items]

        # Store items for direct access on first page
        if self._current_page == 1:
            self.items = page_items

        self._buffer = page_items
        self._buffer_index = 0

        if not page_items:
            self._exhausted = True
            return False

        if self._current_page >= self._total_pages:
            self._exhausted = True

        return True

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        while self._buffer_index >= len(self._buffer):
            if not self._fetch_next_page():
                raise StopIteration
        item = self._buffer[self._buffer_index]
        self._buffer_index += 1
        return item


class AsyncPageIterator(Generic[T]):
    """Async variant — lazily paginates through all pages, yielding individual items."""

    def __init__(
        self,
        *,
        fetch_page: Callable[..., Awaitable[dict[str, Any]]],
        params: dict[str, Any],
        item_key: str,
        model_cls: type[T],
        request_options: Optional[RequestOptions] = None,
    ) -> None:
        self._fetch_page = fetch_page
        self._params = dict(params)
        self._item_key = item_key
        self._model_cls = model_cls
        self._request_options = request_options
        self._current_page = 0
        self._total_pages: Optional[int] = None
        self._buffer: List[T] = []
        self._buffer_index = 0
        self._exhausted = False

        self.total_entries: Optional[int] = None
        self.total_pages: Optional[int] = None
        self.per_page: Optional[int] = None
        self.page: Optional[int] = None
        self.items: List[T] = []

    async def _fetch_next_page(self) -> bool:
        if self._exhausted:
            return False

        if self._total_pages is not None and self._current_page >= self._total_pages:
            self._exhausted = True
            return False

        self._current_page += 1
        self._params["page"] = self._current_page

        data = await self._fetch_page(params=self._params, request_options=self._request_options)

        self._total_pages = data.get("total_pages", 1)
        self.total_entries = data.get("total_entries")
        self.total_pages = self._total_pages
        self.per_page = data.get("per_page")
        self.page = self._current_page

        raw_items = data.get(self._item_key, [])
        page_items = [self._model_cls.model_validate(item) if isinstance(item, dict) else item for item in raw_items]

        if self._current_page == 1:
            self.items = page_items

        self._buffer = page_items
        self._buffer_index = 0

        if not page_items:
            self._exhausted = True
            return False

        if self._current_page >= self._total_pages:
            self._exhausted = True

        return True

    def __aiter__(self) -> AsyncPageIterator[T]:
        return self

    async def __anext__(self) -> T:
        while self._buffer_index >= len(self._buffer):
            if not await self._fetch_next_page():
                raise StopAsyncIteration
        item = self._buffer[self._buffer_index]
        self._buffer_index += 1
        return item
