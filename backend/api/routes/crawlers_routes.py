"""
🕷️ CRAWLERS ROUTES - Complete Implementation
============================================
ALL 30 endpoints for crawler management, results, scheduling
Author: Fahed Mlaiel
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

router = APIRouter(prefix="/crawlers", tags=["Crawlers"])

# ============================================================================
# MODELS
# ============================================================================

class CrawlerType(str, Enum):
    WEB = "web"
    API = "api"
    SOCIAL = "social"
    NEWS = "news"
    ECOMMERCE = "ecommerce"

class CrawlerStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"

# ============================================================================
# CRAWLER MANAGEMENT
# ============================================================================

@router.get("/")
async def list_crawlers():
    """Get all crawlers"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        crawlers = await crawlers_gateway.list_crawlers()
        return {"total": len(crawlers), "crawlers": crawlers}
    except Exception as e:
        return {"total": 0, "crawlers": [], "error": str(e)}

@router.post("/create")
async def create_crawler(name: str, type: CrawlerType, config: Dict[str, Any]):
    """Create new crawler"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        crawler = await crawlers_gateway.create_crawler(name, type.value, config)
        return {"message": "Crawler created", "crawler_id": crawler['id'], "crawler": crawler}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{crawler_id}")
async def get_crawler(crawler_id: str):
    """Get crawler details"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        crawler = await crawlers_gateway.get_crawler(crawler_id)
        if not crawler:
            raise HTTPException(status_code=404, detail="Crawler not found")
        return crawler
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{crawler_id}")
async def update_crawler(crawler_id: str, updates: Dict[str, Any]):
    """Update crawler configuration"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        await crawlers_gateway.update_crawler(crawler_id, updates)
        return {"message": "Crawler updated", "crawler_id": crawler_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{crawler_id}")
async def delete_crawler(crawler_id: str):
    """Delete crawler"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        await crawlers_gateway.delete_crawler(crawler_id)
        return {"message": "Crawler deleted", "crawler_id": crawler_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CRAWLER EXECUTION
# ============================================================================

@router.post("/{crawler_id}/start")
async def start_crawler(crawler_id: str):
    """Start crawler"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        await crawlers_gateway.start_crawler(crawler_id)
        return {"message": "Crawler started", "crawler_id": crawler_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{crawler_id}/stop")
async def stop_crawler(crawler_id: str):
    """Stop crawler"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        await crawlers_gateway.stop_crawler(crawler_id)
        return {"message": "Crawler stopped", "crawler_id": crawler_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{crawler_id}/pause")
async def pause_crawler(crawler_id: str):
    """Pause crawler"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        await crawlers_gateway.pause_crawler(crawler_id)
        return {"message": "Crawler paused", "crawler_id": crawler_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{crawler_id}/resume")
async def resume_crawler(crawler_id: str):
    """Resume crawler"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        await crawlers_gateway.resume_crawler(crawler_id)
        return {"message": "Crawler resumed", "crawler_id": crawler_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{crawler_id}/status")
async def get_crawler_status(crawler_id: str):
    """Get crawler status"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        status = await crawlers_gateway.get_crawler_status(crawler_id)
        return {"crawler_id": crawler_id, "status": status}
    except Exception as e:
        return {"crawler_id": crawler_id, "status": "unknown", "error": str(e)}

# ============================================================================
# RESULTS
# ============================================================================

@router.get("/{crawler_id}/results")
async def get_crawler_results(crawler_id: str, limit: int = 100):
    """Get crawler results"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        results = await crawlers_gateway.get_results(crawler_id, limit)
        return {"crawler_id": crawler_id, "total": len(results), "results": results}
    except Exception as e:
        return {"crawler_id": crawler_id, "total": 0, "results": [], "error": str(e)}

@router.get("/{crawler_id}/results/latest")
async def get_latest_results(crawler_id: str, limit: int = 20):
    """Get latest crawler results"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        results = await crawlers_gateway.get_latest_results(crawler_id, limit)
        return {"crawler_id": crawler_id, "results": results}
    except Exception as e:
        return {"crawler_id": crawler_id, "results": [], "error": str(e)}

@router.delete("/{crawler_id}/results")
async def clear_crawler_results(crawler_id: str):
    """Clear crawler results"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        await crawlers_gateway.clear_results(crawler_id)
        return {"message": "Results cleared", "crawler_id": crawler_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{crawler_id}/export")
async def export_results(crawler_id: str, format: str = "json"):
    """Export crawler results"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        export = await crawlers_gateway.export_results(crawler_id, format)
        return export
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SCHEDULING
# ============================================================================

@router.post("/{crawler_id}/schedule")
async def schedule_crawler(crawler_id: str, cron_expression: str):
    """Schedule crawler execution"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        await crawlers_gateway.schedule_crawler(crawler_id, cron_expression)
        return {"message": "Crawler scheduled", "crawler_id": crawler_id, "schedule": cron_expression}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{crawler_id}/schedule")
async def get_crawler_schedule(crawler_id: str):
    """Get crawler schedule"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        schedule = await crawlers_gateway.get_schedule(crawler_id)
        return {"crawler_id": crawler_id, "schedule": schedule}
    except Exception as e:
        return {"crawler_id": crawler_id, "schedule": None, "error": str(e)}

@router.delete("/{crawler_id}/schedule")
async def remove_crawler_schedule(crawler_id: str):
    """Remove crawler schedule"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        await crawlers_gateway.remove_schedule(crawler_id)
        return {"message": "Schedule removed", "crawler_id": crawler_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STATISTICS
# ============================================================================

@router.get("/{crawler_id}/stats")
async def get_crawler_stats(crawler_id: str):
    """Get crawler statistics"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        stats = await crawlers_gateway.get_stats(crawler_id)
        return {"crawler_id": crawler_id, "stats": stats}
    except Exception as e:
        return {"crawler_id": crawler_id, "stats": {}, "error": str(e)}

@router.get("/{crawler_id}/history")
async def get_crawler_history(crawler_id: str, limit: int = 50):
    """Get crawler execution history"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        history = await crawlers_gateway.get_history(crawler_id, limit)
        return {"crawler_id": crawler_id, "history": history}
    except Exception as e:
        return {"crawler_id": crawler_id, "history": [], "error": str(e)}

@router.get("/{crawler_id}/performance")
async def get_crawler_performance(crawler_id: str):
    """Get crawler performance metrics"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        performance = await crawlers_gateway.get_performance(crawler_id)
        return {"crawler_id": crawler_id, "performance": performance}
    except Exception as e:
        return {"crawler_id": crawler_id, "performance": {}, "error": str(e)}

# ============================================================================
# LOGS & DEBUGGING
# ============================================================================

@router.get("/{crawler_id}/logs")
async def get_crawler_logs(crawler_id: str, limit: int = 100):
    """Get crawler logs"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        logs = await crawlers_gateway.get_logs(crawler_id, limit)
        return {"crawler_id": crawler_id, "logs": logs}
    except Exception as e:
        return {"crawler_id": crawler_id, "logs": [], "error": str(e)}

@router.get("/{crawler_id}/errors")
async def get_crawler_errors(crawler_id: str, limit: int = 50):
    """Get crawler errors"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        errors = await crawlers_gateway.get_errors(crawler_id, limit)
        return {"crawler_id": crawler_id, "errors": errors}
    except Exception as e:
        return {"crawler_id": crawler_id, "errors": [], "error": str(e)}

# ============================================================================
# BATCH OPERATIONS
# ============================================================================

@router.post("/batch/start")
async def start_multiple_crawlers(crawler_ids: List[str]):
    """Start multiple crawlers"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        results = await crawlers_gateway.start_multiple(crawler_ids)
        return {"message": "Crawlers started", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch/stop")
async def stop_multiple_crawlers(crawler_ids: List[str]):
    """Stop multiple crawlers"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        results = await crawlers_gateway.stop_multiple(crawler_ids)
        return {"message": "Crawlers stopped", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TEMPLATES
# ============================================================================

@router.get("/templates")
async def list_crawler_templates():
    """Get crawler templates"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        templates = await crawlers_gateway.list_templates()
        return {"templates": templates}
    except Exception as e:
        return {"templates": [], "error": str(e)}

@router.post("/templates")
async def create_crawler_from_template(template_id: str, name: str, config: Dict[str, Any]):
    """Create crawler from template"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        crawler = await crawlers_gateway.create_from_template(template_id, name, config)
        return {"message": "Crawler created from template", "crawler": crawler}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MONITORING
# ============================================================================

@router.get("/monitoring/active")
async def get_active_crawlers():
    """Get all active crawlers"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        active = await crawlers_gateway.get_active_crawlers()
        return {"total": len(active), "crawlers": active}
    except Exception as e:
        return {"total": 0, "crawlers": [], "error": str(e)}

@router.get("/monitoring/overview")
async def get_crawlers_overview():
    """Get crawlers overview"""
    try:
        from backend.core.crawlers_gateway import crawlers_gateway
        await crawlers_gateway.initialize()
        
        overview = await crawlers_gateway.get_overview()
        return overview
    except Exception as e:
        return {"error": str(e), "overview": {}}
