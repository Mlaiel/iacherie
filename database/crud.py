"""📝 Database CRUD Operations - Core Data Access Layer
======================================================
Module: database/crud.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: CRUD Operations - Production-Ready
Responsibility: Create, Read, Update, Delete operations for all models

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This CRUD module provides data access operations for:
- User management (create, read, update, delete users)
- Content management (upload, retrieve, update, delete content)
- Fingerprint operations (create, match, search fingerprints)
- Generic CRUD operations for any model
"""

import logging
from typing import List, Dict, Any, Optional, Type, Union
from datetime import datetime

# Optional imports for production features
try:
    from sqlalchemy.orm import Session
    from sqlalchemy import and_, or_, desc, asc
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    Session = None

# Configure logging
logger = logging.getLogger(__name__)

class CRUDBase:
    """Base CRUD operations class"""
    
    def __init__(self, model_class, session=None) -> None:
        self.model_class = model_class
        self.session = session
        self.in_memory_store = {}  # Fallback for non-SQLAlchemy environments
        self._next_id = 1
    
    def create(self, obj_data: Dict[str, Any]) -> Any:
        """Create a new object"""
        try:
            if SQLALCHEMY_AVAILABLE and self.session:
                # SQLAlchemy version
                db_obj = self.model_class(**obj_data)
                self.session.add(db_obj)
                self.session.commit()
                self.session.refresh(db_obj)
                logger.info(f"Created {self.model_class.__name__} with data: {obj_data}")
                return db_obj
            else:
                # In-memory version
                obj_data['id'] = self._next_id
                self._next_id += 1
                obj = self.model_class(**obj_data)
                model_name = self.model_class.__name__
                if model_name not in self.in_memory_store:
                    self.in_memory_store[model_name] = {}
                self.in_memory_store[model_name][obj.id] = obj
                logger.info(f"Created {model_name} in memory with ID: {obj.id}")
                return obj
        except Exception as e:
            logger.error(f"Failed to create {self.model_class.__name__}: {e}")
            if SQLALCHEMY_AVAILABLE and self.session:
                self.session.rollback()
            return None
    
    def get(self, obj_id: int) -> Any:
        """Get object by ID"""
        try:
            if SQLALCHEMY_AVAILABLE and self.session:
                # SQLAlchemy version
                obj = self.session.query(self.model_class).filter(self.model_class.id == obj_id).first()
                return obj
            else:
                # In-memory version
                model_name = self.model_class.__name__
                if model_name in self.in_memory_store:
                    return self.in_memory_store[model_name].get(obj_id)
                return None
        except Exception as e:
            logger.error(f"Failed to get {self.model_class.__name__} with ID {obj_id}: {e}")
            return None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Any]:
        """Get all objects with pagination"""
        try:
            if SQLALCHEMY_AVAILABLE and self.session:
                # SQLAlchemy version
                objects = self.session.query(self.model_class).offset(skip).limit(limit).all()
                return objects
            else:
                # In-memory version
                model_name = self.model_class.__name__
                if model_name in self.in_memory_store:
                    all_objects = list(self.in_memory_store[model_name].values())
                    return all_objects[skip:skip + limit]
                return []
        except Exception as e:
            logger.error(f"Failed to get all {self.model_class.__name__}: {e}")
            return []
    
    def update(self, obj_id: int, update_data: Dict[str, Any]) -> Any:
        """Update object by ID"""
        try:
            if SQLALCHEMY_AVAILABLE and self.session:
                # SQLAlchemy version
                obj = self.session.query(self.model_class).filter(self.model_class.id == obj_id).first()
                if obj:
                    for key, value in update_data.items():
                        if hasattr(obj, key):
                            setattr(obj, key, value)
                    if hasattr(obj, 'updated_at'):
                        obj.updated_at = datetime.utcnow()
                    self.session.commit()
                    self.session.refresh(obj)
                    logger.info(f"Updated {self.model_class.__name__} ID {obj_id}")
                    return obj
            else:
                # In-memory version
                model_name = self.model_class.__name__
                if model_name in self.in_memory_store and obj_id in self.in_memory_store[model_name]:
                    obj = self.in_memory_store[model_name][obj_id]
                    obj.update(**update_data)
                    logger.info(f"Updated {model_name} ID {obj_id} in memory")
                    return obj
            return None
        except Exception as e:
            logger.error(f"Failed to update {self.model_class.__name__} ID {obj_id}: {e}")
            if SQLALCHEMY_AVAILABLE and self.session:
                self.session.rollback()
            return None
    
    def delete(self, obj_id: int) -> bool:
        """Delete object by ID"""
        try:
            if SQLALCHEMY_AVAILABLE and self.session:
                # SQLAlchemy version
                obj = self.session.query(self.model_class).filter(self.model_class.id == obj_id).first()
                if obj:
                    self.session.delete(obj)
                    self.session.commit()
                    logger.info(f"Deleted {self.model_class.__name__} ID {obj_id}")
                    return True
            else:
                # In-memory version
                model_name = self.model_class.__name__
                if model_name in self.in_memory_store and obj_id in self.in_memory_store[model_name]:
                    del self.in_memory_store[model_name][obj_id]
                    logger.info(f"Deleted {model_name} ID {obj_id} from memory")
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete {self.model_class.__name__} ID {obj_id}: {e}")
            if SQLALCHEMY_AVAILABLE and self.session:
                self.session.rollback()
            return False
    
    def search(self, filters: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Any]:
        """Search objects with filters"""
        try:
            if SQLALCHEMY_AVAILABLE and self.session:
                # SQLAlchemy version
                query = self.session.query(self.model_class)
                for key, value in filters.items():
                    if hasattr(self.model_class, key):
                        query = query.filter(getattr(self.model_class, key) == value)
                return query.offset(skip).limit(limit).all()
            else:
                # In-memory version
                model_name = self.model_class.__name__
                if model_name not in self.in_memory_store:
                    return []
                
                results = []
                for obj in self.in_memory_store[model_name].values():
                    match = True
                    for key, value in filters.items():
                        if not hasattr(obj, key) or getattr(obj, key) != value:
                            match = False
                            break
                    if match:
                        results.append(obj)
                
                return results[skip:skip + limit]
        except Exception as e:
            logger.error(f"Failed to search {self.model_class.__name__}: {e}")
            return []

