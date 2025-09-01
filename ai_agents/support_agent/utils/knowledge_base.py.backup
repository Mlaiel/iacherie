"""Knowledge Base Manager - Ultra-Advanced AI Knowledge Management System

Enterprise-grade knowledge management system providing semantic search, intelligent
content curation, dynamic learning, and contextual information retrieval for
customer support operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import hashlib
import re
from collections import defaultdict, Counter

# Vector search and embeddings
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import torch

# Text processing and NLP
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Database and caching
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func

logger = logging.getLogger(__name__)

class KnowledgeCategory(Enum):
    """Knowledge base categories"""
    TECHNICAL_SUPPORT = "technical_support"
    USER_GUIDES = "user_guides"
    API_DOCUMENTATION = "api_documentation"
    TROUBLESHOOTING = "troubleshooting"
    BILLING_SUPPORT = "billing_support"
    FEATURE_TUTORIALS = "feature_tutorials"
    CONTENT_PROTECTION = "content_protection"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    PLATFORM_INTEGRATION = "platform_integration"
    SECURITY = "security"
    COMPLIANCE = "compliance"

class ContentType(Enum):
    """Types of knowledge content"""
    ARTICLE = "article"
    FAQ = "faq"
    TUTORIAL = "tutorial"
    VIDEO = "video"
    INFOGRAPHIC = "infographic"
    CODE_SNIPPET = "code_snippet"
    TROUBLESHOOTING_GUIDE = "troubleshooting_guide"
    POLICY_DOCUMENT = "policy_document"

class ContentStatus(Enum):
    """Content status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    UNDER_REVIEW = "under_review"

@dataclass
class KnowledgeArticle:
    """Knowledge base article structure"""
    id: str
    title: str
    content: str
    category: KnowledgeCategory
    content_type: ContentType
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    author: str = "AI Support System"
    language: str = "en"
    
    # Status and versioning
    status: ContentStatus = ContentStatus.PUBLISHED
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Analytics and usage
    view_count: int = 0
    usefulness_score: float = 0.0
    feedback_count: int = 0
    success_rate: float = 0.0
    
    # Search optimization
    embedding: Optional[np.ndarray] = None
    tfidf_vector: Optional[np.ndarray] = None
    search_terms: List[str] = field(default_factory=list)
    
    # Relationships
    related_articles: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    follow_ups: List[str] = field(default_factory=list)

@dataclass
class SearchQuery:
    """Search query with context"""
    query: str
    user_id: str
    session_id: str
    
    # Query context
    category_filter: Optional[KnowledgeCategory] = None
    content_type_filter: Optional[ContentType] = None
    language_filter: str = "en"
    
    # Search parameters
    max_results: int = 10
    similarity_threshold: float = 0.7
    include_related: bool = True
    
    # User context
    user_level: str = "beginner"  # beginner, intermediate, advanced
    previous_queries: List[str] = field(default_factory=list)
    current_issue: Optional[str] = None
    
    # Metadata
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    session_context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SearchResult:
    """Search result with relevance scoring"""
    article: KnowledgeArticle
    relevance_score: float
    match_type: str  # "exact", "semantic", "keyword", "related"
    
    # Matching details
    matched_terms: List[str] = field(default_factory=list)
    snippet: str = ""
    highlight_ranges: List[Tuple[int, int]] = field(default_factory=list)
    
    # Context relevance
    category_match: bool = False
    user_level_appropriate: bool = True
    recency_score: float = 1.0

