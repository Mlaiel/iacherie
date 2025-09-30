"""
📄 Pagination Pattern Schemas
Enterprise pagination system for efficient data browsing

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional, Union, Generic, TypeVar
from pydantic import BaseModel, Field, validator
from enum import Enum
import math
from datetime import datetime

T = TypeVar('T')


class SortDirection(str, Enum):
    """Sort direction options"""
    ASC = "asc"
    DESC = "desc"


class PaginationType(str, Enum):
    """Pagination implementation types"""
    OFFSET = "offset"          # Traditional offset-based pagination
    CURSOR = "cursor"          # Cursor-based pagination for large datasets
    KEYSET = "keyset"         # Keyset pagination for optimal performance
    HYBRID = "hybrid"         # Hybrid approach combining multiple methods


class PaginationRequest(BaseModel):
    """Base pagination request schema"""
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Number of items per page")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_direction: SortDirection = Field(default=SortDirection.ASC, description="Sort direction")
    
    @validator('page_size')
    def validate_page_size(cls, v):
        """Validate page size limits"""
        if v > 100:
            raise ValueError("Page size cannot exceed 100 items")
        return v


class OffsetPaginationRequest(PaginationRequest):
    """Offset-based pagination request"""
    offset: Optional[int] = Field(None, ge=0, description="Number of items to skip")
    
    @validator('offset')
    def validate_offset(cls, v, values):
        """Calculate offset from page if not provided"""
        if v is None and 'page' in values and 'page_size' in values:
            return (values['page'] - 1) * values['page_size']
        return v


class CursorPaginationRequest(BaseModel):
    """Cursor-based pagination request"""
    cursor: Optional[str] = Field(None, description="Cursor for pagination")
    limit: int = Field(default=20, ge=1, le=100, description="Number of items to return")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_direction: SortDirection = Field(default=SortDirection.ASC, description="Sort direction")


class KeysetPaginationRequest(BaseModel):
    """Keyset pagination request for high-performance scenarios"""
    last_key: Optional[Union[str, int, float]] = Field(None, description="Last key from previous page")
    limit: int = Field(default=20, ge=1, le=100, description="Number of items to return")
    sort_by: str = Field(..., description="Field to sort by (required for keyset)")
    sort_direction: SortDirection = Field(default=SortDirection.ASC, description="Sort direction")


class PaginationMetadata(BaseModel):
    """Pagination metadata information"""
    total_items: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    current_page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Items per page")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    start_index: int = Field(..., ge=0, description="Start index of current page items")
    end_index: int = Field(..., ge=0, description="End index of current page items")


class PaginationLinks(BaseModel):
    """Pagination navigation links"""
    first: Optional[str] = Field(None, description="URL to first page")
    previous: Optional[str] = Field(None, description="URL to previous page")
    next: Optional[str] = Field(None, description="URL to next page")
    last: Optional[str] = Field(None, description="URL to last page")
    self: str = Field(..., description="URL to current page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema"""
    items: List[T] = Field(..., description="Page items")
    metadata: PaginationMetadata = Field(..., description="Pagination metadata")
    links: Optional[PaginationLinks] = Field(None, description="Pagination links")
    request_info: Dict[str, Any] = Field(default_factory=dict, description="Original request info")


class CursorPaginationMetadata(BaseModel):
    """Cursor pagination metadata"""
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    next_cursor: Optional[str] = Field(None, description="Cursor for next page")
    previous_cursor: Optional[str] = Field(None, description="Cursor for previous page")
    total_count: Optional[int] = Field(None, description="Total count if available")
    page_size: int = Field(..., description="Requested page size")


class CursorPaginatedResponse(BaseModel, Generic[T]):
    """Cursor-based paginated response"""
    items: List[T] = Field(..., description="Page items")
    metadata: CursorPaginationMetadata = Field(..., description="Cursor pagination metadata")
    links: Optional[PaginationLinks] = Field(None, description="Pagination links")


class KeysetPaginationMetadata(BaseModel):
    """Keyset pagination metadata"""
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    next_key: Optional[Union[str, int, float]] = Field(None, description="Key for next page")
    previous_key: Optional[Union[str, int, float]] = Field(None, description="Key for previous page")
    page_size: int = Field(..., description="Requested page size")
    sort_field: str = Field(..., description="Field used for sorting")
    sort_direction: SortDirection = Field(..., description="Sort direction")


