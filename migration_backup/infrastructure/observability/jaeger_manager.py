"""Jaeger Manager"""
import logging
logger = logging.getLogger(__name__)
class JaegerManager:
    def __init__(self): logger.info("Jaeger manager initialized")
    async def setup_tracing(self, config): return {'status': 'configured'}