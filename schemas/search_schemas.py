"""IA Influencer Agent Platform - Search and Filter Schemas
Advanced search and filtering patterns for content discovery.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive search and filtering schemas:
- Advanced search queries with operators
- Filtering patterns for different content types
- Faceted search support
- Elasticsearch integration
- Real-time search suggestions
"""

from typing import Optional, List, Dict, Any, Union, Set
from enum import Enum
from datetime import datetime, date
from pydantic import BaseModel, Field, validator, model_validator
from .base import BaseSchema, UUIDSchema, TimestampSchema
from .primitive_types import TagType, LanguageCodeType, CountryCodeType


class SearchOperator(str, Enum):
    """Search query operators."""
    AND = "and"
    OR = "or"
    NOT = "not"
    PHRASE = "phrase"
    WILDCARD = "wildcard"
    FUZZY = "fuzzy"
    REGEX = "regex"
    RANGE = "range"
    EXISTS = "exists"
    NEAR = "near"


class SortDirection(str, Enum):
    """Sort direction options."""
    ASC = "asc"
    DESC = "desc"


class SearchScope(str, Enum):
    """Search scope definitions."""
    ALL = "all"
    TITLE = "title"
    DESCRIPTION = "description"
    CONTENT = "content"
    TAGS = "tags"
    METADATA = "metadata"
    AUTHOR = "author"
    COMMENTS = "comments"


class FilterType(str, Enum):
    """Filter type classifications."""
    EXACT = "exact"
    RANGE = "range"
    LIST = "list"
    BOOLEAN = "boolean"
    DATE_RANGE = "date_range"
    NUMERIC_RANGE = "numeric_range"
    TEXT_MATCH = "text_match"
    GEO_DISTANCE = "geo_distance"


class AggregationType(str, Enum):
    """Aggregation types for faceted search."""
    TERMS = "terms"
    RANGE = "range"
    DATE_HISTOGRAM = "date_histogram"
    NESTED = "nested"
    FILTER = "filter"
    STATS = "stats"
    CARDINALITY = "cardinality"


class SearchQuery(BaseSchema):
    """Basic search query structure."""
    
    query: str = Field(..., min_length=1, max_length=1000, description="Search query string")
    operator: SearchOperator = Field(SearchOperator.AND, description="Query operator")
    scope: List[SearchScope] = Field(default=[SearchScope.ALL], description="Search scopes")
    boost: float = Field(1.0, ge=0.1, le=10.0, description="Query boost factor")
    fuzzy: bool = Field(False, description="Enable fuzzy matching")
    fuzzy_distance: int = Field(2, ge=1, le=5, description="Fuzzy edit distance")
    
    @validator('query')
    def validate_query(cls, v) -> None:
        """Validate search query."""
        # Remove excessive whitespace
        v = ' '.join(v.split())
        
        # Check for balanced quotes
        if v.count('"') % 2 != 0:
            raise ValueError('Unbalanced quotes in search query')
        
        return v


class AdvancedSearchQuery(BaseSchema):
    """Advanced search query with multiple conditions."""
    
    must: List[SearchQuery] = Field(default=[], description="Must match conditions")
    should: List[SearchQuery] = Field(default=[], description="Should match conditions")
    must_not: List[SearchQuery] = Field(default=[], description="Must not match conditions")
    minimum_should_match: Optional[int] = Field(None, ge=1, description="Minimum should matches")
    boost: float = Field(1.0, ge=0.1, le=10.0, description="Overall query boost")
    
    @model_validator(mode='after')
    def validate_conditions(self) -> None:
        """Validate that at least one condition is provided."""
        if not self.must and not self.should and not self.must_not:
            raise ValueError('At least one search condition must be provided')
        
        return self


