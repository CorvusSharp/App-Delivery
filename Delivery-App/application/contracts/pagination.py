"""
Контракты UC для пагинации (Pydantic v2).
"""
from typing import Generic, TypeVar, List
from pydantic import BaseModel, computed_field

T = TypeVar('T')


class PageRequest(BaseModel):
    """Запрос страницы."""
    page: int = 1
    size: int = 20

    @computed_field  # type: ignore[misc]
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

    @computed_field  # type: ignore[misc]
    @property
    def limit(self) -> int:
        return self.size


class PageResponse(BaseModel, Generic[T]):
    """Ответ со страницей результатов."""
    items: List[T]
    total: int
    page: int
    size: int

    @computed_field  # type: ignore[misc]
    @property
    def total_pages(self) -> int:
        return (self.total + self.size - 1) // self.size

    @computed_field  # type: ignore[misc]
    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @computed_field  # type: ignore[misc]
    @property
    def has_prev(self) -> bool:
        return self.page > 1


class PaginationDTO(BaseModel, Generic[T]):
    """Пагинация для UC."""
    items: List[T]
    total: int
    page: int
    pages: int
    size: int
    has_next: bool
    has_prev: bool
