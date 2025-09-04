# API Routes initialization
# NOTE: Routes have been consolidated into backend/api/
# Please use the consolidated routers instead:
# - backend.api.core_router for core functionality (auth, content, analytics, monitoring, etc.)
# - backend.api.business_router for business functionality (monetization, payments, collaboration, etc.)

from ...backend.api import core_router, business_router

__all__ = [
    "core_router",
    "business_router"
]

# Legacy imports for backward compatibility (deprecated)
# These will be removed in a future version
import warnings
warnings.warn(
    "Individual route imports from api.routes are deprecated. "
    "Please use consolidated routers from backend.api instead.",
    DeprecationWarning,
    stacklevel=2
)