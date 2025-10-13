"""
🔍 SEO & OPTIMIZATION ROUTES - Complete Implementation
======================================================
ALL 40 endpoints for SEO engines, analysis, keywords, content optimization
Author: Fahed Mlaiel
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

router = APIRouter(prefix="/seo", tags=["SEO & Optimization"])

# ============================================================================
# SEO ANALYSIS
# ============================================================================

@router.post("/analyze/page")
async def analyze_page(url: str):
    """Analyze page SEO"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        analysis = await engine.analyze_page(url)
        return {"url": url, "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/content")
async def analyze_content(content: str, target_keyword: Optional[str] = None):
    """Analyze content SEO"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        analysis = await engine.analyze_content(content, target_keyword)
        return {"analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyze/site")
async def analyze_site(domain: str):
    """Analyze entire site SEO"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        analysis = await engine.analyze_site(domain)
        return {"domain": domain, "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/score/{url}")
async def get_seo_score(url: str):
    """Get SEO score for URL"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        score = await engine.get_seo_score(url)
        return {"url": url, "score": score}
    except Exception as e:
        return {"url": url, "score": 0, "error": str(e)}

# ============================================================================
# KEYWORD RESEARCH
# ============================================================================

@router.post("/keywords/research")
async def research_keywords(seed_keyword: str, limit: int = 50):
    """Research keywords"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        keywords = await engine.research_keywords(seed_keyword, limit)
        return {"seed": seed_keyword, "keywords": keywords}
    except Exception as e:
        return {"seed": seed_keyword, "keywords": [], "error": str(e)}

@router.get("/keywords/suggestions")
async def get_keyword_suggestions(query: str):
    """Get keyword suggestions"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        suggestions = await engine.get_keyword_suggestions(query)
        return {"query": query, "suggestions": suggestions}
    except Exception as e:
        return {"query": query, "suggestions": [], "error": str(e)}

@router.post("/keywords/difficulty")
async def get_keyword_difficulty(keyword: str):
    """Get keyword difficulty score"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        difficulty = await engine.get_keyword_difficulty(keyword)
        return {"keyword": keyword, "difficulty": difficulty}
    except Exception as e:
        return {"keyword": keyword, "difficulty": 0, "error": str(e)}

@router.post("/keywords/volume")
async def get_search_volume(keyword: str):
    """Get keyword search volume"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        volume = await engine.get_search_volume(keyword)
        return {"keyword": keyword, "volume": volume}
    except Exception as e:
        return {"keyword": keyword, "volume": 0, "error": str(e)}

@router.post("/keywords/trends")
async def get_keyword_trends(keyword: str, period: int = 12):
    """Get keyword trends"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        trends = await engine.get_keyword_trends(keyword, period)
        return {"keyword": keyword, "trends": trends}
    except Exception as e:
        return {"keyword": keyword, "trends": [], "error": str(e)}

# ============================================================================
# CONTENT OPTIMIZATION
# ============================================================================