class KeysetPaginatedResponse(BaseModel, Generic[T]):
    """Keyset-based paginated response"""
    items: List[T] = Field(..., description="Page items")
    metadata: KeysetPaginationMetadata = Field(..., description="Keyset pagination metadata")
    links: Optional[PaginationLinks] = Field(None, description="Pagination links")


class PaginationConfig(BaseModel):
    """Pagination configuration settings"""
    default_page_size: int = Field(default=20, ge=1, le=100)
    max_page_size: int = Field(default=100, ge=1)
    default_sort_direction: SortDirection = Field(default=SortDirection.ASC)
    enable_total_count: bool = Field(default=True, description="Whether to calculate total count")
    enable_links: bool = Field(default=True, description="Whether to generate pagination links")
    cursor_field: str = Field(default="id", description="Default field for cursor pagination")
    keyset_field: str = Field(default="created_at", description="Default field for keyset pagination")


class SearchPaginationRequest(PaginationRequest):
    """Pagination request with search capabilities"""
    search_query: Optional[str] = Field(None, description="Search query string")
    search_fields: List[str] = Field(default_factory=list, description="Fields to search in")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Additional filters")
    facets: List[str] = Field(default_factory=list, description="Facet fields for aggregation")


class SearchFacet(BaseModel):
    """Search facet for aggregated results"""
    field: str = Field(..., description="Facet field name")
    values: List[Dict[str, Union[str, int]]] = Field(..., description="Facet values with counts")
    total_count: int = Field(..., description="Total items in this facet")


class SearchPaginatedResponse(PaginatedResponse[T]):
    """Paginated response with search results"""
    search_metadata: Dict[str, Any] = Field(default_factory=dict, description="Search-specific metadata")
    facets: List[SearchFacet] = Field(default_factory=list, description="Search facets")
    search_time_ms: float = Field(default=0.0, description="Search execution time in milliseconds")
    total_hits: int = Field(default=0, description="Total search hits")


class InfiniteScrollRequest(BaseModel):
    """Infinite scroll pagination request"""
    cursor: Optional[str] = Field(None, description="Cursor for next batch")
    batch_size: int = Field(default=10, ge=1, le=50, description="Number of items per batch")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_direction: SortDirection = Field(default=SortDirection.DESC, description="Sort direction")


class InfiniteScrollResponse(BaseModel, Generic[T]):
    """Infinite scroll response"""
    items: List[T] = Field(..., description="Batch items")
    next_cursor: Optional[str] = Field(None, description="Cursor for next batch")
    has_more: bool = Field(..., description="Whether more items are available")
    batch_info: Dict[str, Any] = Field(default_factory=dict, description="Batch metadata")


