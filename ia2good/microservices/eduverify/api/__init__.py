"""
EduVerify API Routes
"""
from .routes.content import router as content_router
from .routes.quizzes import router as quizzes_router
from .routes.fact_checking import router as fact_checking_router
from .routes.explanations import router as explanations_router
from .routes.analytics import router as analytics_router

__all__ = [
    "content_router",
    "quizzes_router",
    "fact_checking_router",
    "explanations_router",
    "analytics_router",
]
