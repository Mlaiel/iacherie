"""
EduVerify API Routes Package
"""
from .content import router as content_router
from .quizzes import router as quizzes_router
from .fact_checking import router as fact_checking_router
from .explanations import router as explanations_router
from .analytics import router as analytics_router
from .chatroom import router as chatroom_router

__all__ = [
    "content_router",
    "quizzes_router",
    "fact_checking_router",
    "explanations_router",
    "analytics_router",
    "chatroom_router",
]