class PaginationBuilder:
    """Builder class for creating pagination responses"""
    
    def __init__(self, config: Optional[PaginationConfig] = None):
        self.config = config or PaginationConfig()
    
    def build_offset_pagination(
        self,
        items: List[T],
        request: OffsetPaginationRequest,
        total_items: int,
        base_url: Optional[str] = None
    ) -> PaginatedResponse[T]:
        """Build offset-based paginated response"""
        
        # Calculate pagination metadata
        total_pages = math.ceil(total_items / request.page_size) if total_items > 0 else 1
        current_page = request.page
        has_next = current_page < total_pages
        has_previous = current_page > 1
        start_index = (current_page - 1) * request.page_size
        end_index = min(start_index + len(items) - 1, total_items - 1)
        
        metadata = PaginationMetadata(
            total_items=total_items,
            total_pages=total_pages,
            current_page=current_page,
            page_size=request.page_size,
            has_next=has_next,
            has_previous=has_previous,
            start_index=start_index,
            end_index=end_index
        )
        
        # Build pagination links if base URL provided
        links = None
        if base_url and self.config.enable_links:
            links = self._build_offset_links(request, total_pages, base_url)
        
        return PaginatedResponse(
            items=items,
            metadata=metadata,
            links=links,
            request_info={
                "page": request.page,
                "page_size": request.page_size,
                "sort_by": request.sort_by,
                "sort_direction": request.sort_direction
            }
        )
    
    def build_cursor_pagination(
        self,
        items: List[T],
        request: CursorPaginationRequest,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        total_count: Optional[int] = None,
        base_url: Optional[str] = None
    ) -> CursorPaginatedResponse[T]:
        """Build cursor-based paginated response"""
        
        has_next = next_cursor is not None
        has_previous = previous_cursor is not None
        
        metadata = CursorPaginationMetadata(
            has_next=has_next,
            has_previous=has_previous,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            total_count=total_count,
            page_size=request.limit
        )
        
        # Build pagination links if base URL provided
        links = None
        if base_url and self.config.enable_links:
            links = self._build_cursor_links(request, next_cursor, previous_cursor, base_url)
        
        return CursorPaginatedResponse(
            items=items,
            metadata=metadata,
            links=links
        )
    
    def build_keyset_pagination(
        self,
        items: List[T],
        request: KeysetPaginationRequest,
        next_key: Optional[Union[str, int, float]] = None,
        previous_key: Optional[Union[str, int, float]] = None,
        base_url: Optional[str] = None
    ) -> KeysetPaginatedResponse[T]:
        """Build keyset-based paginated response"""
        
        has_next = next_key is not None
        has_previous = previous_key is not None
        
        metadata = KeysetPaginationMetadata(
            has_next=has_next,
            has_previous=has_previous,
            next_key=next_key,
            previous_key=previous_key,
            page_size=request.limit,
            sort_field=request.sort_by,
            sort_direction=request.sort_direction
        )
        
        # Build pagination links if base URL provided
        links = None
        if base_url and self.config.enable_links:
            links = self._build_keyset_links(request, next_key, previous_key, base_url)
        
        return KeysetPaginatedResponse(
            items=items,
            metadata=metadata,
            links=links
        )
    
    def _build_offset_links(
        self,
        request: OffsetPaginationRequest,
        total_pages: int,
        base_url: str
    ) -> PaginationLinks:
        """Build pagination links for offset pagination"""
        
        def build_url(page: int) -> str:
            params = f"page={page}&page_size={request.page_size}"
            if request.sort_by:
                params += f"&sort_by={request.sort_by}&sort_direction={request.sort_direction}"
            return f"{base_url}?{params}"
        
        return PaginationLinks(
            first=build_url(1),
            previous=build_url(request.page - 1) if request.page > 1 else None,
            next=build_url(request.page + 1) if request.page < total_pages else None,
            last=build_url(total_pages),
            self=build_url(request.page)
        )
    
    def _build_cursor_links(
        self,
        request: CursorPaginationRequest,
        next_cursor: Optional[str],
        previous_cursor: Optional[str],
        base_url: str
    ) -> PaginationLinks:
        """Build pagination links for cursor pagination"""
        
        def build_url(cursor: Optional[str]) -> str:
            params = f"limit={request.limit}"
            if cursor:
                params += f"&cursor={cursor}"
            if request.sort_by:
                params += f"&sort_by={request.sort_by}&sort_direction={request.sort_direction}"
            return f"{base_url}?{params}"
        
        return PaginationLinks(
            first=build_url(None),
            previous=build_url(previous_cursor) if previous_cursor else None,
            next=build_url(next_cursor) if next_cursor else None,
            last=None,  # Not applicable for cursor pagination
            self=build_url(request.cursor)
        )
    
    def _build_keyset_links(
        self,
        request: KeysetPaginationRequest,
        next_key: Optional[Union[str, int, float]],
        previous_key: Optional[Union[str, int, float]],
        base_url: str
    ) -> PaginationLinks:
        """Build pagination links for keyset pagination"""
        
        def build_url(key: Optional[Union[str, int, float]]) -> str:
            params = f"limit={request.limit}&sort_by={request.sort_by}&sort_direction={request.sort_direction}"
            if key is not None:
                params += f"&last_key={key}"
            return f"{base_url}?{params}"
        
        return PaginationLinks(
            first=build_url(None),
            previous=build_url(previous_key) if previous_key is not None else None,
            next=build_url(next_key) if next_key is not None else None,
            last=None,  # Not applicable for keyset pagination
            self=build_url(request.last_key)
        )


# Export classes for external use
__all__ = [
    'SortDirection',
    'PaginationType',
    'PaginationRequest',
    'OffsetPaginationRequest',
    'CursorPaginationRequest',
    'KeysetPaginationRequest',
    'PaginationMetadata',
    'PaginationLinks',
    'PaginatedResponse',
    'CursorPaginationMetadata',
    'CursorPaginatedResponse',
    'KeysetPaginationMetadata',
    'KeysetPaginatedResponse',
    'PaginationConfig',
    'SearchPaginationRequest',
    'SearchFacet',
    'SearchPaginatedResponse',
    'InfiniteScrollRequest',
    'InfiniteScrollResponse',
    'PaginationBuilder'
]