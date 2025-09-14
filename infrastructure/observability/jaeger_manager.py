"""Jaeger Manager"""
import asyncio

import logging
logger = logging.getLogger(__name__)
class JaegerManager:
    """JaegerManager: class implementation"""
    def __init__(self) -> None: logger.info("Jaeger manager initialized")
    async def setup_tracing(self, config) -> None: return {'status': 'configured'}