class FilterCondition(BaseSchema):
    """Individual filter condition."""
    
    field: str = Field(..., description="Field name to filter on")
    filter_type: FilterType = Field(..., description="Type of filter")
    value: Any = Field(..., description="Filter value")
    operator: Optional[SearchOperator] = Field(None, description="Filter operator")
    case_sensitive: bool = Field(False, description="Case sensitive matching")
    negate: bool = Field(False, description="Negate the filter condition")


class DateRangeFilter(BaseSchema):
    """Date range filter condition."""
    
    field: str = Field(..., description="Date field name")
    start_date: Optional[datetime] = Field(None, description="Range start date")
    end_date: Optional[datetime] = Field(None, description="Range end date")
    relative_range: Optional[str] = Field(None, description="Relative range (e.g., 'last_7_days')")
    include_start: bool = Field(True, description="Include start date")
    include_end: bool = Field(True, description="Include end date")
    
    @model_validator(mode='after')
    def validate_range(self) -> None:
        """Validate date range."""
        if not self.start_date and not self.end_date and not self.relative_range:
            raise ValueError('Either date range or relative range must be specified')
        
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError('Start date must be before end date')
        
        return self


class NumericRangeFilter(BaseSchema):
    """Numeric range filter condition."""
    
    field: str = Field(..., description="Numeric field name")
    min_value: Optional[float] = Field(None, description="Minimum value")
    max_value: Optional[float] = Field(None, description="Maximum value")
    include_min: bool = Field(True, description="Include minimum value")
    include_max: bool = Field(True, description="Include maximum value")
    
    @model_validator(mode='after')
    def validate_range(self) -> None:
        """Validate numeric range."""
        if self.min_value is None and self.max_value is None:
            raise ValueError('At least one range boundary must be specified')
        
        if self.min_value is not None and self.max_value is not None and self.min_value > self.max_value:
            raise ValueError('Minimum value must be less than maximum value')
        
        return self


class GeoDistanceFilter(BaseSchema):
    """Geographic distance filter."""
    
    field: str = Field(..., description="Geographic field name")
    center_lat: float = Field(..., ge=-90, le=90, description="Center latitude")
    center_lon: float = Field(..., ge=-180, le=180, description="Center longitude")
    distance: float = Field(..., gt=0, description="Distance value")
    distance_unit: str = Field("km", pattern="^(m|km|mi|ft)$", description="Distance unit")


class SortCriteria(BaseSchema):
    """Sort criteria for search results."""
    
    field: str = Field(..., description="Field to sort by")
    direction: SortDirection = Field(SortDirection.ASC, description="Sort direction")
    mode: Optional[str] = Field(None, description="Sort mode for array fields")
    missing: Optional[str] = Field(None, description="How to handle missing values")
    boost: float = Field(1.0, ge=0.1, le=10.0, description="Sort boost factor")


class FacetDefinition(BaseSchema):
    """Facet definition for aggregated search results."""
    
    name: str = Field(..., description="Facet name")
    field: str = Field(..., description="Field to aggregate on")
    aggregation_type: AggregationType = Field(..., description="Type of aggregation")
    size: int = Field(10, ge=1, le=1000, description="Number of facet values to return")
    min_doc_count: int = Field(1, ge=0, description="Minimum document count for facet values")
    missing_bucket: bool = Field(False, description="Include bucket for missing values")
    order_by: str = Field("count", description="Facet ordering criteria")
    order_direction: SortDirection = Field(SortDirection.DESC, description="Facet order direction")


class SearchFilter(BaseSchema):
    """Complete search filter configuration."""
    
    conditions: List[FilterCondition] = Field(default=[], description="Filter conditions")
    date_ranges: List[DateRangeFilter] = Field(default=[], description="Date range filters")
    numeric_ranges: List[NumericRangeFilter] = Field(default=[], description="Numeric range filters")
    geo_filters: List[GeoDistanceFilter] = Field(default=[], description="Geographic filters")
    tags: List[TagType] = Field(default=[], description="Tag filters")
    categories: List[str] = Field(default=[], description="Category filters")
    languages: List[LanguageCodeType] = Field(default=[], description="Language filters")
    countries: List[CountryCodeType] = Field(default=[], description="Country filters")


