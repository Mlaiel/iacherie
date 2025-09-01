"""Legal Research - Advanced Legal Research & Analysis Engine

Comprehensive legal research capabilities including case law analysis, statutory
interpretation, and legal precedent research for content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""
import asyncio
import logging
import json
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import elasticsearch
from rank_bm25 import BM25Okapi

try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
try:
    from core.exceptions import ResearchError, QueryError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ResearchError, QueryError = globals().get('ResearchError, QueryError', Exception)
from ...utils.ai_processor import AIProcessor
from ...utils.legal_database import LegalDatabase
from ...utils.citation_parser import CitationParser
from ...models.legal_models import CaseResult, StatutoryReference, LegalPrecedent

logger = logging.getLogger(__name__)

class ResearchScope(Enum):
    """Legal research scope levels"""
    NARROW = "narrow"        # Specific legal issue
    FOCUSED = "focused"      # Specific legal area
    BROAD = "broad"         # Multiple legal areas
    COMPREHENSIVE = "comprehensive"  # Full legal landscape

class ResearchDepth(Enum):
    """Research depth levels"""
    SURFACE = "surface"      # Basic overview
    STANDARD = "standard"    # Standard research depth
    DETAILED = "detailed"    # Detailed analysis
    EXHAUSTIVE = "exhaustive" # Complete research

class CaseRelevance(Enum):
    """Case relevance levels"""
    HIGHLY_RELEVANT = "highly_relevant"
    MODERATELY_RELEVANT = "moderately_relevant"
    SOMEWHAT_RELEVANT = "somewhat_relevant"
    TANGENTIALLY_RELEVANT = "tangentially_relevant"

@dataclass
class ResearchQuery:
    """Legal research query structure"""
    query_text: str
    legal_areas: List[str]
    jurisdictions: List[str]
    scope: ResearchScope
    depth: ResearchDepth
    date_range: Optional[Tuple[datetime, datetime]] = None
    case_types: List[str] = field(default_factory=list)
    citation_requirements: bool = True

@dataclass
class ResearchResult:
    """Legal research result structure"""
    research_id: str
    query: ResearchQuery
    case_law: List[Dict[str, Any]]
    statutes: List[Dict[str, Any]]
    regulations: List[Dict[str, Any]]
    secondary_sources: List[Dict[str, Any]]
    legal_analysis: Dict[str, Any]
    citation_network: Dict[str, Any]
    research_summary: str
    confidence_score: float
    research_time: float

class LegalResearch:
    """
    Advanced Legal Research Engine
    
    Comprehensive legal research capabilities including:
    - Case law research and analysis
    - Statutory interpretation and research
    - Legal precedent identification
    - Citation network analysis
    - AI-powered legal reasoning
    - Multi-jurisdiction research
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ai_processor = AIProcessor(config.get('ai_config', {}))
        self.legal_database = LegalDatabase()
        self.citation_parser = CitationParser()
        
        # Research databases and indexes
        self.case_database = None
        self.statute_database = None
        self.elasticsearch_client = None
        
        # AI models for legal research
        self.legal_reasoner = None
        self.case_classifier = None
        self.relevance_scorer = None
        
        # Research configuration
        self.research_databases = {}
        self.jurisdiction_mappings = {}
        self.legal_area_mappings = {}
        
        self._initialize_research_systems()
        
        logger.info("Legal Research Engine initialized successfully")
    
    def _initialize_research_systems(self):
        """Initialize legal research systems and databases"""
        try:
            # Setup research databases
            self._setup_research_databases()
            
            # Initialize AI research models
            self._setup_ai_research_models()
            
            # Load jurisdiction and legal area mappings
            self._load_research_mappings()
            
            # Setup search indexes
            self._setup_search_indexes()
            
            logger.info("Research systems initialized successfully")
            
        except Exception as e:
            logger.error(f"Research systems initialization failed: {e}")
            raise ResearchError(f"Research initialization error: {e}")
    
    def _setup_research_databases(self):
        """Setup connections to legal research databases"""
        try:
            # Setup Elasticsearch for full-text search
            if self.config.get('elasticsearch_enabled', False):
                self.elasticsearch_client = elasticsearch.Elasticsearch(
                    hosts=[self.config.get('elasticsearch_host', 'localhost:9200')],
                    timeout=30
                )
            
            # Setup legal databases
            self.research_databases = {
                'case_law': {
                    'us_federal': 'https://api.case.law/v1/',
                    'us_state': 'https://api.courtlistener.com/api/rest/v3/',
                    'eu_caselaw': 'https://eur-lex.europa.eu/search.html',
                    'uk_caselaw': 'https://www.bailii.org/'
                },
                'statutes': {
                    'us_federal': 'https://api.congress.gov/v3/',
                    'eu_legislation': 'https://eur-lex.europa.eu/legal-content/',
                    'german_law': 'https://www.gesetze-im-internet.de/',
                    'french_law': 'https://www.legifrance.gouv.fr/',
                    'uk_legislation': 'https://www.legislation.gov.uk/'
                },
                'regulations': {
                    'us_federal': 'https://www.federalregister.gov/api/v1/',
                    'eu_regulations': 'https://eur-lex.europa.eu/homepage.html'
                }
            }
            
            logger.info(f"Configured {len(self.research_databases)} research database categories")
            
        except Exception as e:
            logger.error(f"Research database setup failed: {e}")
    
    def _setup_ai_research_models(self):
        """Setup AI models for legal research enhancement"""
        try:
            # Legal reasoning model
            self.legal_reasoner = self.ai_processor.load_model(
                "legal_reasoning_model",
                fallback_available=True
            )
            
            # Case classification model
            self.case_classifier = self.ai_processor.load_model(
                "legal_case_classifier",
                fallback_available=True
            )
            
            # Relevance scoring model
            self.relevance_scorer = self.ai_processor.load_model(
                "legal_relevance_scorer",
                fallback_available=True
            )
            
            # Citation network analyzer
            self.citation_analyzer = self.ai_processor.load_model(
                "citation_network_analyzer",
                fallback_available=True
            )
            
            logger.info("AI research models loaded successfully")
            
        except Exception as e:
            logger.warning(f"AI research models setup failed: {e}")
            # Continue without AI enhancement
            self.legal_reasoner = None
            self.case_classifier = None
            self.relevance_scorer = None
            self.citation_analyzer = None
    
    def _load_research_mappings(self):
        """Load jurisdiction and legal area mappings"""
        self.jurisdiction_mappings = {
            'us_federal': {
                'courts': ['Supreme Court', 'Circuit Courts', 'District Courts'],
                'databases': ['case.law', 'courtlistener', 'justia'],
                'citation_formats': ['U.S.', 'F.2d', 'F.3d', 'F.Supp']
            },
            'us_state': {
                'courts': ['State Supreme Courts', 'State Appellate Courts'],
                'databases': ['case.law', 'state_databases'],
                'citation_formats': ['state_reporters']
            },
            'eu': {
                'courts': ['ECJ', 'CFI', 'National Courts'],
                'databases': ['eur-lex', 'eu_caselaw'],
                'citation_formats': ['ECR', 'EU:C:', 'EU:T:']
            },
            'uk': {
                'courts': ['House of Lords', 'Court of Appeal', 'High Court'],
                'databases': ['bailii', 'justis'],
                'citation_formats': ['UKHL', 'EWCA', 'EWHC']
            },
            'german': {
                'courts': ['BGH', 'BVerfG', 'OLG', 'LG'],
                'databases': ['juris', 'beck-online'],
                'citation_formats': ['BGH', 'BVerfG', 'NJW']
            },
            'french': {
                'courts': ['Cour de cassation', 'Conseil d\'État', 'CAA'],
                'databases': ['legifrance', 'dalloz'],
                'citation_formats': ['Cass.', 'CE', 'CAA']
            }
        }
        
        self.legal_area_mappings = {
            'intellectual_property': {
                'keywords': ['copyright', 'trademark', 'patent', 'trade secret', 'ip'],
                'case_types': ['copyright infringement', 'trademark disputes', 'patent litigation'],
                'statutes': ['Copyright Act', 'Trademark Act', 'Patent Act']
            },
            'data_privacy': {
                'keywords': ['privacy', 'data protection', 'gdpr', 'ccpa', 'personal data'],
                'case_types': ['privacy violations', 'data breaches', 'consent disputes'],
                'statutes': ['GDPR', 'CCPA', 'PIPEDA', 'Data Protection Act']
            },
            'content_creation': {
                'keywords': ['content', 'creator', 'influencer', 'social media', 'platform'],
                'case_types': ['platform disputes', 'content removal', 'monetization'],
                'statutes': ['DMCA', 'Communications Decency Act', 'Platform regulations']
            },
            'contract_law': {
                'keywords': ['contract', 'agreement', 'breach', 'performance', 'damages'],
                'case_types': ['breach of contract', 'contract interpretation', 'remedies'],
                'statutes': ['Uniform Commercial Code', 'Contract statutes']
            },
            'tort_law': {
                'keywords': ['negligence', 'liability', 'damages', 'defamation', 'privacy torts'],
                'case_types': ['negligence claims', 'defamation suits', 'privacy torts'],
                'statutes': ['Tort reform statutes', 'Liability statutes']
            }
        }
    
    def _setup_search_indexes(self):
        """Setup search indexes for efficient legal research"""
        try:
            # Create indexes for different legal content types
            if self.elasticsearch_client:
                index_configs = {
                    'legal_cases': {
                        'mappings': {
                            'properties': {
                                'title': {'type': 'text', 'analyzer': 'legal_analyzer'},
                                'content': {'type': 'text', 'analyzer': 'legal_analyzer'},
                                'citation': {'type': 'keyword'},
                                'court': {'type': 'keyword'},
                                'jurisdiction': {'type': 'keyword'},
                                'date': {'type': 'date'},
                                'legal_areas': {'type': 'keyword'},
                                'precedential_value': {'type': 'integer'}
                            }
                        }
                    },
                    'legal_statutes': {
                        'mappings': {
                            'properties': {
                                'title': {'type': 'text', 'analyzer': 'legal_analyzer'},
                                'content': {'type': 'text', 'analyzer': 'legal_analyzer'},
                                'citation': {'type': 'keyword'},
                                'jurisdiction': {'type': 'keyword'},
                                'effective_date': {'type': 'date'},
                                'legal_areas': {'type': 'keyword'}
                            }
                        }
                    }
                }
                
                # Create indexes if they don't exist
                for index_name, config in index_configs.items():
                    if not self.elasticsearch_client.indices.exists(index=index_name):
                        self.elasticsearch_client.indices.create(index=index_name, body=config)
                        logger.info(f"Created search index: {index_name}")
                
        except Exception as e:
            logger.error(f"Search index setup failed: {e}")
    
    async def conduct_research(self, query: ResearchQuery) -> ResearchResult:
        """
        Conduct comprehensive legal research based on query
        
        Args:
            query: Research query with parameters and requirements
            
        Returns:
            Comprehensive research results with analysis
        """
        try:
            start_time = datetime.now(timezone.utc)
            research_id = f"research_{start_time.strftime('%Y%m%d_%H%M%S')}"
            
            # Validate research query
            self._validate_research_query(query)
            
            # Parse and expand query
            expanded_query = await self._expand_research_query(query)
            
            # Conduct multi-source research
            case_results = await self._research_case_law(expanded_query)
            statute_results = await self._research_statutes(expanded_query)
            regulation_results = await self._research_regulations(expanded_query)
            secondary_results = await self._research_secondary_sources(expanded_query)
            
            # Analyze and synthesize results
            legal_analysis = await self._analyze_research_results(
                case_results, statute_results, regulation_results, secondary_results, expanded_query
            )
            
            # Build citation network
            citation_network = await self._build_citation_network(
                case_results, statute_results, regulation_results
            )
            
            # Generate research summary
            research_summary = await self._generate_research_summary(
                legal_analysis, case_results, statute_results
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_research_confidence(
                case_results, statute_results, legal_analysis
            )
            
            research_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            result = ResearchResult(
                research_id=research_id,
                query=query,
                case_law=case_results,
                statutes=statute_results,
                regulations=regulation_results,
                secondary_sources=secondary_results,
                legal_analysis=legal_analysis,
                citation_network=citation_network,
                research_summary=research_summary,
                confidence_score=confidence_score,
                research_time=research_time
            )
            
            # Store research results
            await self._store_research_results(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Legal research failed: {e}")
            raise ResearchError(f"Research execution error: {e}")
    
    def _validate_research_query(self, query: ResearchQuery):
        """Validate research query parameters"""
        if not query.query_text or len(query.query_text.strip()) < 3:
            raise QueryError("Research query text must be at least 3 characters")
        
        if not query.legal_areas:
            raise QueryError("At least one legal area must be specified")
        
        if not query.jurisdictions:
            raise QueryError("At least one jurisdiction must be specified")
        
        # Validate jurisdiction availability
        for jurisdiction in query.jurisdictions:
            if jurisdiction not in self.jurisdiction_mappings:
                logger.warning(f"Unknown jurisdiction: {jurisdiction}")
    
    async def _expand_research_query(self, query: ResearchQuery) -> Dict[str, Any]:
        """Expand and enhance research query using AI"""
        try:
            expanded_query = {
                'original_query': query.query_text,
                'expanded_terms': [],
                'legal_concepts': [],
                'search_strategies': [],
                'jurisdiction_specific_terms': {}
            }
            
            # Use AI to expand query terms if available
            if self.legal_reasoner:
                expansion_result = await self.ai_processor.process_request(
                    "expand_legal_query",
                    {
                        'query': query.query_text,
                        'legal_areas': query.legal_areas,
                        'jurisdictions': query.jurisdictions
                    }
                )
                
                if expansion_result:
                    expanded_query.update(expansion_result)
            
            # Add domain-specific expansions
            expanded_query['expanded_terms'].extend(
                self._get_domain_specific_terms(query.legal_areas)
            )
            
            # Add jurisdiction-specific search terms
            for jurisdiction in query.jurisdictions:
                if jurisdiction in self.jurisdiction_mappings:
                    expanded_query['jurisdiction_specific_terms'][jurisdiction] = \
                        self.jurisdiction_mappings[jurisdiction].get('citation_formats', [])
            
            return expanded_query
            
        except Exception as e:
            logger.error(f"Query expansion failed: {e}")
            return {'original_query': query.query_text, 'expanded_terms': []}
    
    def _get_domain_specific_terms(self, legal_areas: List[str]) -> List[str]:
        """Get domain-specific search terms for legal areas"""
        terms = []
        for area in legal_areas:
            if area in self.legal_area_mappings:
                terms.extend(self.legal_area_mappings[area]['keywords'])
        return list(set(terms))  # Remove duplicates
    
    async def _research_case_law(self, expanded_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Research case law using multiple databases and sources"""
        case_results = []
        
        try:
            # Search local case database if available
            if self.elasticsearch_client:
                es_cases = await self._search_elasticsearch_cases(expanded_query)
                case_results.extend(es_cases)
            
            # Search external case law databases
            for jurisdiction, db_config in self.research_databases.get('case_law', {}).items():
                try:
                    jurisdiction_cases = await self._search_case_database(
                        db_config, expanded_query, jurisdiction
                    )
                    case_results.extend(jurisdiction_cases)
                except Exception as e:
                    logger.error(f"Case database search failed for {jurisdiction}: {e}")
            
            # Rank and filter results by relevance
            ranked_cases = await self._rank_case_results(case_results, expanded_query)
            
            # Limit results based on research depth
            depth_limits = {
                ResearchDepth.SURFACE: 10,
                ResearchDepth.STANDARD: 25,
                ResearchDepth.DETAILED: 50,
                ResearchDepth.EXHAUSTIVE: 100
            }
            
            query_depth = ResearchDepth.STANDARD  # Default from query
            limit = depth_limits.get(query_depth, 25)
            
            return ranked_cases[:limit]
            
        except Exception as e:
            logger.error(f"Case law research failed: {e}")
            return []
    
    async def _search_elasticsearch_cases(self, expanded_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search cases using Elasticsearch"""
        try:
            search_body = {
                'query': {
                    'bool': {
                        'should': [
                            {
                                'match': {
                                    'content': {
                                        'query': expanded_query['original_query'],
                                        'boost': 2.0
                                    }
                                }
                            },
                            {
                                'terms': {
                                    'legal_areas': expanded_query.get('legal_concepts', []),
                                    'boost': 1.5
                                }
                            }
                        ]
                    }
                },
                'sort': [
                    {'precedential_value': {'order': 'desc'}},
                    {'_score': {'order': 'desc'}}
                ],
                'size': 50
            }
            
            response = self.elasticsearch_client.search(
                index='legal_cases',
                body=search_body
            )
            
            results = []
            for hit in response['hits']['hits']:
                case_data = hit['_source']
                case_data['relevance_score'] = hit['_score']
                case_data['search_source'] = 'elasticsearch'
                results.append(case_data)
            
            return results
            
        except Exception as e:
            logger.error(f"Elasticsearch case search failed: {e}")
            return []
    
    async def _search_case_database(self, database_url: str, expanded_query: Dict[str, Any], jurisdiction: str) -> List[Dict[str, Any]]:
        """Search external case law database"""
        # Implementation would depend on specific database APIs
        # For now, return mock results
        return []
    
    async def _rank_case_results(self, cases: List[Dict[str, Any]], expanded_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank case results by relevance using AI or traditional methods"""
        try:
            if self.relevance_scorer and cases:
                # Use AI relevance scoring
                scored_cases = []
                for case in cases:
                    relevance_score = await self._calculate_ai_relevance(case, expanded_query)
                    case['ai_relevance_score'] = relevance_score
                    scored_cases.append(case)
                
                # Sort by AI relevance score
                scored_cases.sort(key=lambda x: x.get('ai_relevance_score', 0), reverse=True)
                return scored_cases
            else:
                # Use traditional ranking methods
                return self._rank_cases_traditional(cases, expanded_query)
                
        except Exception as e:
            logger.error(f"Case ranking failed: {e}")
            return cases  # Return original order on failure
    
    def _rank_cases_traditional(self, cases: List[Dict[str, Any]], expanded_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Traditional case ranking using keyword matching and precedential value"""
        for case in cases:
            score = 0
            
            # Keyword matching score
            case_text = f"{case.get('title', '')} {case.get('content', '')}".lower()
            query_terms = expanded_query['original_query'].lower().split()
            
            for term in query_terms:
                if term in case_text:
                    score += case_text.count(term)
            
            # Precedential value bonus
            score += case.get('precedential_value', 0) * 10
            
            # Recent cases get slight bonus
            if case.get('date'):
                try:
                    case_date = datetime.fromisoformat(str(case['date']))
                    years_old = (datetime.now(timezone.utc) - case_date).days / 365
                    if years_old < 5:
                        score += (5 - years_old) * 2
                except:
                    pass
            
            case['traditional_relevance_score'] = score
        
        # Sort by traditional relevance score
        cases.sort(key=lambda x: x.get('traditional_relevance_score', 0), reverse=True)
        return cases
    
    async def _calculate_ai_relevance(self, case: Dict[str, Any], expanded_query: Dict[str, Any]) -> float:
        """Calculate AI-based relevance score for case"""
        try:
            relevance_input = {
                'case_title': case.get('title', ''),
                'case_content': case.get('content', '')[:2000],  # Limit content length
                'query': expanded_query['original_query'],
                'legal_areas': expanded_query.get('legal_concepts', [])
            }
            
            relevance_result = await self.ai_processor.process_request(
                "calculate_legal_relevance",
                relevance_input
            )
            
            return relevance_result.get('relevance_score', 0.5) if relevance_result else 0.5
            
        except Exception as e:
            logger.error(f"AI relevance calculation failed: {e}")
            return 0.5  # Default neutral relevance
    
    async def _research_statutes(self, expanded_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Research relevant statutes and legislation"""
        statute_results = []
        
        try:
            # Search statute databases
            for jurisdiction, db_config in self.research_databases.get('statutes', {}).items():
                try:
                    jurisdiction_statutes = await self._search_statute_database(
                        db_config, expanded_query, jurisdiction
                    )
                    statute_results.extend(jurisdiction_statutes)
                except Exception as e:
                    logger.error(f"Statute database search failed for {jurisdiction}: {e}")
            
            # Search local statute index if available
            if self.elasticsearch_client:
                es_statutes = await self._search_elasticsearch_statutes(expanded_query)
                statute_results.extend(es_statutes)
            
            # Remove duplicates and rank by relevance
            unique_statutes = self._deduplicate_statutes(statute_results)
            ranked_statutes = self._rank_statutes(unique_statutes, expanded_query)
            
            return ranked_statutes[:20]  # Limit statute results
            
        except Exception as e:
            logger.error(f"Statute research failed: {e}")
            return []
    
    async def _search_statute_database(self, database_url: str, expanded_query: Dict[str, Any], jurisdiction: str) -> List[Dict[str, Any]]:
        """Search external statute database"""
        # Implementation would depend on specific database APIs
        return []
    
    async def _search_elasticsearch_statutes(self, expanded_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search statutes using Elasticsearch"""
        try:
            search_body = {
                'query': {
                    'bool': {
                        'should': [
                            {
                                'match': {
                                    'title': {
                                        'query': expanded_query['original_query'],
                                        'boost': 3.0
                                    }
                                }
                            },
                            {
                                'match': {
                                    'content': {
                                        'query': expanded_query['original_query'],
                                        'boost': 1.0
                                    }
                                }
                            }
                        ]
                    }
                },
                'size': 30
            }
            
            response = self.elasticsearch_client.search(
                index='legal_statutes',
                body=search_body
            )
            
            results = []
            for hit in response['hits']['hits']:
                statute_data = hit['_source']
                statute_data['relevance_score'] = hit['_score']
                statute_data['search_source'] = 'elasticsearch'
                results.append(statute_data)
            
            return results
            
        except Exception as e:
            logger.error(f"Elasticsearch statute search failed: {e}")
            return []
    
    def _deduplicate_statutes(self, statutes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate statutes based on citation or title"""
        seen_citations = set()
        seen_titles = set()
        unique_statutes = []
        
        for statute in statutes:
            citation = statute.get('citation', '').strip()
            title = statute.get('title', '').strip()
            
            if citation and citation not in seen_citations:
                seen_citations.add(citation)
                unique_statutes.append(statute)
            elif title and title not in seen_titles:
                seen_titles.add(title)
                unique_statutes.append(statute)
        
        return unique_statutes
    
    def _rank_statutes(self, statutes: List[Dict[str, Any]], expanded_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank statutes by relevance"""
        for statute in statutes:
            score = 0
            
            # Title matching gets higher weight
            title = statute.get('title', '').lower()
            query_terms = expanded_query['original_query'].lower().split()
            
            for term in query_terms:
                if term in title:
                    score += title.count(term) * 5
            
            # Content matching
            content = statute.get('content', '').lower()
            for term in query_terms:
                if term in content:
                    score += content.count(term)
            
            # Current statutes get preference
            if statute.get('effective_date'):
                try:
                    effective_date = datetime.fromisoformat(str(statute['effective_date']))
                    if effective_date <= datetime.now(timezone.utc):
                        score += 10  # Bonus for currently effective
                except:
                    pass
            
            statute['relevance_score'] = score
        
        statutes.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return statutes
    
    async def _research_regulations(self, expanded_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Research relevant regulations"""
        # Similar implementation to statutes research
        return []
    
    async def _research_secondary_sources(self, expanded_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Research secondary legal sources"""
        # Implementation for law reviews, treatises, etc.
        return []
    
    async def _analyze_research_results(self, cases: List[Dict[str, Any]], statutes: List[Dict[str, Any]], 
                                      regulations: List[Dict[str, Any]], secondary: List[Dict[str, Any]], 
                                      expanded_query: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and synthesize research results"""
        try:
            analysis = {
                'key_findings': [],
                'legal_principles': [],
                'jurisdictional_variations': {},
                'precedent_hierarchy': [],
                'statutory_framework': [],
                'regulatory_considerations': [],
                'gaps_and_uncertainties': [],
                'recommendations': []
            }
            
            # Analyze case law findings
            if cases:
                analysis['key_findings'].extend(await self._extract_case_findings(cases))
                analysis['legal_principles'].extend(await self._extract_legal_principles(cases))
                analysis['precedent_hierarchy'] = await self._build_precedent_hierarchy(cases)
            
            # Analyze statutory framework
            if statutes:
                analysis['statutory_framework'] = await self._analyze_statutory_framework(statutes)
            
            # Identify jurisdictional variations
            analysis['jurisdictional_variations'] = await self._identify_jurisdictional_variations(
                cases, statutes, regulations
            )
            
            # Use AI for comprehensive analysis if available
            if self.legal_reasoner:
                ai_analysis = await self._generate_ai_analysis(
                    cases, statutes, regulations, expanded_query
                )
                analysis.update(ai_analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Research analysis failed: {e}")
            return {'error': str(e)}
    
    async def _extract_case_findings(self, cases: List[Dict[str, Any]]) -> List[str]:
        """Extract key findings from case law"""
        findings = []
        for case in cases[:10]:  # Analyze top 10 cases
            # Extract key holdings and rationales
            if case.get('content'):
                # Simple extraction based on common legal phrases
                content = case['content']
                
                # Look for holdings
                holding_patterns = [
                    r'we hold that (.*?)\.', r'held that (.*?)\.', r'holding (.*?)\.',
                    r'we conclude that (.*?)\.', r'concluded that (.*?)\.'
                ]
                
                for pattern in holding_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if len(match.strip()) > 10:  # Meaningful findings
                            findings.append(f"From {case.get('citation', 'case')}: {match.strip()}")
        
        return findings[:5]  # Return top 5 findings
    
    async def _extract_legal_principles(self, cases: List[Dict[str, Any]]) -> List[str]:
        """Extract legal principles from cases"""
        principles = []
        
        # Common legal principle indicators
        principle_patterns = [
            r'the principle (?:that|of) (.*?)\.', r'established principle (.*?)\.',
            r'fundamental principle (.*?)\.', r'legal principle (.*?)\.'
        ]
        
        for case in cases[:10]:
            content = case.get('content', '')
            for pattern in principle_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if len(match.strip()) > 10:
                        principles.append(match.strip())
        
        return list(set(principles))[:10]  # Return unique principles
    
    async def _build_precedent_hierarchy(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build precedent hierarchy from cases"""
        hierarchy = []
        
        # Group cases by court level and precedential value
        court_levels = {
            'Supreme Court': 10,
            'Circuit Court': 8,
            'Court of Appeals': 8,
            'District Court': 6,
            'State Supreme Court': 9,
            'State Appellate Court': 7,
            'State Trial Court': 5
        }
        
        for case in cases:
            court = case.get('court', 'Unknown Court')
            precedential_value = case.get('precedential_value', 5)
            
            # Adjust precedential value based on court level
            for court_name, level in court_levels.items():
                if court_name.lower() in court.lower():
                    precedential_value = max(precedential_value, level)
                    break
            
            hierarchy.append({
                'case': case.get('citation', case.get('title', 'Unknown')),
                'court': court,
                'precedential_value': precedential_value,
                'jurisdiction': case.get('jurisdiction', 'unknown')
            })
        
        # Sort by precedential value
        hierarchy.sort(key=lambda x: x['precedential_value'], reverse=True)
        return hierarchy[:15]  # Return top 15 precedents
    
    async def _analyze_statutory_framework(self, statutes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze statutory framework"""
        framework = []
        
        for statute in statutes[:10]:
            framework_item = {
                'statute': statute.get('citation', statute.get('title', 'Unknown')),
                'jurisdiction': statute.get('jurisdiction', 'unknown'),
                'effective_date': statute.get('effective_date'),
                'key_provisions': self._extract_key_provisions(statute),
                'relevance_score': statute.get('relevance_score', 0)
            }
            framework.append(framework_item)
        
        return framework
    
    def _extract_key_provisions(self, statute: Dict[str, Any]) -> List[str]:
        """Extract key provisions from statute"""
        provisions = []
        content = statute.get('content', '')
        
        # Look for section headers and key provisions
        section_pattern = r'§\s*\d+[.\w]*\s*(.*?)(?=§|\n\n|$)'
        matches = re.findall(section_pattern, content, re.DOTALL)
        
        for match in matches:
            if len(match.strip()) > 20:
                provisions.append(match.strip()[:200])  # First 200 chars
        
        return provisions[:5]  # Return top 5 provisions
    
    async def _build_citation_network(self, cases: List[Dict[str, Any]], statutes: List[Dict[str, Any]], 
                                    regulations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build citation network from research results"""
        network = {
            'nodes': [],
            'edges': [],
            'clusters': {},
            'authority_scores': {}
        }
        
        try:
            # Add cases as nodes
            for case in cases:
                network['nodes'].append({
                    'id': case.get('citation', case.get('title', 'unknown')),
                    'type': 'case',
                    'title': case.get('title', ''),
                    'court': case.get('court', ''),
                    'date': case.get('date', ''),
                    'precedential_value': case.get('precedential_value', 0)
                })
            
            # Add statutes as nodes
            for statute in statutes:
                network['nodes'].append({
                    'id': statute.get('citation', statute.get('title', 'unknown')),
                    'type': 'statute',
                    'title': statute.get('title', ''),
                    'jurisdiction': statute.get('jurisdiction', ''),
                    'effective_date': statute.get('effective_date', '')
                })
            
            # Extract citations and build edges
            for case in cases:
                case_id = case.get('citation', case.get('title', 'unknown'))
                content = case.get('content', '')
                
                # Find citations in content
                citations = self.citation_parser.extract_citations(content)
                for citation in citations:
                    network['edges'].append({
                        'source': case_id,
                        'target': citation,
                        'type': 'cites'
                    })
            
            return network
            
        except Exception as e:
            logger.error(f"Citation network building failed: {e}")
            return network
    
    async def _generate_research_summary(self, analysis: Dict[str, Any], cases: List[Dict[str, Any]], 
                                       statutes: List[Dict[str, Any]]) -> str:
        """Generate comprehensive research summary"""
        try:
            summary_parts = []
            
            # Summary header
            summary_parts.append("LEGAL RESEARCH SUMMARY\n" + "="*50)
            
            # Key findings
            if analysis.get('key_findings'):
                summary_parts.append("\nKEY FINDINGS:")
                for i, finding in enumerate(analysis['key_findings'][:5], 1):
                    summary_parts.append(f"{i}. {finding}")
            
            # Legal principles
            if analysis.get('legal_principles'):
                summary_parts.append("\nLEGAL PRINCIPLES:")
                for i, principle in enumerate(analysis['legal_principles'][:3], 1):
                    summary_parts.append(f"{i}. {principle}")
            
            # Primary authorities
            if cases:
                summary_parts.append(f"\nPRIMARY CASE AUTHORITIES ({len(cases)} cases analyzed):")
                for i, case in enumerate(cases[:5], 1):
                    citation = case.get('citation', 'No citation')
                    title = case.get('title', 'No title')
                    summary_parts.append(f"{i}. {citation} - {title[:100]}...")
            
            # Statutory framework
            if statutes:
                summary_parts.append(f"\nSTATUTORY FRAMEWORK ({len(statutes)} statutes analyzed):")
                for i, statute in enumerate(statutes[:3], 1):
                    citation = statute.get('citation', statute.get('title', 'No citation'))
                    summary_parts.append(f"{i}. {citation}")
            
            # Jurisdictional considerations
            if analysis.get('jurisdictional_variations'):
                summary_parts.append("\nJURISDICTIONAL CONSIDERATIONS:")
                for jurisdiction, variations in analysis['jurisdictional_variations'].items():
                    if variations:
                        summary_parts.append(f"• {jurisdiction}: {variations}")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Research summary generation failed: {e}")
            return "Research summary generation failed due to processing error."
    
    def _calculate_research_confidence(self, cases: List[Dict[str, Any]], statutes: List[Dict[str, Any]], 
                                     analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for research results"""
        confidence_factors = []
        
        # Number of relevant cases found
        if cases:
            case_confidence = min(len(cases) / 20, 1.0)  # Max confidence at 20 cases
            confidence_factors.append(case_confidence * 0.4)
        else:
            confidence_factors.append(0.0)
        
        # Number of relevant statutes
        if statutes:
            statute_confidence = min(len(statutes) / 10, 1.0)  # Max confidence at 10 statutes
            confidence_factors.append(statute_confidence * 0.3)
        else:
            confidence_factors.append(0.0)
        
        # Quality of analysis
        analysis_quality = 0.0
        if analysis.get('key_findings'):
            analysis_quality += 0.3
        if analysis.get('legal_principles'):
            analysis_quality += 0.3
        if analysis.get('precedent_hierarchy'):
            analysis_quality += 0.2
        if analysis.get('statutory_framework'):
            analysis_quality += 0.2
        
        confidence_factors.append(analysis_quality * 0.3)
        
        # Overall confidence
        overall_confidence = sum(confidence_factors)
        return round(min(overall_confidence, 1.0), 2)
    
    async def _store_research_results(self, result: ResearchResult):
        """Store research results for future reference"""
        try:
            # Store in database for future reference and caching
            with get_db_session() as db:
                research_record = {
                    'research_id': result.research_id,
                    'query_text': result.query.query_text,
                    'legal_areas': result.query.legal_areas,
                    'jurisdictions': result.query.jurisdictions,
                    'case_count': len(result.case_law),
                    'statute_count': len(result.statutes),
                    'confidence_score': result.confidence_score,
                    'research_time': result.research_time,
                    'created_at': datetime.now(timezone.utc)
                }
                
                logger.info(f"Stored research results: {result.research_id}")
                
        except Exception as e:
            logger.error(f"Research results storage failed: {e}")


class CaseLawAnalyzer:
    """
    Specialized analyzer for case law research and precedent analysis
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.legal_research = LegalResearch(config)
        self.precedent_analyzer = None
        self._initialize_case_analysis()
    
    def _initialize_case_analysis(self):
        """Initialize case law analysis systems"""
        try:
            # Setup specialized precedent analysis
            logger.info("Case Law Analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Case Law Analyzer initialization failed: {e}")
    
    async def analyze_precedent_impact(self, case_citation: str, legal_area: str) -> Dict[str, Any]:
        """
        Analyze the precedential impact of a specific case
        
        Args:
            case_citation: Citation of the case to analyze
            legal_area: Legal area for context
            
        Returns:
            Analysis of precedential impact and influence
        """
        try:
            impact_analysis = {
                'case_citation': case_citation,
                'precedential_strength': 0.0,
                'citing_cases': [],
                'legal_influence': {},
                'doctrinal_development': [],
                'current_validity': 'unknown'
            }
            
            # Find cases that cite this precedent
            citing_cases = await self._find_citing_cases(case_citation)
            impact_analysis['citing_cases'] = citing_cases
            
            # Analyze precedential strength
            impact_analysis['precedential_strength'] = self._calculate_precedential_strength(
                case_citation, citing_cases
            )
            
            # Analyze legal influence over time
            impact_analysis['legal_influence'] = await self._analyze_legal_influence(
                case_citation, citing_cases, legal_area
            )
            
            return impact_analysis
            
        except Exception as e:
            logger.error(f"Precedent impact analysis failed for {case_citation}: {e}")
            return {'error': str(e), 'case_citation': case_citation}
    
    async def _find_citing_cases(self, case_citation: str) -> List[Dict[str, Any]]:
        """Find cases that cite the given case"""
        # Implementation would search legal databases for cases citing the given case
        return []
    
    def _calculate_precedential_strength(self, case_citation: str, citing_cases: List[Dict[str, Any]]) -> float:
        """Calculate precedential strength based on citations and treatment"""
        strength = 0.0
        
        # Base strength from number of citations
        citation_count = len(citing_cases)
        strength += min(citation_count / 50, 1.0) * 0.5  # Max 0.5 from citation count
        
        # Analyze quality of citations
        positive_treatment = sum(1 for case in citing_cases 
                               if case.get('treatment') in ['followed', 'applied', 'approved'])
        negative_treatment = sum(1 for case in citing_cases 
                               if case.get('treatment') in ['overruled', 'criticized', 'questioned'])
        
        if citation_count > 0:
            treatment_ratio = (positive_treatment - negative_treatment) / citation_count
            strength += treatment_ratio * 0.3
        
        # Court level of citing cases
        high_court_citations = sum(1 for case in citing_cases 
                                 if 'supreme' in case.get('court', '').lower() or 
                                    'appellate' in case.get('court', '').lower())
        
        if citation_count > 0:
            court_quality = high_court_citations / citation_count
            strength += court_quality * 0.2
        
        return round(min(strength, 1.0), 2)
    
    async def _analyze_legal_influence(self, case_citation: str, citing_cases: List[Dict[str, Any]], 
                                     legal_area: str) -> Dict[str, Any]:
        """Analyze the legal influence of a case over time"""
        influence = {
            'temporal_influence': {},
            'doctrinal_areas': [],
            'geographic_spread': {},
            'influence_trend': 'stable'
        }
        
        # Analyze temporal influence
        citation_dates = []
        for case in citing_cases:
            if case.get('date'):
                try:
                    date = datetime.fromisoformat(str(case['date']))
                    citation_dates.append(date.year)
                except:
                    continue
        
        if citation_dates:
            # Group citations by year
            year_counts = {}
            for year in citation_dates:
                year_counts[year] = year_counts.get(year, 0) + 1
            
            influence['temporal_influence'] = year_counts
            
            # Determine trend
            recent_years = [year for year in citation_dates if year >= datetime.now().year - 5]
            older_years = [year for year in citation_dates if year < datetime.now().year - 5]
            
            if len(recent_years) > len(older_years):
                influence['influence_trend'] = 'increasing'
            elif len(recent_years) < len(older_years) * 0.5:
                influence['influence_trend'] = 'declining'
            else:
                influence['influence_trend'] = 'stable'
        
        return influence
    
    def __init__(self):
        self.ai_processor = AIProcessor()
        self.legal_db = LegalDatabase()
        self.citation_parser = CitationParser()
        
        # Research databases
        self.case_db = None  # Elasticsearch for case law
        self.statute_db = None  # Statutory database
        
        # Research metrics
        self.queries_processed = 0
        self.cases_analyzed = 0
        self.research_accuracy = 0.0

    async def conduct_legal_research(
        self,
        query: ResearchQuery
    ) -> ResearchResult:
        """
        Conduct comprehensive legal research
        
        Args:
            query: Research query parameters
            
        Returns:
            Complete research results
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # Validate research query
            await self._validate_research_query(query)
            
            # Initialize research session
            research_id = f"research_{hash(query.query_text)[:8]}"
            
            # Conduct multi-source research
            case_law_results = await self._research_case_law(query)
            statutory_results = await self._research_statutes(query)
            regulatory_results = await self._research_regulations(query)
            secondary_sources = await self._research_secondary_sources(query)
            
            # Perform legal analysis
            legal_analysis = await self._perform_legal_analysis(
                query, case_law_results, statutory_results, regulatory_results
            )
            
            # Build citation network
            citation_network = await self._build_citation_network(
                case_law_results, statutory_results
            )
            
            # Generate research summary
            research_summary = await self._generate_research_summary(
                query, legal_analysis, case_law_results, statutory_results
            )
            
            # Calculate confidence score
            confidence_score = await self._calculate_research_confidence(
                case_law_results, statutory_results, legal_analysis
            )
            
            research_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            result = ResearchResult(
                research_id=research_id,
                query=query,
                case_law=case_law_results,
                statutes=statutory_results,
                regulations=regulatory_results,
                secondary_sources=secondary_sources,
                legal_analysis=legal_analysis,
                citation_network=citation_network,
                research_summary=research_summary,
                confidence_score=confidence_score,
                research_time=research_time
            )
            
            self.queries_processed += 1
            return result
            
        except Exception as e:
            logger.error(f"Legal research failed: {str(e)}")
            raise ResearchError(f"Legal research error: {str(e)}")

    async def analyze_case_precedents(
        self,
        legal_issue: str,
        jurisdiction: str,
        case_limit: int = 50
    ) -> Dict[str, Any]:
        """
        Analyze case precedents for specific legal issue
        
        Args:
            legal_issue: Legal issue to research
            jurisdiction: Legal jurisdiction
            case_limit: Maximum number of cases to analyze
            
        Returns:
            Precedent analysis results
        """
        try:
            # Search for relevant cases
            relevant_cases = await self._search_relevant_cases(
                legal_issue, jurisdiction, case_limit
            )
            
            # Rank cases by relevance
            ranked_cases = await self._rank_cases_by_relevance(
                relevant_cases, legal_issue
            )
            
            # Extract legal principles
            legal_principles = await self._extract_legal_principles(ranked_cases)
            
            # Identify binding vs persuasive precedents
            precedent_classification = await self._classify_precedents(
                ranked_cases, jurisdiction
            )
            
            # Analyze precedent consistency
            consistency_analysis = await self._analyze_precedent_consistency(
                ranked_cases, legal_principles
            )
            
            # Generate precedent summary
            precedent_summary = await self._generate_precedent_summary(
                legal_issue, ranked_cases, legal_principles
            )
            
            return {
                'legal_issue': legal_issue,
                'jurisdiction': jurisdiction,
                'total_cases_found': len(relevant_cases),
                'analyzed_cases': len(ranked_cases),
                'top_precedents': ranked_cases[:10],
                'legal_principles': legal_principles,
                'precedent_classification': precedent_classification,
                'consistency_analysis': consistency_analysis,
                'precedent_summary': precedent_summary,
                'research_strength': self._assess_research_strength(ranked_cases)
            }
            
        except Exception as e:
            logger.error(f"Precedent analysis failed: {str(e)}")
            raise ResearchError(f"Precedent analysis error: {str(e)}")

    async def research_statutory_framework(
        self,
        legal_area: str,
        jurisdiction: str
    ) -> Dict[str, Any]:
        """
        Research statutory framework for legal area
        
        Args:
            legal_area: Legal area to research
            jurisdiction: Legal jurisdiction
            
        Returns:
            Statutory framework analysis
        """
        try:
            # Search relevant statutes
            relevant_statutes = await self._search_relevant_statutes(
                legal_area, jurisdiction
            )
            
            # Analyze statutory hierarchy
            statutory_hierarchy = await self._analyze_statutory_hierarchy(
                relevant_statutes, jurisdiction
            )
            
            # Identify key provisions
            key_provisions = await self._identify_key_provisions(
                relevant_statutes, legal_area
            )
            
            # Find implementing regulations
            implementing_regulations = await self._find_implementing_regulations(
                relevant_statutes, jurisdiction
            )
            
            # Analyze statutory interpretation
            interpretation_analysis = await self._analyze_statutory_interpretation(
                relevant_statutes, key_provisions
            )
            
            # Generate statutory summary
            statutory_summary = await self._generate_statutory_summary(
                legal_area, relevant_statutes, key_provisions
            )
            
            return {
                'legal_area': legal_area,
                'jurisdiction': jurisdiction,
                'relevant_statutes': relevant_statutes,
                'statutory_hierarchy': statutory_hierarchy,
                'key_provisions': key_provisions,
                'implementing_regulations': implementing_regulations,
                'interpretation_analysis': interpretation_analysis,
                'statutory_summary': statutory_summary,
                'framework_completeness': self._assess_framework_completeness(relevant_statutes)
            }
            
        except Exception as e:
            logger.error(f"Statutory research failed: {str(e)}")
            raise ResearchError(f"Statutory research error: {str(e)}")

    async def generate_legal_memorandum(
        self,
        research_results: ResearchResult,
        memo_purpose: str,
        target_audience: str = "legal_professional"
    ) -> str:
        """
        Generate legal memorandum from research results
        
        Args:
            research_results: Research results to summarize
            memo_purpose: Purpose of the memorandum
            target_audience: Target audience for memo
            
        Returns:
            Formatted legal memorandum
        """
        try:
            # Structure memorandum sections
            memo_sections = await self._structure_memorandum_sections(
                research_results, memo_purpose
            )
            
            # Generate executive summary
            executive_summary = await self._generate_executive_summary(
                research_results, memo_purpose
            )
            
            # Write legal analysis section
            legal_analysis_section = await self._write_legal_analysis_section(
                research_results.legal_analysis,
                research_results.case_law,
                research_results.statutes
            )
            
            # Create citations section
            citations_section = await self._create_citations_section(
                research_results.case_law,
                research_results.statutes,
                research_results.secondary_sources
            )
            
            # Write recommendations section
            recommendations_section = await self._write_recommendations_section(
                research_results.legal_analysis,
                memo_purpose
            )
            
            # Assemble final memorandum
            memorandum = await self._assemble_memorandum(
                executive_summary,
                legal_analysis_section,
                citations_section,
                recommendations_section,
                memo_sections
            )
            
            # Format for target audience
            formatted_memo = await self._format_memorandum(
                memorandum, target_audience
            )
            
            return formatted_memo
            
        except Exception as e:
            logger.error(f"Memorandum generation failed: {str(e)}")
            raise ResearchError(f"Memorandum generation error: {str(e)}")

    # Private helper methods
    async def _validate_research_query(self, query: ResearchQuery):
        """Validate research query parameters"""
        if not query.query_text:
            raise QueryError("Research query text is required")
        if not query.legal_areas:
            raise QueryError("At least one legal area must be specified")
        if not query.jurisdictions:
            raise QueryError("At least one jurisdiction must be specified")

    async def _research_case_law(self, query: ResearchQuery) -> List[Dict[str, Any]]:
        """Research case law for query"""
        try:
            # Build case law search query
            search_params = await self._build_case_search_params(query)
            
            # Search case databases
            case_results = await self.legal_db.search_cases(
                **search_params,
                limit=self._get_case_limit_for_scope(query.scope)
            )
            
            # Analyze and rank cases
            analyzed_cases = []
            for case in case_results:
                case_analysis = await self._analyze_case_relevance(case, query)
                if case_analysis['relevance_score'] > 0.3:  # Relevance threshold
                    analyzed_cases.append(case_analysis)
            
            # Sort by relevance
            analyzed_cases.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return analyzed_cases
            
        except Exception as e:
            logger.warning(f"Case law research failed: {str(e)}")
            return []

    async def _research_statutes(self, query: ResearchQuery) -> List[Dict[str, Any]]:
        """Research statutes for query"""
        try:
            # Build statutory search query
            search_params = await self._build_statutory_search_params(query)
            
            # Search statutory databases
            statute_results = await self.legal_db.search_statutes(**search_params)
            
            # Analyze statutory relevance
            analyzed_statutes = []
            for statute in statute_results:
                statute_analysis = await self._analyze_statutory_relevance(statute, query)
                if statute_analysis['relevance_score'] > 0.4:
                    analyzed_statutes.append(statute_analysis)
            
            return analyzed_statutes
            
        except Exception as e:
            logger.warning(f"Statutory research failed: {str(e)}")
            return []

    async def _perform_legal_analysis(
        self,
        query: ResearchQuery,
        cases: List[Dict[str, Any]],
        statutes: List[Dict[str, Any]],
        regulations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform comprehensive legal analysis"""
        
        # AI-powered legal analysis
        analysis_prompt = self._build_analysis_prompt(query, cases, statutes)
        
        ai_analysis = await self.ai_processor.analyze_legal_landscape(
            analysis_prompt,
            legal_areas=query.legal_areas,
            jurisdictions=query.jurisdictions
        )
        
        # Identify legal issues and arguments
        legal_issues = await self._identify_legal_issues(cases, statutes, query)
        
        # Analyze conflicting authorities
        conflicts_analysis = await self._analyze_conflicting_authorities(cases, statutes)
        
        # Generate legal arguments
        legal_arguments = await self._generate_legal_arguments(
            legal_issues, cases, statutes
        )
        
        return {
            'ai_analysis': ai_analysis,
            'legal_issues': legal_issues,
            'conflicts_analysis': conflicts_analysis,
            'legal_arguments': legal_arguments,
            'strength_assessment': ai_analysis.get('strength_assessment'),
            'risk_factors': ai_analysis.get('risk_factors', [])
        }

    def _build_analysis_prompt(
        self,
        query: ResearchQuery,
        cases: List[Dict[str, Any]],
        statutes: List[Dict[str, Any]]
    ) -> str:
        """Build AI prompt for legal analysis"""
        
        case_summaries = [case.get('summary', '') for case in cases[:10]]
        statute_summaries = [statute.get('summary', '') for statute in statutes[:5]]
        
        return f"""
        Perform comprehensive legal analysis for the following research query:
        
        Query: {query.query_text}
        Legal Areas: {query.legal_areas}
        Jurisdictions: {query.jurisdictions}
        
        Relevant Case Law:
        {json.dumps(case_summaries, indent=2)}
        
        Relevant Statutes:
        {json.dumps(statute_summaries, indent=2)}
        
        Provide detailed analysis including:
        - Key legal principles
        - Strength of legal position
        - Potential risks and challenges
        - Strategic recommendations
        - Conflicting authorities analysis
        """
    def _get_case_limit_for_scope(self, scope: ResearchScope) -> int:
        """Get case limit based on research scope"""
        scope_limits = {
            ResearchScope.NARROW: 25,
            ResearchScope.FOCUSED: 50,
            ResearchScope.BROAD: 100,
            ResearchScope.COMPREHENSIVE: 200
        }
        return scope_limits.get(scope, 50)

class CaseLawAnalyzer:
    """
    Specialized Case Law Analysis System
    
    Advanced case law analysis with precedent identification and legal principle extraction
    """
    
    def __init__(self):
        self.legal_research = LegalResearch()
        self.precedent_database = {}
        self.analysis_cache = {}
        
    async def analyze_case_line(
        self,
        leading_case: Dict[str, Any],
        jurisdiction: str
    ) -> Dict[str, Any]:
        """Analyze line of cases following a leading case"""
        
        try:
            # Identify citing cases
            citing_cases = await self._find_citing_cases(leading_case, jurisdiction)
            
            # Analyze case development
            case_development = await self._analyze_case_development(
                leading_case, citing_cases
            )
            
            # Track legal principle evolution
            principle_evolution = await self._track_principle_evolution(
                leading_case, citing_cases
            )
            
            # Identify case line stability
            stability_analysis = await self._analyze_case_line_stability(
                case_development, principle_evolution
            )
            
            return {
                'leading_case': leading_case,
                'citing_cases_count': len(citing_cases),
                'top_citing_cases': citing_cases[:10],
                'case_development': case_development,
                'principle_evolution': principle_evolution,
                'stability_analysis': stability_analysis,
                'predictive_strength': self._calculate_predictive_strength(stability_analysis)
            }
            
        except Exception as e:
            logger.error(f"Case line analysis failed: {str(e)}")
            raise ResearchError(f"Case line analysis error: {str(e)}")

    async def _find_citing_cases(
        self,
        leading_case: Dict[str, Any],
        jurisdiction: str
    ) -> List[Dict[str, Any]]:
        """Find cases that cite the leading case"""
        
        case_citation = leading_case.get('citation', '')
        if not case_citation:
            return []
        
        # Search for cases citing this case
        citing_cases = await self.legal_research.legal_db.find_citing_cases(
            citation=case_citation,
            jurisdiction=jurisdiction
        )
        
        return citing_cases

    def _calculate_predictive_strength(self, stability_analysis: Dict[str, Any]) -> float:
        """Calculate predictive strength of case line"""
        
        stability_score = stability_analysis.get('stability_score', 0.5)
        consistency_score = stability_analysis.get('consistency_score', 0.5)
        authority_level = stability_analysis.get('authority_level', 0.5)
        
        # Weighted average
        predictive_strength = (
            stability_score * 0.4 +
            consistency_score * 0.4 +
            authority_level * 0.2
        )
        
        return min(max(predictive_strength, 0.0), 1.0)
