#!/usr/bin/env python3
"""
Mock aiohttp pour éviter les erreurs d'import sécurité
"""

class ClientSession:
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        pass
    
    async def get(self, url, **kwargs):
        return MockResponse()
    
    async def post(self, url, **kwargs):
        return MockResponse()

class MockResponse:
    def __init__(self):
        self.status = 200
    
    async def json(self):
        return {"status": "ok", "mock": True}
    
    async def text(self):
        return "Mock response"