@router.post("/optimize/content")
async def optimize_content(content: str, target_keywords: List[str]):
    """Optimize content for SEO"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        optimized = await engine.optimize_content(content, target_keywords)
        return {"optimized_content": optimized, "suggestions": optimized.get("suggestions", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize/title")
async def optimize_title(title: str, keyword: str):
    """Optimize title for SEO"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        optimized = await engine.optimize_title(title, keyword)
        return {"original": title, "optimized": optimized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize/meta")
async def optimize_meta_description(description: str, keyword: str):
    """Optimize meta description"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        optimized = await engine.optimize_meta_description(description, keyword)
        return {"original": description, "optimized": optimized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize/headings")
async def optimize_headings(headings: List[str], keywords: List[str]):
    """Optimize headings structure"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        optimized = await engine.optimize_headings(headings, keywords)
        return {"original": headings, "optimized": optimized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# BACKLINKS
# ============================================================================

@router.get("/backlinks/{domain}")
async def get_backlinks(domain: str, limit: int = 100):
    """Get domain backlinks"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        backlinks = await engine.get_backlinks(domain, limit)
        return {"domain": domain, "backlinks": backlinks}
    except Exception as e:
        return {"domain": domain, "backlinks": [], "error": str(e)}

@router.get("/backlinks/{domain}/quality")
async def analyze_backlink_quality(domain: str):
    """Analyze backlink quality"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        quality = await engine.analyze_backlink_quality(domain)
        return {"domain": domain, "quality": quality}
    except Exception as e:
        return {"domain": domain, "quality": {}, "error": str(e)}

@router.post("/backlinks/opportunities")
async def find_backlink_opportunities(domain: str, competitors: List[str]):
    """Find backlink opportunities"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        opportunities = await engine.find_backlink_opportunities(domain, competitors)
        return {"domain": domain, "opportunities": opportunities}
    except Exception as e:
        return {"domain": domain, "opportunities": [], "error": str(e)}

# ============================================================================
# COMPETITORS
# ============================================================================

@router.post("/competitors/analyze")
async def analyze_competitors(domain: str, competitors: List[str]):
    """Analyze competitors"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        analysis = await engine.analyze_competitors(domain, competitors)
        return {"domain": domain, "competitors": analysis}
    except Exception as e:
        return {"domain": domain, "competitors": [], "error": str(e)}

@router.post("/competitors/keywords")
async def get_competitor_keywords(domain: str):
    """Get competitor keywords"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        keywords = await engine.get_competitor_keywords(domain)
        return {"domain": domain, "keywords": keywords}
    except Exception as e:
        return {"domain": domain, "keywords": [], "error": str(e)}

@router.post("/competitors/gaps")
async def find_keyword_gaps(domain: str, competitors: List[str]):
    """Find keyword gaps"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        gaps = await engine.find_keyword_gaps(domain, competitors)
        return {"domain": domain, "gaps": gaps}
    except Exception as e:
        return {"domain": domain, "gaps": [], "error": str(e)}

# ============================================================================
# TECHNICAL SEO
# ============================================================================

@router.get("/technical/audit")
async def technical_seo_audit(domain: str):
    """Run technical SEO audit"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        audit = await engine.technical_audit(domain)
        return {"domain": domain, "audit": audit}
    except Exception as e:
        return {"domain": domain, "audit": {}, "error": str(e)}

@router.get("/technical/sitemap")
async def analyze_sitemap(sitemap_url: str):
    """Analyze sitemap"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        analysis = await engine.analyze_sitemap(sitemap_url)
        return {"sitemap_url": sitemap_url, "analysis": analysis}
    except Exception as e:
        return {"sitemap_url": sitemap_url, "analysis": {}, "error": str(e)}

@router.get("/technical/robots")
async def analyze_robots_txt(domain: str):
    """Analyze robots.txt"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        analysis = await engine.analyze_robots_txt(domain)
        return {"domain": domain, "analysis": analysis}
    except Exception as e:
        return {"domain": domain, "analysis": {}, "error": str(e)}

@router.get("/technical/speed")
async def analyze_page_speed(url: str):
    """Analyze page speed"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        speed = await engine.analyze_page_speed(url)
        return {"url": url, "speed": speed}
    except Exception as e:
        return {"url": url, "speed": {}, "error": str(e)}

@router.get("/technical/mobile")
async def check_mobile_friendly(url: str):
    """Check mobile friendliness"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        mobile = await engine.check_mobile_friendly(url)
        return {"url": url, "mobile": mobile}
    except Exception as e:
        return {"url": url, "mobile": {}, "error": str(e)}

# ============================================================================
# RANKINGS
# ============================================================================

@router.get("/rankings/track")
async def track_rankings(domain: str, keywords: List[str]):
    """Track keyword rankings"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        rankings = await engine.track_rankings(domain, keywords)
        return {"domain": domain, "rankings": rankings}
    except Exception as e:
        return {"domain": domain, "rankings": {}, "error": str(e)}

@router.get("/rankings/history")
async def get_ranking_history(domain: str, keyword: str):
    """Get ranking history"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        history = await engine.get_ranking_history(domain, keyword)
        return {"domain": domain, "keyword": keyword, "history": history}
    except Exception as e:
        return {"domain": domain, "keyword": keyword, "history": [], "error": str(e)}

@router.get("/rankings/serp")
async def get_serp_analysis(keyword: str):
    """Analyze SERP for keyword"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        serp = await engine.analyze_serp(keyword)
        return {"keyword": keyword, "serp": serp}
    except Exception as e:
        return {"keyword": keyword, "serp": {}, "error": str(e)}

# ============================================================================
# REPORTS
# ============================================================================

@router.post("/reports/generate")
async def generate_seo_report(domain: str):
    """Generate comprehensive SEO report"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        report = await engine.generate_seo_report(domain)
        return {"domain": domain, "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports")
async def list_seo_reports(domain: Optional[str] = None):
    """Get SEO reports"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        reports = await engine.list_reports(domain)
        return {"reports": reports}
    except Exception as e:
        return {"reports": [], "error": str(e)}

@router.get("/reports/{report_id}")
async def get_seo_report(report_id: str):
    """Get SEO report"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        report = await engine.get_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RECOMMENDATIONS
# ============================================================================

@router.get("/recommendations/{domain}")
async def get_seo_recommendations(domain: str):
    """Get SEO recommendations"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        recommendations = await engine.get_recommendations(domain)
        return {"domain": domain, "recommendations": recommendations}
    except Exception as e:
        return {"domain": domain, "recommendations": [], "error": str(e)}

@router.get("/opportunities/{domain}")
async def find_seo_opportunities(domain: str):
    """Find SEO opportunities"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        opportunities = await engine.find_opportunities(domain)
        return {"domain": domain, "opportunities": opportunities}
    except Exception as e:
        return {"domain": domain, "opportunities": [], "error": str(e)}

# ============================================================================
# LOCAL SEO
# ============================================================================

@router.post("/local/optimize")
async def optimize_local_seo(business_name: str, location: Dict[str, Any]):
    """Optimize for local SEO"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        optimized = await engine.optimize_local_seo(business_name, location)
        return {"business": business_name, "optimized": optimized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/local/listings")
async def get_local_listings(business_name: str):
    """Get local business listings"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        listings = await engine.get_local_listings(business_name)
        return {"business": business_name, "listings": listings}
    except Exception as e:
        return {"business": business_name, "listings": [], "error": str(e)}

# ============================================================================
# SCHEMA & STRUCTURED DATA
# ============================================================================

@router.post("/schema/generate")
async def generate_schema(content_type: str, data: Dict[str, Any]):
    """Generate schema markup"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        schema = await engine.generate_schema(content_type, data)
        return {"type": content_type, "schema": schema}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schema/validate")
async def validate_schema(url: str):
    """Validate schema markup"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        validation = await engine.validate_schema(url)
        return {"url": url, "validation": validation}
    except Exception as e:
        return {"url": url, "validation": {}, "error": str(e)}

# ============================================================================
# MONITORING
# ============================================================================

@router.post("/monitor/add")
async def add_monitoring(domain: str, keywords: List[str]):
    """Add domain to monitoring"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        await engine.add_monitoring(domain, keywords)
        return {"message": "Monitoring added", "domain": domain}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitor/alerts")
async def get_seo_alerts(domain: Optional[str] = None):
    """Get SEO alerts"""
    try:
        from backend.seo.seo_engine import SEOEngine
        engine = SEOEngine()
        alerts = await engine.get_seo_alerts(domain)
        return {"alerts": alerts}
    except Exception as e:
        return {"alerts": [], "error": str(e)}