class SearchRequest(BaseSchema):
    """Complete search request."""
    
    query: Optional[Union[SearchQuery, AdvancedSearchQuery]] = Field(None, description="Search query")
    filters: Optional[SearchFilter] = Field(None, description="Search filters")
    sort: List[SortCriteria] = Field(default=[], description="Sort criteria")
    facets: List[FacetDefinition] = Field(default=[], description="Facet definitions")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    include_highlights: bool = Field(False, description="Include search highlights")
    include_score: bool = Field(False, description="Include relevance scores")
    track_total_hits: bool = Field(True, description="Track total hit count")
    timeout: int = Field(30, ge=1, le=300, description="Search timeout in seconds")
    
    @model_validator(mode='after')
    def validate_request(self) -> None:
        """Validate search request."""
        if not self.query and not self.filters:
            raise ValueError('Either query or filters must be provided')
        
        return self


class SearchHighlight(BaseSchema):
    """Search result highlight."""
    
    field: str = Field(..., description="Highlighted field")
    fragments: List[str] = Field(..., description="Highlighted text fragments")
    matched_terms: List[str] = Field(default=[], description="Matched search terms")


class SearchResult(UUIDSchema, TimestampSchema):
    """Individual search result item."""
    
    title: str = Field(..., description="Result title")
    description: Optional[str] = Field(None, description="Result description")
    content_type: str = Field(..., description="Type of content")
    author: Optional[str] = Field(None, description="Content author")
    url: Optional[str] = Field(None, description="Result URL")
    thumbnail: Optional[str] = Field(None, description="Thumbnail URL")
    score: Optional[float] = Field(None, description="Relevance score")
    highlights: List[SearchHighlight] = Field(default=[], description="Search highlights")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")


class FacetValue(BaseSchema):
    """Individual facet value."""
    
    value: str = Field(..., description="Facet value")
    count: int = Field(..., ge=0, description="Document count")
    selected: bool = Field(False, description="Whether this facet is selected")


class SearchFacet(BaseSchema):
    """Search facet with values."""
    
    name: str = Field(..., description="Facet name")
    display_name: str = Field(..., description="Display name")
    field: str = Field(..., description="Field name")
    values: List[FacetValue] = Field(..., description="Facet values")
    total_values: int = Field(..., ge=0, description="Total number of values")
    has_more: bool = Field(False, description="Whether there are more values")


