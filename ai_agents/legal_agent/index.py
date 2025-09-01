#!/usr/bin/env python3
"""Legal Agent Service Index
========================

Main entry point for the Legal Agent service.
Provides RESTful API endpoints for legal services integration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit 
written permission is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from .legal_agent import LegalAgent, LegalAgentConfig
from .legal_analyzer import LegalAnalyzer
from .document_generator import DocumentGenerator, ContractTemplate
from .regulatory_monitor import RegulatoryMonitor
from .legal_research import LegalResearcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Legal Agent Service",
    description="Professional Legal Services for Content Creators and Influencers",
    version="1.0.0",
    docs_url="/legal/docs",
    redoc_url="/legal/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instances
legal_agent: Optional[LegalAgent] = None
legal_analyzer: Optional[LegalAnalyzer] = None
document_generator: Optional[DocumentGenerator] = None
regulatory_monitor: Optional[RegulatoryMonitor] = None
legal_researcher: Optional[LegalResearcher] = None


# Pydantic models for API
class LegalAnalysisRequest(BaseModel):
    """Request model for legal analysis"""
    content: str = Field(..., description="Content to analyze")
    content_type: str = Field(..., description="Type of content (text, image, audio, video)")
    jurisdiction: str = Field(default="US", description="Legal jurisdiction")
    analysis_type: List[str] = Field(default=["copyright", "trademark"], description="Types of analysis")


class ContractGenerationRequest(BaseModel):
    """Request model for contract generation"""
    contract_type: str = Field(..., description="Type of contract to generate")
    parties: Dict[str, Any] = Field(..., description="Contract parties information")
    terms: Dict[str, Any] = Field(..., description="Contract terms and conditions")
    jurisdiction: str = Field(default="US", description="Legal jurisdiction")


class ComplianceCheckRequest(BaseModel):
    """Request model for compliance checking"""
    content_data: Dict[str, Any] = Field(..., description="Content data to check")
    platform: str = Field(..., description="Target platform")
    content_type: str = Field(..., description="Type of content")


class LegalResearchRequest(BaseModel):
    """Request model for legal research"""
    query: str = Field(..., description="Research query")
    jurisdiction: str = Field(default="US", description="Legal jurisdiction")
    research_depth: str = Field(default="comprehensive", description="Research depth level")
    areas: List[str] = Field(default=["intellectual_property"], description="Legal areas to research")


class RegulatoryUpdateRequest(BaseModel):
    """Request model for regulatory updates"""
    jurisdictions: List[str] = Field(default=["US"], description="Jurisdictions to monitor")
    areas: List[str] = Field(default=["intellectual_property"], description="Legal areas to monitor")


# Service initialization
async def initialize_services():
    """Initialize all legal service components"""
    global legal_agent, legal_analyzer, document_generator, regulatory_monitor, legal_researcher
    
    try:
        # Initialize configuration
        config = LegalAgentConfig(
            jurisdiction="US",
            compliance_level="strict",
            document_templates_path="./templates",
            research_databases=["lexis", "westlaw", "google_scholar"],
            monitoring_enabled=True
        )
        
        # Initialize services
        legal_agent = LegalAgent(config)
        legal_analyzer = LegalAnalyzer()
        document_generator = DocumentGenerator()
        regulatory_monitor = RegulatoryMonitor()
        legal_researcher = LegalResearcher()
        
        # Start background services
        await legal_agent.initialize()
        await regulatory_monitor.start_monitoring()
        
        logger.info("Legal Agent services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize legal services: {e}")
        raise


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    await initialize_services()


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    if regulatory_monitor:
        await regulatory_monitor.stop_monitoring()
    
    if legal_agent:
        await legal_agent.shutdown()


# Health check endpoint
@app.get("/legal/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "legal_agent",
        "version": "1.0.0"
    }


# Legal analysis endpoints
@app.post("/legal/analyze")
async def analyze_content(request: LegalAnalysisRequest):
    """Analyze content for legal compliance and risks"""
    try:
        if not legal_analyzer:
            raise HTTPException(status_code=503, detail="Legal analyzer not available")
        
        analysis_result = await legal_analyzer.analyze_content(
            content=request.content,
            content_type=request.content_type,
            jurisdiction=request.jurisdiction,
            analysis_types=request.analysis_type
        )
        
        return {
            "success": True,
            "analysis": analysis_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Content analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/legal/copyright/check")
async def check_copyright(request: LegalAnalysisRequest):
    """Check content for copyright issues"""
    try:
        if not legal_analyzer:
            raise HTTPException(status_code=503, detail="Legal analyzer not available")
        
        copyright_analysis = await legal_analyzer.check_copyright_infringement(
            content=request.content,
            content_type=request.content_type
        )
        
        return {
            "success": True,
            "copyright_analysis": copyright_analysis,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Copyright check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/legal/trademark/check")
async def check_trademark(request: LegalAnalysisRequest):
    """Check content for trademark issues"""
    try:
        if not legal_analyzer:
            raise HTTPException(status_code=503, detail="Legal analyzer not available")
        
        trademark_analysis = await legal_analyzer.check_trademark_infringement(
            content=request.content,
            content_type=request.content_type
        )
        
        return {
            "success": True,
            "trademark_analysis": trademark_analysis,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Trademark check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Document generation endpoints
@app.post("/legal/contracts/generate")
async def generate_contract(request: ContractGenerationRequest):
    """Generate legal contracts and agreements"""
    try:
        if not document_generator:
            raise HTTPException(status_code=503, detail="Document generator not available")
        
        contract = await document_generator.generate_contract(
            contract_type=request.contract_type,
            parties=request.parties,
            terms=request.terms,
            jurisdiction=request.jurisdiction
        )
        
        return {
            "success": True,
            "contract": contract,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Contract generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/legal/documents/privacy-policy")
async def generate_privacy_policy(request: ContractGenerationRequest):
    """Generate privacy policy document"""
    try:
        if not document_generator:
            raise HTTPException(status_code=503, detail="Document generator not available")
        
        privacy_policy = await document_generator.generate_privacy_policy(
            business_info=request.parties,
            data_practices=request.terms,
            jurisdiction=request.jurisdiction
        )
        
        return {
            "success": True,
            "privacy_policy": privacy_policy,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Privacy policy generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/legal/documents/terms-of-service")
async def generate_terms_of_service(request: ContractGenerationRequest):
    """Generate terms of service document"""
    try:
        if not document_generator:
            raise HTTPException(status_code=503, detail="Document generator not available")
        
        terms_of_service = await document_generator.generate_terms_of_service(
            service_info=request.parties,
            service_terms=request.terms,
            jurisdiction=request.jurisdiction
        )
        
        return {
            "success": True,
            "terms_of_service": terms_of_service,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Terms of service generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Compliance checking endpoints
@app.post("/legal/compliance/check")
async def check_compliance(request: ComplianceCheckRequest):
    """Check content compliance with platform policies"""
    try:
        if not legal_agent:
            raise HTTPException(status_code=503, detail="Legal agent not available")
        
        compliance_result = await legal_agent.check_platform_compliance(
            content_data=request.content_data,
            platform=request.platform,
            content_type=request.content_type
        )
        
        return {
            "success": True,
            "compliance": compliance_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Compliance check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/legal/compliance/requirements/{platform}")
async def get_compliance_requirements(platform: str):
    """Get compliance requirements for a specific platform"""
    try:
        if not legal_agent:
            raise HTTPException(status_code=503, detail="Legal agent not available")
        
        requirements = await legal_agent.get_platform_requirements(platform)
        
        return {
            "success": True,
            "platform": platform,
            "requirements": requirements,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get compliance requirements: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Legal research endpoints
@app.post("/legal/research")
async def conduct_legal_research(request: LegalResearchRequest):
    """Conduct comprehensive legal research"""
    try:
        if not legal_researcher:
            raise HTTPException(status_code=503, detail="Legal researcher not available")
        
        research_result = await legal_researcher.conduct_research(
            query=request.query,
            jurisdiction=request.jurisdiction,
            depth=request.research_depth,
            areas=request.areas
        )
        
        return {
            "success": True,
            "research": research_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Legal research failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/legal/precedents/{case_type}")
async def find_legal_precedents(case_type: str, jurisdiction: str = "US"):
    """Find relevant legal precedents"""
    try:
        if not legal_researcher:
            raise HTTPException(status_code=503, detail="Legal researcher not available")
        
        precedents = await legal_researcher.find_precedents(
            case_type=case_type,
            jurisdiction=jurisdiction
        )
        
        return {
            "success": True,
            "case_type": case_type,
            "jurisdiction": jurisdiction,
            "precedents": precedents,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Precedent search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Regulatory monitoring endpoints
@app.post("/legal/regulatory/updates")
async def get_regulatory_updates(request: RegulatoryUpdateRequest):
    """Get latest regulatory updates"""
    try:
        if not regulatory_monitor:
            raise HTTPException(status_code=503, detail="Regulatory monitor not available")
        
        updates = await regulatory_monitor.get_recent_updates(
            jurisdictions=request.jurisdictions,
            areas=request.areas
        )
        
        return {
            "success": True,
            "updates": updates,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get regulatory updates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/legal/regulatory/alerts")
async def get_regulatory_alerts():
    """Get active regulatory alerts"""
    try:
        if not regulatory_monitor:
            raise HTTPException(status_code=503, detail="Regulatory monitor not available")
        
        alerts = await regulatory_monitor.get_active_alerts()
        
        return {
            "success": True,
            "alerts": alerts,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get regulatory alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Risk assessment endpoints
@app.post("/legal/risk/assess")
async def assess_legal_risk(request: LegalAnalysisRequest):
    """Assess legal risks for content or business decision"""
    try:
        if not legal_agent:
            raise HTTPException(status_code=503, detail="Legal agent not available")
        
        risk_assessment = await legal_agent.assess_legal_risks(
            content=request.content,
            content_type=request.content_type,
            jurisdiction=request.jurisdiction
        )
        
        return {
            "success": True,
            "risk_assessment": risk_assessment,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Risk assessment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Legal advice endpoints
@app.post("/legal/advice/request")
async def request_legal_advice(request: LegalAnalysisRequest):
    """Request legal advice for specific situation"""
    try:
        if not legal_agent:
            raise HTTPException(status_code=503, detail="Legal agent not available")
        
        advice = await legal_agent.provide_legal_advice(
            situation=request.content,
            context=request.content_type,
            jurisdiction=request.jurisdiction
        )
        
        return {
            "success": True,
            "advice": advice,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Legal advice request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Service status endpoints
@app.get("/legal/status")
async def get_service_status():
    """Get comprehensive service status"""
    try:
        status = {
            "legal_agent": legal_agent is not None,
            "legal_analyzer": legal_analyzer is not None,
            "document_generator": document_generator is not None,
            "regulatory_monitor": regulatory_monitor is not None,
            "legal_researcher": legal_researcher is not None,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if regulatory_monitor:
            status["monitoring_active"] = await regulatory_monitor.is_monitoring_active()
        
        return {
            "success": True,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Main execution
def main():
    """Main entry point for running the service"""
    uvicorn.run(
        "legal_agent.index:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