class KnowledgeBaseManager:
    """Ultra-advanced knowledge base management system"""
    
    def __init__(
        self,
        redis_client: aioredis.Redis,
        db_session: AsyncSession,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        self.redis_client = redis_client
        self.db_session = db_session
        
        # Initialize AI models
        self.embedding_model = SentenceTransformer(embedding_model)
        self.qa_model = pipeline(
            "question-answering",
            model="deepset/roberta-base-squad2",
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Initialize NLP tools
        self.nlp = spacy.load("en_core_web_sm")
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        
        # Vector indexes
        self.faiss_index: Optional[faiss.Index] = None
        self.article_mappings: Dict[int, str] = {}
        
        # Cache and statistics
        self.search_cache: Dict[str, Any] = {}
        self.usage_stats: Dict[str, int] = defaultdict(int)
        self.knowledge_articles: Dict[str, KnowledgeArticle] = {}
        
        # Initialize knowledge base
        asyncio.create_task(self._initialize_knowledge_base())
    
    async def _initialize_knowledge_base(self):
        """Initialize knowledge base with default content"""
        try:
            await self._load_existing_articles()
            await self._create_default_articles()
            await self._build_vector_index()
            await self._precompute_relationships()
            
            logger.info("Knowledge base initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize knowledge base: {str(e)}")
    
    async def _create_default_articles(self):
        """Create comprehensive default knowledge base articles"""
        default_articles = [
            # Technical Support Articles
            KnowledgeArticle(
                id="tech_001",
                title="Audio Upload Issues - Complete Troubleshooting Guide",
                content="""
                # Audio Upload Issues - Complete Troubleshooting Guide
                
                ## Common Upload Problems and Solutions
                
                ### 1. File Format Issues
                **Supported Formats:** MP3, WAV, FLAC, AAC, OGG
                - **Problem:** "Unsupported file format" error
                - **Solution:** Convert your file to MP3 or WAV using a free converter
                - **Tools:** Audacity (free), FFmpeg, or online converters
                
                ### 2. File Size Limitations
                **Maximum Size:** 100MB per file
                - **Problem:** "File too large" error
                - **Solution:** Compress your audio file or reduce quality
                - **Steps:**
                  1. Use Audacity to export at lower bitrate (128kbps minimum)
                  2. Trim unnecessary silence
                  3. Use MP3 compression instead of WAV
                
                ### 3. Network Connection Issues
                **Symptoms:** Upload stalls, timeouts, or fails randomly
                - **Solutions:**
                  1. Check internet connection speed (minimum 5Mbps recommended)
                  2. Try uploading during off-peak hours
                  3. Use ethernet instead of WiFi
                  4. Disable VPN temporarily
                
                ### 4. Browser-Related Issues
                **Common Problems:** JavaScript errors, cache conflicts
                - **Solutions:**
                  1. Clear browser cache and cookies
                  2. Disable browser extensions temporarily
                  3. Try incognito/private mode
                  4. Update browser to latest version
                  5. Try different browser (Chrome, Firefox, Safari)
                
                ### 5. Account and Permissions
                **Verification Required:** Some uploads require verified accounts
                - **Check:** Account verification status
                - **Action:** Complete email verification if pending
                - **Permissions:** Ensure account has upload rights
                
                ## Advanced Troubleshooting
                
                ### Audio File Corruption Detection
                1. Try playing the file in multiple players
                2. Check file properties for unusual characteristics
                3. Re-export from original source if available
                
                ### Server-Side Issues
                If all else fails, the problem might be server-side:
                - Check our status page: status.ia-influencer.com
                - Contact support with error details
                - Include browser console logs if possible
                
                ## Prevention Tips
                1. Always keep backup copies of original files
                2. Test uploads with smaller files first
                3. Use supported formats from the start
                4. Ensure stable internet connection before large uploads
                
                **Still having issues?** Contact our support team with:
                - File format and size
                - Browser and version
                - Error messages
                - Screenshots of the issue
                """,
                category=KnowledgeCategory.TECHNICAL_SUPPORT,
                content_type=ContentType.TROUBLESHOOTING_GUIDE,
                tags=["audio", "upload", "troubleshooting", "file-format", "error"],
                keywords=["upload error", "audio file", "file format", "network issue", "browser problem"],
                search_terms=["can't upload", "upload failed", "audio not uploading", "file format error"]
            ),
            
            KnowledgeArticle(
                id="content_001",
                title="Content Protection and Copyright Detection System",
                content="""
                # Content Protection and Copyright Detection System
                
                ## How Our AI Protection Works
                
                ### Audio Fingerprinting Technology
                Our advanced AI system creates unique "fingerprints" for your content:
                
                1. **Acoustic Analysis:** Analyzes frequency patterns, tempo, and harmonic structure
                2. **Spectral Fingerprinting:** Creates mathematical signatures of your audio
                3. **Machine Learning Detection:** Continuously improving recognition accuracy
                4. **Real-time Monitoring:** 24/7 scanning across 1000+ platforms
                
                ### Multi-Format Protection
                **Audio Formats Supported:**
                - MP3, WAV, FLAC, AAC, OGG
                - Quality: 128kbps minimum for accurate detection
                - Duration: 30 seconds minimum for fingerprinting
                
                **Video Formats:**
                - MP4, AVI, MOV, WMV, FLV
                - Audio track extraction for sound matching
                - Visual scene recognition (coming soon)
                
                **Image Formats:**
                - JPG, PNG, GIF, WebP
                - Reverse image search integration
                - Metadata preservation and tracking
                
                ### How to Enable Protection
                
                #### Step 1: Upload Your Content
                1. Navigate to "Content Protection" dashboard
                2. Click "Upload for Protection"
                3. Select files or drag & drop
                4. Add metadata: title, description, tags
                
                #### Step 2: Configure Protection Settings
                - **Sensitivity Level:** High (recommended), Medium, Low
                - **Monitoring Scope:** Global, Regional, or Platform-specific
                - **Action on Detection:** Notify, Report, or Auto-claim
                
                #### Step 3: Verification Process
                - System processes and creates fingerprints
                - Usually takes 5-15 minutes depending on file size
                - Email notification when protection is active
                
                ### Understanding Detection Results
                
                #### Match Accuracy Levels
                - **Exact Match (95-100%):** Identical or near-identical content
                - **High Similarity (80-94%):** Very similar with minor changes
                - **Moderate Similarity (60-79%):** Significant portions match
                - **Low Similarity (40-59%):** Some similarities detected
                
                #### Common Detection Scenarios
                1. **Direct Copy:** Exact file uploaded elsewhere
                2. **Quality Change:** Compressed or format-converted versions
                3. **Edit Derivatives:** Remixed, cut, or modified versions
                4. **Sample Usage:** Your content used in other works
                
                ### Taking Action on Infringement
                
                #### Automated Responses
                - **DMCA Takedown:** Automatic filing with platforms
                - **Content Claiming:** Monetization rights assertion
                - **Warning Messages:** Sent to infringers
                
                #### Manual Review Process
                1. Review detected matches in dashboard
                2. Verify legitimate vs. false positives
                3. Choose appropriate action
                4. Track resolution progress
                
                ### Best Practices for Protection
                
                1. **Upload Original Quality:** Higher quality = better detection
                2. **Complete Metadata:** Helps with ownership verification
                3. **Regular Monitoring:** Check dashboard weekly
                4. **Prompt Action:** Respond to detections quickly
                5. **Documentation:** Keep records of creation and ownership
                
                ### Collaborative Creator Protection
                When working with other creators:
                - Set up shared protection agreements
                - Define revenue sharing for detected content
                - Establish clear ownership percentages
                - Use collaborative protection tags
                
                **Need help with protection setup?** Our AI assistant can guide you through the process step-by-step!
                """,
                category=KnowledgeCategory.CONTENT_PROTECTION,
                content_type=ContentType.USER_GUIDES,
                tags=["copyright", "protection", "fingerprinting", "detection", "AI"],
                keywords=["content protection", "copyright detection", "fingerprint", "piracy", "DMCA"],
                search_terms=["protect my content", "copyright protection", "detect copying", "fingerprint audio"]
            ),
            
            KnowledgeArticle(
                id="collab_001",
                title="Collaboration Features and Creator Matching",
                content="""
                # Collaboration Features and Creator Matching
                
                ## AI-Powered Creator Discovery
                
                ### How Creator Matching Works
                Our intelligent system analyzes multiple factors to suggest ideal collaborators:
                
                1. **Musical Style Analysis:** Genre, tempo, key signatures, and mood
                2. **Content Quality Metrics:** Engagement rates, production quality, consistency
                3. **Collaboration History:** Past successful partnerships and ratings
                4. **Audience Overlap:** Complementary vs. competitive audience analysis
                5. **Professional Goals:** Career objectives and project preferences
                
                ### Setting Up Your Collaboration Profile
                
                #### Profile Optimization
                1. **Complete Your Profile:**
                   - Musical genres and subgenres
                   - Instruments and vocal ranges
                   - Production skills and equipment
                   - Previous collaboration experience
                
                2. **Portfolio Showcase:**
                   - Upload 3-5 best representative tracks
                   - Include various styles and moods
                   - Add project descriptions and your role
                   - Link to streaming platforms
                
                3. **Collaboration Preferences:**
                   - Types of projects (singles, albums, live performances)
                   - Preferred communication methods
                   - Timeline expectations
                   - Revenue sharing preferences
                
                ### Types of Collaborations Available
                
                #### 1. Musical Collaborations
                **Producer-Artist Partnerships:**
                - Beat makers with vocalists/rappers
                - Instrumentalists with songwriters
                - Mixing/mastering engineers with creators
                
                **Multi-Artist Collaborations:**
                - Featured artist opportunities
                - Remix and remix contest participation
                - Group project formations
                
                #### 2. Content Collaborations
                **Cross-Format Projects:**
                - Musicians with video creators
                - Audio content with visual artists
                - Podcast collaborations with music creators
                
                **Brand Partnerships:**
                - Sponsored content collaborations
                - Product placement opportunities
                - Brand ambassador programs
                
                ### Collaboration Workflow
                
                #### Phase 1: Discovery and Matching
                1. **AI Recommendations:** System suggests potential collaborators
                2. **Manual Search:** Use filters to find specific types of creators
                3. **Community Browsing:** Explore featured creators and trending collaborators
                
                #### Phase 2: Initial Contact
                1. **Send Collaboration Request:**
                   - Include project description
                   - Specify your needs and what you offer
                   - Attach relevant portfolio samples
                   - Suggest timeline and terms
                
                2. **Response and Negotiation:**
                   - Built-in messaging system
                   - Terms and conditions templates
                   - Revenue sharing calculators
                   - Contract generation tools
                
                #### Phase 3: Project Management
                **Collaborative Workspace Features:**
                - Shared file storage (up to 10GB per project)
                - Version control for audio files
                - Real-time commenting and feedback
                - Task assignment and deadline tracking
                
                **Communication Tools:**
                - Built-in video conferencing
                - Voice note exchange
                - Real-time chat with translation
                - Scheduled meeting coordination
                
                #### Phase 4: Content Creation
                **Production Tools:**
                - Collaborative audio editing (basic)
                - Reference track sharing
                - Sync and alignment tools
                - Quality check automation
                
                **Rights Management:**
                - Automatic split sheet generation
                - Copyright co-ownership documentation
                - Performance rights distribution setup
                - Publishing administration coordination
                
                ### Revenue Sharing and Rights
                
                #### Automated Revenue Distribution
                1. **Smart Contracts:** Blockchain-based automatic splitting
                2. **Platform Integration:** Direct splits from Spotify, Apple Music, etc.
                3. **Performance Royalties:** ASCAP/BMI/SESAC coordination
                4. **Merchandise Revenue:** Shared product sales
                
                #### Legal Protection
                - Template collaboration agreements
                - Intellectual property protection
                - Dispute resolution services
                - Legal consultation referrals
                
                ### Success Metrics and Analytics
                
                #### Collaboration Performance Tracking
                - **Engagement Metrics:** Streams, downloads, shares
                - **Audience Growth:** New followers gained through collaboration
                - **Revenue Analytics:** Earnings breakdown by platform
                - **Professional Growth:** Network expansion and opportunities
                
                #### Creator Reputation System
                - **Reliability Score:** Meeting deadlines and commitments
                - **Quality Rating:** Peer reviews and feedback
                - **Collaboration Success:** Percentage of completed projects
                - **Professional Growth:** Career advancement tracking
                
                ### Tips for Successful Collaborations
                
                1. **Clear Communication:** Set expectations early and often
                2. **Defined Roles:** Everyone knows their responsibilities
                3. **Fair Terms:** Equitable revenue and credit sharing
                4. **Professional Attitude:** Treat it like a business partnership
                5. **Creative Freedom:** Allow space for artistic expression
                6. **Timeline Respect:** Meet deadlines and communicate delays
                7. **Quality Standards:** Maintain high production values
                8. **Promotion Support:** Cross-promote the collaboration
                
                **Ready to collaborate?** Use our AI matching system to find your perfect creative partner today!
                """,
                category=KnowledgeCategory.COLLABORATION,
                content_type=ContentType.USER_GUIDES,
                tags=["collaboration", "matching", "partnership", "revenue-sharing", "networking"],
                keywords=["find collaborators", "music collaboration", "creator matching", "partnership", "revenue split"],
                search_terms=["find music partner", "collaboration features", "creator matching", "work together"]
            ),
            
            # Billing and Monetization
            KnowledgeArticle(
                id="billing_001",
                title="Subscription Plans and Billing Management",
                content="""
                # Subscription Plans and Billing Management
                
                ## Available Subscription Tiers
                
                ### Free Tier - Content Creator Starter
                **Perfect for:** New creators testing the platform
                
                **Features Included:**
                - Up to 5 audio uploads per month
                - Basic content protection (1 platform monitoring)
                - Community collaboration access
                - Standard customer support
                - 1GB storage space
                - Basic analytics dashboard
                
                **Limitations:**
                - No advanced AI features
                - Limited copyright detection
                - No priority support
                - Basic collaboration tools only
                
                ### Pro Tier - $29.99/month
                **Perfect for:** Serious creators and small labels
                
                **Everything in Free, plus:**
                - Unlimited audio uploads
                - Advanced content protection (10+ platforms)
                - Priority customer support
                - AI-powered creator matching
                - Advanced analytics and insights
                - 50GB storage space
                - Revenue optimization tools
                - Custom branding options
                - Collaboration project management
                - DMCA takedown automation
                
                ### Enterprise Tier - $99.99/month
                **Perfect for:** Record labels and music businesses
                
                **Everything in Pro, plus:**
                - Multi-user account management
                - White-label platform options
                - Advanced API access
                - Dedicated account manager
                - Custom integration support
                - Unlimited storage
                - Advanced revenue analytics
                - Bulk content processing
                - Priority platform partnerships
                - Custom contract templates
                
                ### Creator Network - $199.99/month
                **Perfect for:** Creator collectives and networks
                
                **Everything in Enterprise, plus:**
                - Network-wide analytics dashboard
                - Cross-creator revenue sharing
                - Collective bargaining tools
                - Network branding and promotion
                - Advanced collaboration matching
                - Group licensing opportunities
                - Collective content protection
                - Network performance bonuses
                
                ## Payment Methods and Billing
                
                ### Accepted Payment Methods
                **Credit/Debit Cards:**
                - Visa, Mastercard, American Express
                - Automated monthly/yearly billing
                - Secure tokenized storage
                - International cards accepted
                
                **Digital Payments:**
                - PayPal integration
                - Apple Pay and Google Pay
                - Bank transfer (annual plans)
                - Cryptocurrency (Bitcoin, Ethereum)
                
                **Business Accounts:**
                - Purchase orders (Enterprise+)
                - Net 30 payment terms
                - Bulk discount negotiations
                - Custom invoicing
                
                ### Billing Cycles and Discounts
                
                #### Monthly vs. Annual Billing
                **Monthly Billing:**
                - Pay monthly, cancel anytime
                - Full access during paid period
                - No long-term commitment
                
                **Annual Billing (20% Discount):**
                - Pro: $287.88/year (save $71.88)
                - Enterprise: $959.88/year (save $239.88)
                - Network: $1,919.88/year (save $479.88)
                
                #### Additional Discounts
                - **Student Discount:** 50% off Pro tier with valid .edu email
                - **Non-Profit:** 30% off any tier with 501(c)(3) verification
                - **Group Plans:** 15% off for 5+ creators
                - **Referral Bonus:** 1 month free for successful referrals
                
                ### Managing Your Subscription
                
                #### Upgrading Your Plan
                1. Go to Account Settings → Billing
                2. Select "Change Plan"
                3. Choose new tier
                4. Confirm payment method
                5. Immediate access to new features
                6. Prorated billing adjustment
                
                #### Downgrading Your Plan
                - Changes take effect at next billing cycle
                - Access to premium features until cycle end
                - Data retained but may become inaccessible
                - Re-upgrade possible at any time
                
                #### Cancellation Process
                1. Account Settings → Billing → Cancel Subscription
                2. Select cancellation reason (helps us improve)
                3. Confirm cancellation
                4. Access continues until current period ends
                5. Account converts to Free tier
                6. Premium content remains but becomes read-only
                
                ### Revenue Tracking and Payouts
                
                #### Revenue Sources
                **Platform Royalties:**
                - Streaming platforms (Spotify, Apple Music, etc.)
                - Download sales
                - Sync licensing revenue
                - Performance royalties
                
                **Collaboration Revenue:**
                - Shared track earnings
                - Feature appearance fees
                - Production credits
                - Remix competition prizes
                
                **Protection Revenue:**
                - Content claiming monetization
                - License fee collection
                - Settlement distributions
                - Usage fee collection
                
                #### Payout Schedule
                - **Monthly Payouts:** Minimum $50 threshold
                - **Processing Time:** 2-5 business days
                - **Payment Methods:** Bank transfer, PayPal, check
                - **International:** Wire transfer available
                - **Tax Documents:** Automatic 1099 generation
                
                ### Billing Support and Troubleshooting
                
                #### Common Billing Issues
                **Payment Failed:**
                - Check card expiration and limits
                - Verify billing address matches card
                - Contact bank if international transaction blocked
                - Update payment method if needed
                
                **Subscription Questions:**
                - Billing cycle dates and prorations
                - Feature access after plan changes
                - Refund policies and procedures
                - Account sharing and user limits
                
                #### Getting Billing Help
                1. **Self-Service:** Account Settings → Billing → Help
                2. **Live Chat:** Available 24/7 for billing questions
                3. **Phone Support:** Priority number for paid subscribers
                4. **Email Support:** billing@ia-influencer.com
                
                ### Enterprise Custom Solutions
                
                For organizations with specific needs:
                - Custom feature development
                - Volume licensing discounts
                - Dedicated infrastructure
                - SLA guarantees
                - Custom integration support
                - Training and onboarding
                
                **Contact our Enterprise team:** enterprise@ia-influencer.com
                
                **Questions about billing?** Our support team is here to help 24/7!
                """,
                category=KnowledgeCategory.BILLING_SUPPORT,
                content_type=ContentType.USER_GUIDES,
                tags=["billing", "subscription", "payment", "plans", "pricing"],
                keywords=["subscription cost", "billing cycle", "payment failed", "cancel subscription", "upgrade plan"],
                search_terms=["how much does it cost", "billing problem", "change plan", "cancel account"]
            )
        ]
        
        # Add articles to knowledge base
        for article in default_articles:
            if article.id not in self.knowledge_articles:
                self.knowledge_articles[article.id] = article
                await self._cache_article(article)
        
        logger.info(f"Created {len(default_articles)} default knowledge articles")
    
    async def add_article(self, article: KnowledgeArticle) -> bool:
        """Add new article to knowledge base"""
        try:
            # Generate embedding
            article.embedding = self.embedding_model.encode(
                f"{article.title} {article.content}",
                convert_to_numpy=True
            )
            
            # Extract keywords and search terms
            await self._process_article_content(article)
            
            # Store article
            self.knowledge_articles[article.id] = article
            await self._cache_article(article)
            
            # Update indexes
            await self._update_vector_index(article)
            
            logger.info(f"Added article {article.id}: {article.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add article {article.id}: {str(e)}")
            return False
    
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform comprehensive knowledge base search"""
        try:
            start_time = datetime.now()
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query.query, convert_to_numpy=True)
            
            # Perform different types of searches
            semantic_results = await self._semantic_search(query, query_embedding)
            keyword_results = await self._keyword_search(query)
            exact_results = await self._exact_match_search(query)
            
            # Combine and rank results
            all_results = {}
            
            # Add semantic results
            for result in semantic_results:
                all_results[result.article.id] = result
            
            # Enhance with keyword results
            for result in keyword_results:
                if result.article.id in all_results:
                    # Boost existing result
                    all_results[result.article.id].relevance_score += result.relevance_score * 0.3
                else:
                    all_results[result.article.id] = result
            
            # Boost exact matches
            for result in exact_results:
                if result.article.id in all_results:
                    all_results[result.article.id].relevance_score += 0.5
                else:
                    all_results[result.article.id] = result
            
            # Apply filters and context boosting
            filtered_results = await self._apply_filters_and_context(
                list(all_results.values()),
                query
            )
            
            # Sort by relevance and limit results
            final_results = sorted(
                filtered_results,
                key=lambda x: x.relevance_score,
                reverse=True
            )[:query.max_results]
            
            # Add related articles if requested
            if query.include_related:
                final_results = await self._add_related_articles(final_results, query)
            
            # Update usage statistics
            search_time = (datetime.now() - start_time).total_seconds()
            await self._update_search_stats(query, len(final_results), search_time)
            
            return final_results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
    
    async def _semantic_search(
        self,
        query: SearchQuery,
        query_embedding: np.ndarray
    ) -> List[SearchResult]:
        """Perform semantic similarity search"""
        if not self.faiss_index:
            return []
        
        try:
            # Search FAISS index
            scores, indices = self.faiss_index.search(
                query_embedding.reshape(1, -1),
                min(query.max_results * 2, len(self.knowledge_articles))
            )
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1 or score < query.similarity_threshold:
                    continue
                
                article_id = self.article_mappings.get(idx)
                if not article_id or article_id not in self.knowledge_articles:
                    continue
                
                article = self.knowledge_articles[article_id]
                
                # Create search result
                result = SearchResult(
                    article=article,
                    relevance_score=float(score),
                    match_type="semantic",
                    snippet=await self._generate_snippet(article, query.query)
                )
                
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}")
            return []
    
    async def _keyword_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform keyword-based search"""
        results = []
        query_lower = query.query.lower()
        query_terms = self._extract_keywords(query.query)
        
        for article in self.knowledge_articles.values():
            score = 0.0
            matched_terms = []
            
            # Check title matches
            if query_lower in article.title.lower():
                score += 2.0
                matched_terms.append("title")
            
            # Check keyword matches
            for keyword in article.keywords:
                if keyword.lower() in query_lower:
                    score += 1.5
                    matched_terms.append(keyword)
            
            # Check search terms
            for search_term in article.search_terms:
                if search_term.lower() in query_lower:
                    score += 1.8
                    matched_terms.append(search_term)
            
            # Check content matches
            content_lower = article.content.lower()
            for term in query_terms:
                if term in content_lower:
                    score += 0.5
                    matched_terms.append(term)
            
            # Check tags
            for tag in article.tags:
                if tag.lower() in query_lower:
                    score += 1.0
                    matched_terms.append(tag)
            
            if score > 0:
                result = SearchResult(
                    article=article,
                    relevance_score=score,
                    match_type="keyword",
                    matched_terms=matched_terms,
                    snippet=await self._generate_snippet(article, query.query)
                )
                results.append(result)
        
        return results
    
    async def _exact_match_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform exact phrase matching"""
        results = []
        query_lower = query.query.lower().strip()
        
        if len(query_lower) < 3:
            return results
        
        for article in self.knowledge_articles.values():
            score = 0.0
            
            # Exact title match
            if query_lower == article.title.lower():
                score += 5.0
            
            # Exact content phrase match
            if query_lower in article.content.lower():
                score += 3.0
            
            # Exact keyword match
            for keyword in article.keywords:
                if query_lower == keyword.lower():
                    score += 4.0
            
            if score > 0:
                result = SearchResult(
                    article=article,
                    relevance_score=score,
                    match_type="exact",
                    snippet=await self._generate_snippet(article, query.query)
                )
                results.append(result)
        
        return results
    
    async def _apply_filters_and_context(
        self,
        results: List[SearchResult],
        query: SearchQuery
    ) -> List[SearchResult]:
        """Apply filters and context-based boosting"""
        filtered_results = []
        
        for result in results:
            article = result.article
            
            # Apply category filter
            if query.category_filter and article.category != query.category_filter:
                continue
            
            # Apply content type filter
            if query.content_type_filter and article.content_type != query.content_type_filter:
                continue
            
            # Apply language filter
            if article.language != query.language_filter:
                continue
            
            # Context-based boosting
            boost_factor = 1.0
            
            # Category relevance boost
            if query.category_filter and article.category == query.category_filter:
                boost_factor += 0.3
                result.category_match = True
            
            # Recent content boost
            days_old = (datetime.now(timezone.utc) - article.updated_at).days
            if days_old < 30:
                recency_boost = 1.2 - (days_old / 100)
                boost_factor += recency_boost
                result.recency_score = recency_boost
            
            # Popular content boost
            if article.usefulness_score > 0.8:
                boost_factor += 0.2
            
            # Success rate boost
            if article.success_rate > 0.7:
                boost_factor += 0.15
            
            # Apply boost
            result.relevance_score *= boost_factor
            
            # Check minimum threshold
            if result.relevance_score >= query.similarity_threshold:
                filtered_results.append(result)
        
        return filtered_results
    
    async def _add_related_articles(
        self,
        results: List[SearchResult],
        query: SearchQuery
    ) -> List[SearchResult]:
        """Add related articles to search results"""
        if not results:
            return results
        
        # Get related articles for top results
        related_articles = set()
        for result in results[:3]:  # Only for top 3 results
            related_articles.update(result.article.related_articles)
        
        # Add related articles that aren't already in results
        existing_ids = {r.article.id for r in results}
        for article_id in related_articles:
            if article_id not in existing_ids and article_id in self.knowledge_articles:
                article = self.knowledge_articles[article_id]
                
                related_result = SearchResult(
                    article=article,
                    relevance_score=0.4,  # Lower score for related content
                    match_type="related",
                    snippet=await self._generate_snippet(article, query.query)
                )
                results.append(related_result)
        
        return results
    
    async def _generate_snippet(self, article: KnowledgeArticle, query: str) -> str:
        """Generate contextual snippet from article"""
        try:
            # Use QA model to find relevant snippet
            qa_input = {
                'question': query,
                'context': article.content[:2000]  # Limit context length
            }
            
            result = self.qa_model(qa_input)
            
            if result['score'] > 0.1:
                return result['answer']
            
            # Fallback: extract paragraph containing query terms
            query_terms = self._extract_keywords(query)
            sentences = article.content.split('. ')
            
            for sentence in sentences:
                if any(term.lower() in sentence.lower() for term in query_terms):
                    # Return sentence with some context
                    idx = sentences.index(sentence)
                    start_idx = max(0, idx - 1)
                    end_idx = min(len(sentences), idx + 2)
                    return '. '.join(sentences[start_idx:end_idx])
            
            # Final fallback: first paragraph
            first_paragraph = article.content.split('\n\n')[0]
            return first_paragraph[:200] + "..." if len(first_paragraph) > 200 else first_paragraph
            
        except Exception as e:
            logger.error(f"Snippet generation failed: {str(e)}")
            return article.content[:200] + "..."
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Remove common stop words and extract meaningful terms
        doc = self.nlp(text.lower())
        keywords = []
        
        for token in doc:
            if (not token.is_stop and 
                not token.is_punct and 
                len(token.text) > 2 and
                token.is_alpha):
                keywords.append(token.text)
        
        return keywords
    
    async def _process_article_content(self, article: KnowledgeArticle):
        """Process article content to extract metadata"""
        # Extract keywords using NLP
        doc = self.nlp(article.content)
        
        # Extract noun phrases and entities
        entities = [ent.text.lower() for ent in doc.ents]
        noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks if len(chunk.text) > 3]
        
        # Combine with existing keywords
        all_keywords = set(article.keywords + entities + noun_phrases)
        article.keywords = list(all_keywords)[:20]  # Limit to 20 keywords
        
        # Generate search terms from common phrases
        common_phrases = [
            "how to", "what is", "why does", "where can", "when should",
            "can't", "won't work", "not working", "error", "problem"
        ]
        
        content_lower = article.content.lower()
        for phrase in common_phrases:
            if phrase in content_lower:
                # Find sentences containing the phrase
                sentences = content_lower.split('.')
                for sentence in sentences:
                    if phrase in sentence:
                        # Extract the relevant part
                        start = sentence.find(phrase)
                        if start != -1:
                            relevant_part = sentence[start:start+50].strip()
                            if len(relevant_part) > 5:
                                article.search_terms.append(relevant_part)
    
    async def _build_vector_index(self):
        """Build FAISS vector index for semantic search"""
        if not self.knowledge_articles:
            return
        
        try:
            # Collect embeddings
            embeddings = []
            mappings = {}
            
            for i, (article_id, article) in enumerate(self.knowledge_articles.items()):
                if article.embedding is None:
                    # Generate embedding if not exists
                    article.embedding = self.embedding_model.encode(
                        f"{article.title} {article.content}",
                        convert_to_numpy=True
                    )
                
                embeddings.append(article.embedding)
                mappings[i] = article_id
            
            if not embeddings:
                return
            
            # Create FAISS index
            embeddings_matrix = np.vstack(embeddings).astype('float32')
            
            # Use IndexFlatIP for cosine similarity
            self.faiss_index = faiss.IndexFlatIP(embeddings_matrix.shape[1])
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings_matrix)
            
            # Add embeddings to index
            self.faiss_index.add(embeddings_matrix)
            
            # Store mappings
            self.article_mappings = mappings
            
            logger.info(f"Built FAISS index with {len(embeddings)} articles")
            
        except Exception as e:
            logger.error(f"Failed to build vector index: {str(e)}")
    
    async def _update_vector_index(self, article: KnowledgeArticle):
        """Update vector index with new article"""
        try:
            if self.faiss_index is None:
                await self._build_vector_index()
                return
            
            if article.embedding is None:
                return
            
            # Add to existing index
            embedding = article.embedding.reshape(1, -1).astype('float32')
            faiss.normalize_L2(embedding)
            
            new_idx = self.faiss_index.ntotal
            self.faiss_index.add(embedding)
            self.article_mappings[new_idx] = article.id
            
        except Exception as e:
            logger.error(f"Failed to update vector index: {str(e)}")
    
    async def _precompute_relationships(self):
        """Precompute article relationships"""
        for article_id, article in self.knowledge_articles.items():
            if not article.related_articles:
                # Find related articles based on category and tags
                related = []
                
                for other_id, other_article in self.knowledge_articles.items():
                    if other_id == article_id:
                        continue
                    
                    # Same category
                    if other_article.category == article.category:
                        related.append(other_id)
                    
                    # Shared tags
                    shared_tags = set(article.tags) & set(other_article.tags)
                    if len(shared_tags) >= 2:
                        related.append(other_id)
                
                article.related_articles = related[:5]  # Limit to 5 related articles
    
    async def _cache_article(self, article: KnowledgeArticle):
        """Cache article in Redis"""
        try:
            article_data = {
                "id": article.id,
                "title": article.title,
                "content": article.content,
                "category": article.category.value,
                "content_type": article.content_type.value,
                "tags": article.tags,
                "keywords": article.keywords,
                "author": article.author,
                "language": article.language,
                "status": article.status.value,
                "created_at": article.created_at.isoformat(),
                "updated_at": article.updated_at.isoformat(),
                "view_count": article.view_count,
                "usefulness_score": article.usefulness_score,
                "success_rate": article.success_rate,
                "search_terms": article.search_terms,
                "related_articles": article.related_articles
            }
            
            await self.redis_client.setex(
                f"knowledge_article:{article.id}",
                7200,  # 2 hours TTL
                json.dumps(article_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to cache article {article.id}: {str(e)}")
    
    async def _load_existing_articles(self):
        """Load existing articles from database or cache"""
        try:
            # Try to load from Redis cache first
            cached_articles = await self.redis_client.keys("knowledge_article:*")
            
            for key in cached_articles:
                data = await self.redis_client.get(key)
                if data:
                    article_data = json.loads(data)
                    
                    article = KnowledgeArticle(
                        id=article_data["id"],
                        title=article_data["title"],
                        content=article_data["content"],
                        category=KnowledgeCategory(article_data["category"]),
                        content_type=ContentType(article_data["content_type"]),
                        tags=article_data.get("tags", []),
                        keywords=article_data.get("keywords", []),
                        author=article_data.get("author", "AI Support System"),
                        language=article_data.get("language", "en"),
                        status=ContentStatus(article_data.get("status", "published")),
                        created_at=datetime.fromisoformat(article_data["created_at"]),
                        updated_at=datetime.fromisoformat(article_data["updated_at"]),
                        view_count=article_data.get("view_count", 0),
                        usefulness_score=article_data.get("usefulness_score", 0.0),
                        success_rate=article_data.get("success_rate", 0.0),
                        search_terms=article_data.get("search_terms", []),
                        related_articles=article_data.get("related_articles", [])
                    )
                    
                    self.knowledge_articles[article.id] = article
            
            logger.info(f"Loaded {len(self.knowledge_articles)} existing articles")
            
        except Exception as e:
            logger.error(f"Failed to load existing articles: {str(e)}")
    
    async def _update_search_stats(self, query: SearchQuery, result_count: int, search_time: float):
        """Update search statistics"""
        try:
            stats_key = f"search_stats:{datetime.now().strftime('%Y-%m-%d')}"
            
            stats = {
                "query": query.query,
                "user_id": query.user_id,
                "result_count": result_count,
                "search_time": search_time,
                "timestamp": query.timestamp.isoformat()
            }
            
            await self.redis_client.lpush(stats_key, json.dumps(stats))
            await self.redis_client.expire(stats_key, 86400 * 30)  # Keep for 30 days
            
            # Update global counters
            self.usage_stats["total_searches"] += 1
            self.usage_stats["total_search_time"] += search_time
            
        except Exception as e:
            logger.error(f"Failed to update search stats: {str(e)}")
    
    async def get_article_by_id(self, article_id: str) -> Optional[KnowledgeArticle]:
        """Get article by ID"""
        if article_id in self.knowledge_articles:
            article = self.knowledge_articles[article_id]
            article.view_count += 1
            await self._cache_article(article)  # Update cache
            return article
        
        return None
    
    async def update_article_feedback(
        self,
        article_id: str,
        helpful: bool,
        user_feedback: Optional[str] = None
    ):
        """Update article feedback and usefulness score"""
        if article_id not in self.knowledge_articles:
            return
        
        article = self.knowledge_articles[article_id]
        article.feedback_count += 1
        
        # Update usefulness score
        if helpful:
            article.usefulness_score = (
                (article.usefulness_score * (article.feedback_count - 1) + 1) / article.feedback_count
            )
        else:
            article.usefulness_score = (
                (article.usefulness_score * (article.feedback_count - 1) + 0) / article.feedback_count
            )
        
        article.updated_at = datetime.now(timezone.utc)
        await self._cache_article(article)
        
        logger.info(f"Updated feedback for article {article_id}: helpful={helpful}")
    
    async def get_knowledge_analytics(self) -> Dict[str, Any]:
        """Get knowledge base analytics"""
        return {
            "total_articles": len(self.knowledge_articles),
            "categories": {
                category.value: len([a for a in self.knowledge_articles.values() if a.category == category])
                for category in KnowledgeCategory
            },
            "content_types": {
                content_type.value: len([a for a in self.knowledge_articles.values() if a.content_type == content_type])
                for content_type in ContentType
            },
            "average_usefulness": sum(a.usefulness_score for a in self.knowledge_articles.values()) / len(self.knowledge_articles) if self.knowledge_articles else 0,
            "total_views": sum(a.view_count for a in self.knowledge_articles.values()),
            "usage_stats": dict(self.usage_stats)
        }