class SearchResponse(BaseSchema):
    """Complete search response."""
    
    query: Optional[str] = Field(None, description="Executed query")
    results: List[SearchResult] = Field(..., description="Search results")
    facets: List[SearchFacet] = Field(default=[], description="Search facets")
    total_hits: int = Field(..., ge=0, description="Total number of hits")
    max_score: Optional[float] = Field(None, description="Maximum relevance score")
    page: int = Field(..., ge=1, description="Current page")
    page_size: int = Field(..., ge=1, description="Items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    execution_time: float = Field(..., ge=0, description="Execution time in milliseconds")
    suggestions: List[str] = Field(default=[], description="Search suggestions")
    
    @validator('total_pages', always=True)
    def calculate_total_pages(cls, v, values) -> None:
        """Calculate total pages from total hits and page size."""
        total_hits = values.get('total_hits', 0)
        page_size = values.get('page_size', 20)
        return (total_hits + page_size - 1) // page_size if total_hits > 0 else 0


class SearchSuggestion(BaseSchema):
    """Search query suggestion."""
    
    text: str = Field(..., description="Suggested text")
    score: float = Field(..., ge=0, description="Suggestion score")
    highlight: Optional[str] = Field(None, description="Highlighted suggestion")
    category: Optional[str] = Field(None, description="Suggestion category")


class SearchAutoComplete(BaseSchema):
    """Auto-complete search response."""
    
    query: str = Field(..., description="Original query")
    suggestions: List[SearchSuggestion] = Field(..., description="Auto-complete suggestions")
    popular_searches: List[str] = Field(default=[], description="Popular search terms")
    recent_searches: List[str] = Field(default=[], description="Recent user searches")


class SavedSearch(UUIDSchema, TimestampSchema):
    """Saved search configuration."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Search name")
    description: Optional[str] = Field(None, max_length=500, description="Search description")
    user_id: str = Field(..., description="User who saved the search")
    search_request: SearchRequest = Field(..., description="Saved search request")
    is_alert: bool = Field(False, description="Whether to send alerts for new results")
    alert_frequency: Optional[str] = Field(None, description="Alert frequency")
    is_public: bool = Field(False, description="Whether search is public")
    tags: List[TagType] = Field(default=[], description="Search tags")


class SearchAnalytics(UUIDSchema, TimestampSchema):
    """Search analytics and metrics."""
    
    query: str = Field(..., description="Search query")
    user_id: Optional[str] = Field(None, description="User who performed search")
    results_count: int = Field(..., ge=0, description="Number of results returned")
    execution_time: float = Field(..., ge=0, description="Search execution time")
    clicked_results: List[str] = Field(default=[], description="IDs of clicked results")
    session_id: Optional[str] = Field(None, description="Search session ID")
    ip_address: Optional[str] = Field(None, description="User IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    filters_applied: Dict[str, Any] = Field(default={}, description="Applied filters")
    facets_selected: List[str] = Field(default=[], description="Selected facets")


class SearchConfiguration(BaseSchema):
    """Search engine configuration."""
    
    index_name: str = Field(..., description="Elasticsearch index name")
    default_operator: SearchOperator = Field(SearchOperator.AND, description="Default query operator")
    default_page_size: int = Field(20, ge=1, le=100, description="Default page size")
    max_page_size: int = Field(100, ge=1, le=1000, description="Maximum page size")
    highlight_enabled: bool = Field(True, description="Enable result highlighting")
    facets_enabled: bool = Field(True, description="Enable faceted search")
    auto_complete_enabled: bool = Field(True, description="Enable auto-complete")
    search_timeout: int = Field(30, ge=1, le=300, description="Search timeout in seconds")
    boost_settings: Dict[str, float] = Field(default={}, description="Field boost settings")
    analyzer_settings: Dict[str, str] = Field(default={}, description="Field analyzer settings")


class ContentSearchIndex(BaseSchema):
    """Content search index definition."""
    
    content_id: str = Field(..., description="Content identifier")
    title: str = Field(..., description="Content title")
    description: Optional[str] = Field(None, description="Content description")
    content: str = Field(..., description="Full content text")
    content_type: str = Field(..., description="Type of content")
    author_id: str = Field(..., description="Author identifier")
    author_name: str = Field(..., description="Author name")
    category: str = Field(..., description="Content category")
    subcategory: Optional[str] = Field(None, description="Content subcategory")
    tags: List[TagType] = Field(default=[], description="Content tags")
    language: LanguageCodeType = Field(..., description="Content language")
    country: Optional[CountryCodeType] = Field(None, description="Content country")
    publication_date: datetime = Field(..., description="Publication date")
    last_modified: datetime = Field(..., description="Last modification date")
    view_count: int = Field(0, ge=0, description="View count")
    like_count: int = Field(0, ge=0, description="Like count")
    comment_count: int = Field(0, ge=0, description="Comment count")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating")
    duration: Optional[int] = Field(None, ge=0, description="Content duration in seconds")
    file_size: Optional[int] = Field(None, ge=0, description="File size in bytes")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")
    is_featured: bool = Field(False, description="Whether content is featured")
    is_premium: bool = Field(False, description="Whether content is premium")
    visibility: str = Field("public", pattern="^(public|private|unlisted)$", description="Content visibility")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }