from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Generic
from typing import List
from typing import TypeVar

from sqlalchemy.orm import Query

T = TypeVar('T')
V = TypeVar('V')


@dataclass
class PagedData(Generic[T]):

    def __init__(self, base: Query, query: Query, page_number: int, items_per_page: int):
        self.base_items: int = base.count()
        self.page_index: int = page_number - 1
        self.page_number: int = page_number
        self.items_per_page: int = items_per_page
        self.total_items: int = query.order_by(None).count()
        self.page_offset: int = (page_number - 1) * items_per_page
        self.page_start: int = self.page_offset + 1
        self.page_end: int = min(self.page_offset + items_per_page, self.total_items)
        self.total_pages: int = math.ceil(self.total_items / self.items_per_page)
        self.items: List[T] = query.limit(items_per_page).offset(self.page_offset).all()