# Specific CRUD classes for each model
class UserCRUD(CRUDBase):
    """CRUD operations for User model"""
    
    def get_by_username(self, username -> None: str) -> None:
        """Get user by username"""
        return self.search({"username": username})
    
    def get_by_email(self, email -> None: str) -> None:
        """Get user by email"""
        return self.search({"email": email})
    
    def get_active_users(self) -> None:
        """Get all active users"""
        return self.search({"is_active": True})

class ContentCRUD(CRUDBase):
    """CRUD operations for Content model"""
    
    def get_by_owner(self, owner_id -> None: int) -> None:
        """Get content by owner ID"""
        return self.search({"owner_id": owner_id})
    
    def get_by_type(self, content_type -> None: str) -> None:
        """Get content by type"""
        return self.search({"content_type": content_type})
    
    def get_by_status(self, status -> None: str) -> None:
        """Get content by status"""
        return self.search({"status": status})

class FingerprintCRUD(CRUDBase):
    """CRUD operations for Fingerprint model"""
    
    def get_by_content(self, content_id -> None: int) -> None:
        """Get fingerprints by content ID"""
        return self.search({"content_id": content_id})
    
    def get_by_algorithm(self, algorithm -> None: str) -> None:
        """Get fingerprints by algorithm"""
        return self.search({"algorithm": algorithm})

# CRUD manager class
class CRUDManager:
    """Manages all CRUD operations"""
    
    def __init__(self, session=None) -> None:
        self.session = session
        self._crud_instances = {}
    
    def get_crud(self, model_class) -> CRUDBase:
        """Get CRUD instance for a model"""
        model_name = model_class.__name__
        if model_name not in self._crud_instances:
            # Choose specific CRUD class if available
            if model_name == "User":
                self._crud_instances[model_name] = UserCRUD(model_class, self.session)
            elif model_name == "Content":
                self._crud_instances[model_name] = ContentCRUD(model_class, self.session)
            elif model_name == "Fingerprint":
                self._crud_instances[model_name] = FingerprintCRUD(model_class, self.session)
            else:
                self._crud_instances[model_name] = CRUDBase(model_class, self.session)
        
        return self._crud_instances[model_name]

# Global CRUD manager
_crud_manager = None

def get_crud_manager(session=None) -> CRUDManager:
    """Get the global CRUD manager"""
    global _crud_manager
    if _crud_manager is None:
        _crud_manager = CRUDManager(session)
    return _crud_manager

# Convenience functions
def create_user(user_data -> None: Dict[str, Any], session=None) -> None:
    """Create a new user"""
    from . import models
    crud = get_crud_manager(session).get_crud(models.User)
    return crud.create(user_data)

def get_user(user_id -> None: int, session=None) -> None:
    """Get user by ID"""
    from . import models
    crud = get_crud_manager(session).get_crud(models.User)
    return crud.get(user_id)

def create_content(content_data -> None: Dict[str, Any], session=None) -> None:
    """Create new content"""
    from . import models
    crud = get_crud_manager(session).get_crud(models.Content)
    return crud.create(content_data)

def get_content(content_id -> None: int, session=None) -> None:
    """Get content by ID"""
    from . import models
    crud = get_crud_manager(session).get_crud(models.Content)
    return crud.get(content_id)

def create_fingerprint(fingerprint_data -> None: Dict[str, Any], session=None) -> None:
    """Create new fingerprint"""
    from . import models
    crud = get_crud_manager(session).get_crud(models.Fingerprint)
    return crud.create(fingerprint_data)

def get_crud_info() -> Dict[str, Any]:
    """Get CRUD system information"""
    manager = get_crud_manager()
    return {
        "sqlalchemy_available": SQLALCHEMY_AVAILABLE,
        "crud_instances": list(manager._crud_instances.keys()),
        "has_session": manager.session is not None
    }