"""
Dependency Fallbacks for Ainflue Platform
Provides basic functionality when optional dependencies are missing.
"""

class MockSQLAlchemy:
    """Mock SQLAlchemy for when not available"""
    class Base:
        pass
    
    class Column:
        def __init__(self, *args, **kwargs):
            pass
    
    class String:
        def __init__(self, *args, **kwargs):
            pass
    
    class Integer:
        def __init__(self, *args, **kwargs):
            pass

class MockFastAPI:
    """Mock FastAPI for when not available"""
    def __init__(self):
        pass

# Export mocks
sqlalchemy = MockSQLAlchemy()
fastapi = MockFastAPI()
