from __future__ import annotations

from dataclasses import dataclass
from typing import Generic
from typing import List
from typing import TypeVar

from sqlalchemy.orm import Query

T = TypeVar('T')
V = TypeVar('V')


@dataclass
class PagedData(Generic[T]):

    def __init__(self, query: Query, page_number: int, items_per_page: int):
        self.page_index: int = page_number - 1
        self.page_number: int = page_number
        self.items_per_page: int = items_per_page
        self.total_items: int = query.order_by(None).count()
        self.items: List[T] = query.limit(items_per_page).offset((page_number - 1) * items_per_page).all()
