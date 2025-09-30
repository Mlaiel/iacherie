"""
Internal Linking Engine for Ainflue Platform
Advanced internal linking strategy and automation for SEO optimization

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Tuple, Set, Union
import re
from dataclasses import dataclass, field
from datetime import datetime
import json
from collections import defaultdict, Counter
from urllib.parse import urljoin, urlparse
import math


@dataclass
class InternalLink:
    """Internal link representation"""
    source_url: str
    target_url: str
    anchor_text: str
    link_type: str  # 'contextual', 'navigational', 'related', 'hub'
    relevance_score: float
    position: int  # Position in content (0-100%)
    is_dofollow: bool = True
    created_date: datetime = field(default_factory=datetime.now)


@dataclass
class ContentNode:
    """Content node for link graph analysis"""
    url: str
    title: str
    content_type: str
    topics: List[str]
    keywords: List[str]
    creator_id: Optional[str] = None
    page_authority: float = 0.0
    internal_links_in: int = 0
    internal_links_out: int = 0


@dataclass
class LinkRecommendation:
    """Link recommendation with context"""
    source_url: str
    target_url: str
    recommended_anchor: str
    relevance_score: float
    link_type: str
    position_suggestion: str
    reasoning: str


class InternalLinkingEngine:
    """
    Advanced internal linking engine for SEO optimization
    Provides intelligent link suggestions and link graph analysis
    """
    
    def __init__(self, base_domain: str):
        self.base_domain = base_domain.rstrip('/')
        self.content_nodes: Dict[str, ContentNode] = {}
        self.link_graph: Dict[str, List[InternalLink]] = defaultdict(list)
        self.topic_clusters: Dict[str, List[str]] = defaultdict(list)
        self.creator_hubs: Dict[str, str] = {}
        
    def add_content_node(self, url: str, title: str, content_type: str,
                        topics: List[str], keywords: List[str],
                        creator_id: str = None) -> ContentNode:
        """Add content node to the link graph"""
        
        node = ContentNode(
            url=url,
            title=title,
            content_type=content_type,
            topics=topics,
            keywords=keywords,
            creator_id=creator_id
        )
        
        self.content_nodes[url] = node
        
        # Update topic clusters
        for topic in topics:
            self.topic_clusters[topic].append(url)
            
        return node
        
    def add_internal_link(self, source_url: str, target_url: str, anchor_text: str,
                         link_type: str = 'contextual', relevance_score: float = 0.5,
                         position: int = 50) -> InternalLink:
        """Add internal link to the graph"""
        
        link = InternalLink(
            source_url=source_url,
            target_url=target_url,
            anchor_text=anchor_text,
            link_type=link_type,
            relevance_score=relevance_score,
            position=position
        )
        
        self.link_graph[source_url].append(link)
        
        # Update node statistics
        if source_url in self.content_nodes:
            self.content_nodes[source_url].internal_links_out += 1
        if target_url in self.content_nodes:
            self.content_nodes[target_url].internal_links_in += 1
            
        return link
        
    def calculate_content_similarity(self, url1: str, url2: str) -> float:
        """Calculate semantic similarity between two content pieces"""
        
        if url1 not in self.content_nodes or url2 not in self.content_nodes:
            return 0.0
            
        node1 = self.content_nodes[url1]
        node2 = self.content_nodes[url2]
        
        # Topic similarity
        topics1 = set(node1.topics)
        topics2 = set(node2.topics)
        topic_similarity = len(topics1 & topics2) / max(len(topics1 | topics2), 1)
        
        # Keyword similarity
        keywords1 = set(node1.keywords)
        keywords2 = set(node2.keywords)
        keyword_similarity = len(keywords1 & keywords2) / max(len(keywords1 | keywords2), 1)
        
        # Content type compatibility
        type_compatibility = self._get_content_type_compatibility(node1.content_type, node2.content_type)
        
        # Creator relationship
        creator_bonus = 0.2 if node1.creator_id and node1.creator_id == node2.creator_id else 0
        
        # Combined similarity score
        similarity = (
            topic_similarity * 0.4 +
            keyword_similarity * 0.3 +
            type_compatibility * 0.2 +
            creator_bonus * 0.1
        )
        
        return min(1.0, similarity)
        
    def _get_content_type_compatibility(self, type1: str, type2: str) -> float:
        """Get compatibility score between content types"""
        
        compatibility_matrix = {
            ('blog', 'blog'): 1.0,
            ('blog', 'tutorial'): 0.8,
            ('blog', 'video'): 0.6,
            ('blog', 'audio'): 0.4,
            ('tutorial', 'tutorial'): 1.0,
            ('tutorial', 'video'): 0.9,
            ('tutorial', 'blog'): 0.8,
            ('video', 'video'): 1.0,
            ('video', 'tutorial'): 0.9,
            ('video', 'audio'): 0.7,
            ('audio', 'audio'): 1.0,
            ('audio', 'video'): 0.7,
            ('portfolio', 'portfolio'): 1.0,
            ('portfolio', 'blog'): 0.5,
        }
        
        # Check both directions
        key1 = (type1, type2)
        key2 = (type2, type1)
        
        return compatibility_matrix.get(key1, compatibility_matrix.get(key2, 0.3))
        
    def generate_link_recommendations(self, source_url: str, 
                                    max_recommendations: int = 5,
                                    min_relevance: float = 0.3) -> List[LinkRecommendation]:
        """Generate intelligent link recommendations for a source page"""
        
        if source_url not in self.content_nodes:
            return []
            
        source_node = self.content_nodes[source_url]
        recommendations = []
        
        # Get existing outbound links to avoid duplicates
        existing_targets = {link.target_url for link in self.link_graph.get(source_url, [])}
        
        # Find potential target pages
        for target_url, target_node in self.content_nodes.items():
            if target_url == source_url or target_url in existing_targets:
                continue
                
            # Calculate relevance
            relevance = self.calculate_content_similarity(source_url, target_url)
            
            if relevance >= min_relevance:
                # Generate anchor text
                anchor_text = self._generate_anchor_text(source_node, target_node)
                
                # Determine link type
                link_type = self._determine_link_type(source_node, target_node, relevance)
                
                # Position suggestion
                position_suggestion = self._suggest_link_position(source_node, target_node, link_type)
                
                # Reasoning
                reasoning = self._generate_link_reasoning(source_node, target_node, relevance)
                
                recommendation = LinkRecommendation(
                    source_url=source_url,
                    target_url=target_url,
                    recommended_anchor=anchor_text,
                    relevance_score=relevance,
                    link_type=link_type,
                    position_suggestion=position_suggestion,
                    reasoning=reasoning
                )
                
                recommendations.append(recommendation)
                
        # Sort by relevance and return top recommendations
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        return recommendations[:max_recommendations]
        
    def _generate_anchor_text(self, source_node: ContentNode, target_node: ContentNode) -> str:
        """Generate appropriate anchor text for internal link"""
        
        # Use title if it's concise
        title_words = target_node.title.split()
        if len(title_words) <= 5:
            return target_node.title
            
        # Use shared keywords
        shared_keywords = set(source_node.keywords) & set(target_node.keywords)
        if shared_keywords:
            # Pick the most specific shared keyword
            keyword = min(shared_keywords, key=len)
            return keyword.title()
            
        # Use content type + main topic
        if target_node.topics:
            main_topic = target_node.topics[0]
            return f"{target_node.content_type.title()} about {main_topic}"
            
        # Fallback to shortened title
        return ' '.join(title_words[:4]) + ('...' if len(title_words) > 4 else '')
        
    def _determine_link_type(self, source_node: ContentNode, target_node: ContentNode, 
                           relevance: float) -> str:
        """Determine the type of internal link"""
        
        # Hub pages (portfolio, main creator pages)
        if target_node.content_type in ['portfolio', 'profile', 'hub']:
            return 'hub'
            
        # Navigation links
        if target_node.content_type in ['category', 'index', 'home']:
            return 'navigational'
            
        # High relevance contextual links
        if relevance > 0.7:
            return 'contextual'
            
        # Related content
        return 'related'
        
    def _suggest_link_position(self, source_node: ContentNode, target_node: ContentNode, 
                             link_type: str) -> str:
        """Suggest where to place the link in content"""
        
        position_suggestions = {
            'contextual': 'Within the main content where naturally relevant',
            'hub': 'At the beginning or end of article as author bio/portfolio link',
            'navigational': 'In navigation menu or breadcrumbs',
            'related': 'In "Related Articles" or "See Also" section at the end'
        }
        
        return position_suggestions.get(link_type, 'Within relevant content section')
        
    def _generate_link_reasoning(self, source_node: ContentNode, target_node: ContentNode, 
                               relevance: float) -> str:
        """Generate reasoning for the link recommendation"""
        
        reasons = []
        
        # Topic overlap
        shared_topics = set(source_node.topics) & set(target_node.topics)
        if shared_topics:
            reasons.append(f"Shares topics: {', '.join(list(shared_topics)[:3])}")
            
        # Keyword overlap
        shared_keywords = set(source_node.keywords) & set(target_node.keywords)
        if shared_keywords:
            reasons.append(f"Common keywords: {', '.join(list(shared_keywords)[:3])}")
            
        # Creator relationship
        if source_node.creator_id and source_node.creator_id == target_node.creator_id:
            reasons.append("Same creator - builds author authority")
            
        # Content type relationship
        if source_node.content_type == target_node.content_type:
            reasons.append(f"Same content type ({source_node.content_type})")
            
        # High relevance
        if relevance > 0.8:
            reasons.append("High semantic relevance")
            
        return "; ".join(reasons) if reasons else "General topical relevance"
        
    def create_topic_hub_strategy(self, topic: str) -> Dict[str, List[str]]:
        """Create a hub and spoke linking strategy for a topic"""
        
        if topic not in self.topic_clusters:
            return {}
            
        topic_pages = self.topic_clusters[topic]
        
        # Find the best hub page (highest authority or most comprehensive)
        hub_candidates = []
        for url in topic_pages:
            if url in self.content_nodes:
                node = self.content_nodes[url]
                # Score based on content type, incoming links, and keyword coverage
                hub_score = (
                    (1.0 if node.content_type in ['hub', 'guide', 'comprehensive'] else 0.5) +
                    (node.internal_links_in * 0.1) +
                    (len(node.keywords) * 0.05)
                )
                hub_candidates.append((url, hub_score))
                
        if not hub_candidates:
            return {}
            
        # Select hub page
        hub_url = max(hub_candidates, key=lambda x: x[1])[0]
        spoke_pages = [url for url in topic_pages if url != hub_url]
        
        return {
            'hub': hub_url,
            'spokes': spoke_pages,
            'strategy': {
                'hub_to_spokes': f"Link from hub to all {len(spoke_pages)} spoke pages",
                'spokes_to_hub': f"Link from all spoke pages back to hub",
                'spoke_to_spoke': "Minimal cross-linking between spokes"
            }
        }
        
    def analyze_link_distribution(self) -> Dict[str, Union[int, float, List[str]]]:
        """Analyze internal link distribution and identify issues"""
        
        analysis = {
            'total_pages': len(self.content_nodes),
            'total_links': sum(len(links) for links in self.link_graph.values()),
            'orphan_pages': [],
            'over_linked_pages': [],
            'under_linked_pages': [],
            'avg_links_per_page': 0.0,
            'link_equity_issues': []
        }
        
        if analysis['total_pages'] == 0:
            return analysis
            
        analysis['avg_links_per_page'] = analysis['total_links'] / analysis['total_pages']
        
        for url, node in self.content_nodes.items():
            # Orphan pages (no incoming links)
            if node.internal_links_in == 0:
                analysis['orphan_pages'].append(url)
                
            # Over-linked pages (too many outgoing links)
            if node.internal_links_out > 10:
                analysis['over_linked_pages'].append(url)
                
            # Under-linked important pages
            if (node.content_type in ['guide', 'hub', 'comprehensive'] and 
                node.internal_links_in < 3):
                analysis['under_linked_pages'].append(url)
                
        return analysis
        
    def generate_automated_linking_plan(self, content_url: str, content_text: str) -> List[Dict]:
        """Generate automated internal linking plan for new content"""
        
        if content_url not in self.content_nodes:
            return []
            
        # Extract potential anchor texts from content
        potential_anchors = self._extract_potential_anchors(content_text)
        
        # Find matching content for each potential anchor
        linking_plan = []
        
        for anchor_text, position in potential_anchors:
            # Find best matching target page
            best_matches = self._find_anchor_matches(anchor_text, content_url)
            
            if best_matches:
                target_url, match_score = best_matches[0]
                
                plan_item = {
                    'anchor_text': anchor_text,
                    'target_url': target_url,
                    'position': position,
                    'match_score': match_score,
                    'link_type': 'contextual',
                    'recommendation': f"Link '{anchor_text}' to {target_url}"
                }
                
                linking_plan.append(plan_item)
                
        return linking_plan
        
    def _extract_potential_anchors(self, content_text: str) -> List[Tuple[str, int]]:
        """Extract potential anchor texts from content"""
        
        anchors = []
        
        # Look for phrases that match existing page titles or keywords
        sentences = re.split(r'[.!?]+', content_text)
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Extract noun phrases (simplified)
            words = sentence.split()
            for j in range(len(words)):
                for k in range(j + 1, min(j + 6, len(words) + 1)):  # 1-5 word phrases
                    phrase = ' '.join(words[j:k])
                    
                    # Clean phrase
                    phrase = re.sub(r'^[^a-zA-Z]+|[^a-zA-Z]+$', '', phrase)
                    
                    if (len(phrase) > 3 and 
                        len(phrase.split()) <= 4 and
                        not phrase.lower() in ['this', 'that', 'these', 'those']):
                        
                        position = int((i / len(sentences)) * 100)
                        anchors.append((phrase, position))
                        
        return anchors
        
    def _find_anchor_matches(self, anchor_text: str, source_url: str) -> List[Tuple[str, float]]:
        """Find pages that match the anchor text"""
        
        matches = []
        anchor_lower = anchor_text.lower()
        
        for url, node in self.content_nodes.items():
            if url == source_url:
                continue
                
            match_score = 0.0
            
            # Title match
            if anchor_lower in node.title.lower():
                match_score += 0.8
                
            # Keyword match
            for keyword in node.keywords:
                if keyword.lower() in anchor_lower or anchor_lower in keyword.lower():
                    match_score += 0.3
                    
            # Topic match
            for topic in node.topics:
                if topic.lower() in anchor_lower or anchor_lower in topic.lower():
                    match_score += 0.2
                    
            if match_score > 0.3:
                matches.append((url, match_score))
                
        # Sort by match score
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:3]  # Top 3 matches
        
    def optimize_existing_links(self) -> List[Dict[str, str]]:
        """Analyze and optimize existing internal links"""
        
        optimizations = []
        
        for source_url, links in self.link_graph.items():
            for link in links:
                # Check for optimization opportunities
                
                # Generic anchor text
                if link.anchor_text.lower() in ['click here', 'read more', 'here', 'this']:
                    optimizations.append({
                        'type': 'anchor_optimization',
                        'source': source_url,
                        'target': link.target_url,
                        'current_anchor': link.anchor_text,
                        'suggested_anchor': self._generate_anchor_text(
                            self.content_nodes.get(source_url),
                            self.content_nodes.get(link.target_url)
                        ),
                        'reason': 'Generic anchor text should be more descriptive'
                    })
                    
                # Over-optimization (exact match anchor)
                if (link.target_url in self.content_nodes and
                    link.anchor_text.lower() == self.content_nodes[link.target_url].title.lower()):
                    optimizations.append({
                        'type': 'anchor_variation',
                        'source': source_url,
                        'target': link.target_url,
                        'current_anchor': link.anchor_text,
                        'reason': 'Consider varying anchor text to avoid over-optimization'
                    })
                    
                # Low relevance links
                if link.relevance_score < 0.3:
                    optimizations.append({
                        'type': 'relevance_review',
                        'source': source_url,
                        'target': link.target_url,
                        'relevance_score': link.relevance_score,
                        'reason': 'Low relevance link may not provide value'
                    })
                    
        return optimizations
        
    def generate_creator_linking_strategy(self, creator_id: str) -> Dict:
        """Generate linking strategy for a specific creator"""
        
        creator_pages = [url for url, node in self.content_nodes.items() 
                        if node.creator_id == creator_id]
        
        if not creator_pages:
            return {}
            
        # Find creator hub page
        hub_page = None
        for url in creator_pages:
            node = self.content_nodes[url]
            if node.content_type in ['profile', 'portfolio', 'hub']:
                hub_page = url
                break
                
        strategy = {
            'creator_id': creator_id,
            'total_pages': len(creator_pages),
            'hub_page': hub_page,
            'content_pages': [url for url in creator_pages if url != hub_page],
            'recommendations': []
        }
        
        if hub_page:
            # Hub linking strategy
            strategy['recommendations'].extend([
                f"Link all creator content back to hub page: {hub_page}",
                f"Link from hub page to latest/featured content",
                "Use consistent creator branding in anchor texts"
            ])
            
        # Topical clustering for creator
        creator_topics = defaultdict(list)
        for url in creator_pages:
            node = self.content_nodes[url]
            for topic in node.topics:
                creator_topics[topic].append(url)
                
        # Topic-based linking recommendations
        for topic, pages in creator_topics.items():
            if len(pages) > 2:
                strategy['recommendations'].append(
                    f"Create topic cluster for '{topic}' with {len(pages)} pages"
                )
                
        return strategy


# Integration utilities
def create_ainflue_internal_linking_engine(base_domain: str = "https://ainflue.com") -> InternalLinkingEngine:
    """Create configured internal linking engine for Ainflue"""
    
    engine = InternalLinkingEngine(base_domain)
    
    # Could be extended with platform-specific configurations
    
    return engine


if __name__ == "__main__":
    # Example usage
    engine = create_ainflue_internal_linking_engine()
    
    # Add sample content nodes
    engine.add_content_node(
        url="/blog/ai-music-creation",
        title="How to Create Music with AI",
        content_type="blog",
        topics=["AI", "music", "technology"],
        keywords=["AI music", "artificial intelligence", "music creation"],
        creator_id="creator_001"
    )
    
    engine.add_content_node(
        url="/tutorial/music-production-basics",
        title="Music Production Basics",
        content_type="tutorial", 
        topics=["music", "production", "beginner"],
        keywords=["music production", "DAW", "recording"],
        creator_id="creator_001"
    )
    
    engine.add_content_node(
        url="/creator/creator_001/profile",
        title="John Doe - Music Producer",
        content_type="profile",
        topics=["profile", "music", "producer"],
        keywords=["music producer", "creator", "portfolio"],
        creator_id="creator_001"
    )
    
    # Generate recommendations
    recommendations = engine.generate_link_recommendations("/blog/ai-music-creation")
    
    print("Link Recommendations:")
    for rec in recommendations:
        print(f"  {rec.target_url}")
        print(f"    Anchor: {rec.recommended_anchor}")
        print(f"    Relevance: {rec.relevance_score:.2f}")
        print(f"    Type: {rec.link_type}")
        print(f"    Reasoning: {rec.reasoning}")
        print()
        
    # Analyze creator strategy
    creator_strategy = engine.generate_creator_linking_strategy("creator_001")
    print("Creator Linking Strategy:")
    print(json.dumps(creator_strategy, indent=2))