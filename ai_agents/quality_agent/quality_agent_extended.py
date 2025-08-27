"""
Quality Agent Extended Methods - Advanced Analysis Implementations

Extended methods for the Quality Agent to provide comprehensive quality analysis.
This module contains specialized analysis methods for various content types.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
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
import numpy as np
import cv2
import spacy
from textstat import flesch_kincaid_grade, gunning_fog, automated_readability_index
import re
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

class QualityAnalysisExtensions:
    """Extended analysis methods for comprehensive quality assessment"""
    
    def __init__(self):
        # Load NLP model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.nlp = None
            logger.warning("Spacy model not found, some text analysis features will be limited")
            
    async def _analyze_focus_quality(self, image: np.ndarray) -> float:
        """Analyze focus quality and depth of field"""
        try:
            # Calculate Laplacian variance for overall sharpness
            laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
            
            # Edge detection for detail analysis
            edges = cv2.Canny(image, 50, 150)
            edge_density = np.sum(edges) / (image.shape[0] * image.shape[1])
            
            # Texture analysis using LBP-like approach
            texture_score = self._calculate_texture_score(image)
            
            # Combine metrics
            focus_score = (
                min(1.0, laplacian_var / 500) * 0.5 +  # Sharpness
                min(1.0, edge_density * 1000) * 0.3 +  # Edge density  
                texture_score * 0.2  # Texture richness
            )
            
            return focus_score
            
        except Exception:
            return 0.5

    def _calculate_texture_score(self, image: np.ndarray) -> float:
        """Calculate texture richness score"""
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
                
            # Calculate local standard deviation
            kernel = np.ones((9, 9), np.float32) / 81
            mean = cv2.filter2D(gray.astype(np.float32), -1, kernel)
            sq_mean = cv2.filter2D((gray.astype(np.float32))**2, -1, kernel)
            
            texture_map = np.sqrt(sq_mean - mean**2)
            texture_score = np.mean(texture_map) / 255.0
            
            return min(1.0, texture_score * 4)  # Normalize
            
        except Exception:
            return 0.5

    async def _analyze_subject_prominence(self, image: np.ndarray) -> float:
        """Analyze subject prominence and foreground/background separation"""
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
                
            height, width = gray.shape
            
            # Calculate saliency map (simplified)
            saliency_map = self._calculate_saliency(gray)
            
            # Analyze center weighting (subjects often in center)
            center_mask = np.zeros((height, width), dtype=np.uint8)
            center_h, center_w = height // 2, width // 2
            cv2.circle(center_mask, (center_w, center_h), min(height, width) // 4, 255, -1)
            
            center_saliency = np.mean(saliency_map[center_mask > 0])
            edge_saliency = np.mean(saliency_map[center_mask == 0])
            
            # Subject prominence score
            if edge_saliency > 0:
                prominence_ratio = center_saliency / edge_saliency
                prominence_score = min(1.0, prominence_ratio / 2.0)
            else:
                prominence_score = 1.0
                
            return prominence_score
            
        except Exception:
            return 0.6

    def _calculate_saliency(self, image: np.ndarray) -> np.ndarray:
        """Calculate basic saliency map"""
        try:
            # Spectral residual method (simplified)
            img_float = image.astype(np.float32)
            
            # FFT
            fft = np.fft.fft2(img_float)
            log_amplitude = np.log(np.abs(fft) + 1)
            phase = np.angle(fft)
            
            # Spectral residual
            spectral_residual = log_amplitude - cv2.boxFilter(log_amplitude, -1, (3, 3))
            
            # Inverse FFT
            saliency = np.abs(np.fft.ifft2(np.exp(spectral_residual + 1j * phase)))
            
            # Gaussian blur and normalize
            saliency = cv2.GaussianBlur(saliency, (11, 11), 0)
            saliency = (saliency - saliency.min()) / (saliency.max() - saliency.min())
            
            return saliency
            
        except Exception:
            return np.ones(image.shape, dtype=np.float32) * 0.5

    async def _analyze_golden_ratio(self, image: np.ndarray) -> float:
        """Analyze golden ratio spiral composition"""
        try:
            height, width = image.shape
            
            # Golden ratio ≈ 1.618
            golden_ratio = 1.618
            
            # Calculate golden ratio points
            golden_h = int(height / golden_ratio)
            golden_w = int(width / golden_ratio)
            
            # Check for features at golden ratio positions
            edges = cv2.Canny(image, 50, 150)
            
            # Sample points along golden spiral (simplified)
            golden_points = [
                (golden_h, golden_w),
                (height - golden_h, golden_w),
                (golden_h, width - golden_w),
                (height - golden_h, width - golden_w)
            ]
            
            score = 0
            for h, w in golden_points:
                if 0 <= h < height and 0 <= w < width:
                    # Check area around golden point
                    roi = edges[max(0, h-15):min(height, h+15),
                               max(0, w-15):min(width, w+15)]
                    if roi.size > 0 and np.sum(roi) > 0:
                        score += 1
                        
            return score / len(golden_points)
            
        except Exception:
            return 0.4

    async def _analyze_negative_space(self, image: np.ndarray) -> float:
        """Analyze negative space utilization"""
        try:
            # Threshold image to find negative space
            _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Calculate ratio of negative to positive space
            total_pixels = image.shape[0] * image.shape[1]
            negative_pixels = np.sum(binary == 0)
            positive_pixels = total_pixels - negative_pixels
            
            if positive_pixels > 0:
                space_ratio = negative_pixels / positive_pixels
                # Optimal ratio is around 0.3-0.7 (30-70% negative space)
                if 0.3 <= space_ratio <= 0.7:
                    space_score = 1.0
                elif 0.2 <= space_ratio < 0.3 or 0.7 < space_ratio <= 0.8:
                    space_score = 0.8
                else:
                    space_score = 0.5
                    
                return space_score
            else:
                return 0.0
                
        except Exception:
            return 0.6

    async def _analyze_keyword_density(self, text_content: str) -> float:
        """Analyze keyword density and distribution"""
        try:
            words = text_content.lower().split()
            word_count = len(words)
            
            if word_count == 0:
                return 0.0
                
            # Count word frequencies
            word_freq = Counter(words)
            
            # Remove common stop words
            stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                         'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been',
                         'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                         'could', 'should', 'may', 'might', 'can', 'shall', 'must',
                         'a', 'an', 'this', 'that', 'these', 'those', 'i', 'you',
                         'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
            
            filtered_freq = {word: freq for word, freq in word_freq.items() 
                           if word not in stop_words and len(word) > 2}
            
            if not filtered_freq:
                return 0.5
                
            # Calculate density scores
            max_freq = max(filtered_freq.values())
            density_scores = []
            
            for word, freq in filtered_freq.items():
                density = freq / word_count
                # Optimal keyword density: 0.5-3%
                if 0.005 <= density <= 0.03:
                    density_scores.append(1.0)
                elif 0.002 <= density < 0.005 or 0.03 < density <= 0.05:
                    density_scores.append(0.8)
                else:
                    density_scores.append(0.3)
                    
            return np.mean(density_scores) if density_scores else 0.5
            
        except Exception:
            return 0.5

    async def _analyze_heading_structure(self, text_content: str) -> float:
        """Analyze heading structure and hierarchy"""
        try:
            # Look for markdown-style headings and HTML headings
            lines = text_content.split('\n')
            
            h1_count = 0
            h2_count = 0
            h3_count = 0
            h4_count = 0
            
            for line in lines:
                line = line.strip()
                if line.startswith('# '):
                    h1_count += 1
                elif line.startswith('## '):
                    h2_count += 1
                elif line.startswith('### '):
                    h3_count += 1
                elif line.startswith('#### '):
                    h4_count += 1
                # Also check for HTML headings
                elif re.search(r'<h[1-6].*?>', line, re.IGNORECASE):
                    if re.search(r'<h1.*?>', line, re.IGNORECASE):
                        h1_count += 1
                    elif re.search(r'<h2.*?>', line, re.IGNORECASE):
                        h2_count += 1
                    elif re.search(r'<h3.*?>', line, re.IGNORECASE):
                        h3_count += 1
                    elif re.search(r'<h[4-6].*?>', line, re.IGNORECASE):
                        h4_count += 1
                        
            # Analyze structure quality
            structure_score = 0.0
            
            # Should have one main H1
            if h1_count == 1:
                structure_score += 0.4
            elif h1_count > 1:
                structure_score += 0.2
                
            # Should have some H2s for sections
            if 1 <= h2_count <= 8:
                structure_score += 0.3
            elif h2_count > 8:
                structure_score += 0.2
                
            # H3s are good for subsections
            if h3_count > 0:
                structure_score += 0.2
                
            # Bonus for hierarchical structure
            if h1_count >= 1 and h2_count >= h1_count and h3_count >= 0:
                structure_score += 0.1
                
            return min(1.0, structure_score)
            
        except Exception:
            return 0.4

    async def _analyze_link_structure(self, text_content: str) -> float:
        """Analyze internal and external links"""
        try:
            # Find markdown and HTML links
            markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text_content)
            html_links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>', 
                                   text_content, re.IGNORECASE)
            
            total_links = len(markdown_links) + len(html_links)
            word_count = len(text_content.split())
            
            if word_count == 0:
                return 0.0
                
            # Analyze link density (links per 100 words)
            link_density = (total_links / word_count) * 100
            
            # Optimal link density: 1-3 links per 100 words
            if 1 <= link_density <= 3:
                density_score = 1.0
            elif 0.5 <= link_density < 1 or 3 < link_density <= 5:
                density_score = 0.8
            elif link_density > 5:
                density_score = 0.3  # Too many links
            else:
                density_score = 0.6  # No links
                
            # Analyze link types
            external_links = 0
            internal_links = 0
            
            all_links = [link[1] for link in markdown_links] + [link[0] for link in html_links]
            
            for link in all_links:
                if link.startswith(('http://', 'https://', 'www.')):
                    external_links += 1
                elif link.startswith(('#', '/')):
                    internal_links += 1
                    
            # Balance between internal and external links
            if total_links > 0:
                balance_ratio = min(internal_links, external_links) / total_links
                balance_score = balance_ratio * 2  # Max score when balanced
            else:
                balance_score = 0.5
                
            return (density_score + balance_score) / 2
            
        except Exception:
            return 0.5

    async def _analyze_meta_description_potential(self, text_content: str) -> float:
        """Analyze first paragraph as potential meta description"""
        try:
            # Get first paragraph
            paragraphs = [p.strip() for p in text_content.split('\n\n') if p.strip()]
            
            if not paragraphs:
                return 0.0
                
            first_paragraph = paragraphs[0]
            char_count = len(first_paragraph)
            
            # Optimal meta description: 150-160 characters
            if 140 <= char_count <= 160:
                length_score = 1.0
            elif 120 <= char_count < 140 or 160 < char_count <= 180:
                length_score = 0.8
            elif 100 <= char_count < 120 or 180 < char_count <= 200:
                length_score = 0.6
            else:
                length_score = 0.3
                
            # Check for call-to-action words
            cta_words = ['discover', 'learn', 'find', 'get', 'see', 'explore',
                        'read', 'watch', 'download', 'try', 'start', 'join']
            
            first_para_lower = first_paragraph.lower()
            cta_score = 0.0
            
            for word in cta_words:
                if word in first_para_lower:
                    cta_score += 0.1
                    
            cta_score = min(1.0, cta_score)
            
            return (length_score + cta_score) / 2
            
        except Exception:
            return 0.5

    async def _calculate_seo_readability(self, text_content: str) -> float:
        """Calculate SEO-optimized readability score"""
        try:
            # Multiple readability metrics
            fk_grade = flesch_kincaid_grade(text_content)
            gunning_fog_score = gunning_fog(text_content)
            ari_score = automated_readability_index(text_content)
            
            # SEO optimal reading level: 8th-9th grade
            fk_score = max(0, 1.0 - abs(fk_grade - 8.5) / 10)
            gunning_score = max(0, 1.0 - abs(gunning_fog_score - 8.5) / 10)
            ari_score_norm = max(0, 1.0 - abs(ari_score - 8.5) / 10)
            
            return (fk_score + gunning_score + ari_score_norm) / 3
            
        except Exception:
            return 0.6

    async def _analyze_semantic_richness(self, text_content: str) -> float:
        """Analyze semantic richness and vocabulary diversity"""
        try:
            if not self.nlp:
                return 0.6  # Default score if NLP not available
                
            doc = self.nlp(text_content)
            
            # Count unique lemmas (root forms)
            unique_lemmas = set()
            total_words = 0
            
            for token in doc:
                if not token.is_stop and not token.is_punct and token.is_alpha:
                    unique_lemmas.add(token.lemma_.lower())
                    total_words += 1
                    
            if total_words == 0:
                return 0.0
                
            # Lexical diversity (Type-Token Ratio)
            ttr = len(unique_lemmas) / total_words
            
            # Named entity recognition
            named_entities = len(doc.ents)
            entity_density = named_entities / max(total_words / 100, 1)  # Entities per 100 words
            
            # Part-of-speech diversity
            pos_tags = [token.pos_ for token in doc if not token.is_stop and not token.is_punct]
            unique_pos = len(set(pos_tags))
            pos_diversity = min(1.0, unique_pos / 10)  # Normalize
            
            # Combine metrics
            semantic_score = (
                min(1.0, ttr * 3) * 0.5 +  # TTR (capped at reasonable level)
                min(1.0, entity_density / 2) * 0.3 +  # Entity richness
                pos_diversity * 0.2  # POS diversity
            )
            
            return semantic_score
            
        except Exception:
            return 0.6

    async def _analyze_content_freshness(self, text_content: str) -> float:
        """Analyze content freshness indicators"""
        try:
            # Look for temporal indicators
            current_year = datetime.now().year
            fresh_indicators = [
                str(current_year),
                str(current_year - 1),
                'latest',
                'recent',
                'new',
                'updated',
                'current',
                'modern',
                'today',
                'now'
            ]
            
            text_lower = text_content.lower()
            freshness_score = 0.0
            
            for indicator in fresh_indicators:
                if indicator in text_lower:
                    freshness_score += 0.1
                    
            # Look for specific date patterns
            date_patterns = [
                r'\b20\d{2}\b',  # Years 2000-2099
                r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+20\d{2}\b',
                r'\b\d{1,2}[-/]\d{1,2}[-/]20\d{2}\b'
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    freshness_score += 0.2
                    break  # Only count once
                    
            return min(1.0, freshness_score)
            
        except Exception:
            return 0.5

    async def _analyze_schema_potential(self, text_content: str) -> float:
        """Analyze potential for structured data/schema markup"""
        try:
            schema_indicators = 0
            text_lower = text_content.lower()
            
            # Article schema indicators
            article_terms = ['article', 'blog', 'post', 'story', 'news']
            if any(term in text_lower for term in article_terms):
                schema_indicators += 1
                
            # Review schema indicators
            review_terms = ['review', 'rating', 'stars', 'recommend', 'opinion']
            if any(term in text_lower for term in review_terms):
                schema_indicators += 1
                
            # FAQ schema indicators
            faq_terms = ['question', 'answer', 'faq', 'q:', 'a:', 'how to', 'what is', 'why']
            if any(term in text_lower for term in faq_terms):
                schema_indicators += 1
                
            # Recipe schema indicators
            recipe_terms = ['recipe', 'ingredients', 'instructions', 'cooking', 'baking']
            if any(term in text_lower for term in recipe_terms):
                schema_indicators += 1
                
            # Product schema indicators
            product_terms = ['product', 'price', 'buy', 'purchase', 'specifications']
            if any(term in text_lower for term in product_terms):
                schema_indicators += 1
                
            # Event schema indicators
            event_terms = ['event', 'date', 'location', 'venue', 'ticket']
            if any(term in text_lower for term in event_terms):
                schema_indicators += 1
                
            return min(1.0, schema_indicators / 6)
            
        except Exception:
            return 0.3

    async def _analyze_transition_words(self, text_content: str) -> float:
        """Analyze use of transition words for flow"""
        try:
            transition_words = [
                'however', 'moreover', 'furthermore', 'therefore', 'consequently',
                'additionally', 'meanwhile', 'nevertheless', 'similarly',
                'in contrast', 'on the other hand', 'for example', 'for instance',
                'in conclusion', 'finally', 'first', 'second', 'third',
                'next', 'then', 'after', 'before', 'during', 'while',
                'although', 'because', 'since', 'as a result', 'thus'
            ]
            
            text_lower = text_content.lower()
            sentence_count = len([s for s in text_content.split('.') if s.strip()])
            
            if sentence_count == 0:
                return 0.0
                
            transition_count = 0
            for word in transition_words:
                transition_count += text_lower.count(word)
                
            # Optimal: 1 transition per 3-4 sentences
            transition_ratio = transition_count / sentence_count
            
            if 0.2 <= transition_ratio <= 0.4:
                return 1.0
            elif 0.1 <= transition_ratio < 0.2 or 0.4 < transition_ratio <= 0.6:
                return 0.8
            else:
                return 0.5
                
        except Exception:
            return 0.6

    async def _analyze_logical_flow(self, paragraphs: List[str]) -> float:
        """Analyze logical flow between paragraphs"""
        try:
            if not self.nlp or len(paragraphs) < 2:
                return 0.7  # Default for insufficient data
                
            flow_scores = []
            
            for i in range(len(paragraphs) - 1):
                # Analyze semantic similarity between adjacent paragraphs
                doc1 = self.nlp(paragraphs[i])
                doc2 = self.nlp(paragraphs[i + 1])
                
                similarity = doc1.similarity(doc2)
                
                # Good flow: moderate similarity (not too high, not too low)
                if 0.3 <= similarity <= 0.7:
                    flow_scores.append(1.0)
                elif 0.2 <= similarity < 0.3 or 0.7 < similarity <= 0.8:
                    flow_scores.append(0.8)
                else:
                    flow_scores.append(0.5)
                    
            return np.mean(flow_scores) if flow_scores else 0.7
            
        except Exception:
            return 0.6

    async def _analyze_intro_conclusion(self, paragraphs: List[str]) -> float:
        """Analyze introduction and conclusion quality"""
        try:
            if len(paragraphs) < 2:
                return 0.3
                
            intro = paragraphs[0].lower()
            conclusion = paragraphs[-1].lower()
            
            # Introduction indicators
            intro_words = ['introduction', 'begin', 'start', 'overview', 'explore',
                          'discuss', 'examine', 'consider', 'understand', 'learn']
            intro_score = 0.0
            
            for word in intro_words:
                if word in intro:
                    intro_score += 0.1
                    
            # Conclusion indicators
            conclusion_words = ['conclusion', 'summary', 'finally', 'in summary',
                              'to conclude', 'overall', 'ultimately', 'therefore',
                              'thus', 'end', 'finish']
            conclusion_score = 0.0
            
            for word in conclusion_words:
                if word in conclusion:
                    conclusion_score += 0.1
                    
            # Check for topic reinforcement (intro and conclusion similarity)
            if self.nlp:
                intro_doc = self.nlp(paragraphs[0])
                conclusion_doc = self.nlp(paragraphs[-1])
                topic_reinforcement = intro_doc.similarity(conclusion_doc)
                reinforcement_score = min(1.0, topic_reinforcement * 2)
            else:
                reinforcement_score = 0.5
                
            return (
                min(1.0, intro_score) * 0.4 +
                min(1.0, conclusion_score) * 0.4 +
                reinforcement_score * 0.2
            )
            
        except Exception:
            return 0.5

    async def _analyze_topic_coherence(self, paragraphs: List[str]) -> float:
        """Analyze topic coherence throughout content"""
        try:
            if not self.nlp or len(paragraphs) < 2:
                return 0.7
                
            # Extract key terms from each paragraph
            paragraph_terms = []
            
            for paragraph in paragraphs:
                doc = self.nlp(paragraph)
                terms = []
                
                for token in doc:
                    if (not token.is_stop and not token.is_punct and 
                        token.is_alpha and len(token.text) > 2):
                        terms.append(token.lemma_.lower())
                        
                paragraph_terms.append(set(terms))
                
            # Calculate coherence between all paragraph pairs
            coherence_scores = []
            
            for i in range(len(paragraph_terms)):
                for j in range(i + 1, len(paragraph_terms)):
                    intersection = len(paragraph_terms[i] & paragraph_terms[j])
                    union = len(paragraph_terms[i] | paragraph_terms[j])
                    
                    if union > 0:
                        jaccard_similarity = intersection / union
                        coherence_scores.append(jaccard_similarity)
                        
            if coherence_scores:
                return min(1.0, np.mean(coherence_scores) * 3)  # Amplify small similarities
            else:
                return 0.5
                
        except Exception:
            return 0.6

    async def _generate_content_fingerprint(self, text_content: str) -> str:
        """Generate content fingerprint for uniqueness checking"""
        try:
            # Normalize text
            normalized = re.sub(r'[^\w\s]', '', text_content.lower())
            words = normalized.split()
            
            # Create fingerprint using sliding window of 5-grams
            fingerprints = []
            
            for i in range(len(words) - 4):
                ngram = ' '.join(words[i:i+5])
                hash_obj = hashlib.md5(ngram.encode())
                fingerprints.append(hash_obj.hexdigest()[:8])
                
            # Combine fingerprints
            combined = ''.join(sorted(fingerprints))
            final_hash = hashlib.sha256(combined.encode()).hexdigest()
            
            return final_hash
            
        except Exception:
            return hashlib.md5(text_content.encode()).hexdigest()

    async def _check_semantic_uniqueness(self, text_content: str) -> float:
        """Check semantic uniqueness using NLP"""
        try:
            if not self.nlp:
                return 0.8  # Default high score
                
            doc = self.nlp(text_content)
            
            # Extract key concepts and entities
            key_concepts = []
            for token in doc:
                if (not token.is_stop and not token.is_punct and 
                    token.pos_ in ['NOUN', 'VERB', 'ADJ'] and len(token.text) > 2):
                    key_concepts.append(token.lemma_.lower())
                    
            # Add named entities
            for ent in doc.ents:
                key_concepts.append(ent.text.lower())
                
            # Calculate concept uniqueness (simplified)
            if key_concepts:
                unique_concepts = len(set(key_concepts))
                total_concepts = len(key_concepts)
                uniqueness_ratio = unique_concepts / total_concepts
                
                return min(1.0, uniqueness_ratio * 1.2)
            else:
                return 0.5
                
        except Exception:
            return 0.7

    async def _analyze_ngram_uniqueness(self, text_content: str) -> float:
        """Analyze n-gram uniqueness for plagiarism detection"""
        try:
            words = text_content.lower().split()
            
            if len(words) < 5:
                return 0.8  # Short content gets benefit
                
            # Generate 3-grams, 4-grams, and 5-grams
            ngrams_3 = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
            ngrams_4 = [' '.join(words[i:i+4]) for i in range(len(words)-3)]
            ngrams_5 = [' '.join(words[i:i+5]) for i in range(len(words)-4)]
            
            # Calculate uniqueness for each n-gram size
            uniqueness_scores = []
            
            for ngrams in [ngrams_3, ngrams_4, ngrams_5]:
                if ngrams:
                    unique_ngrams = len(set(ngrams))
                    total_ngrams = len(ngrams)
                    uniqueness = unique_ngrams / total_ngrams
                    uniqueness_scores.append(uniqueness)
                    
            if uniqueness_scores:
                return np.mean(uniqueness_scores)
            else:
                return 0.8
                
        except Exception:
            return 0.7

    async def _analyze_structure_uniqueness(self, text_content: str) -> float:
        """Analyze sentence structure uniqueness"""
        try:
            if not self.nlp:
                return 0.8
                
            doc = self.nlp(text_content)
            sentences = list(doc.sents)
            
            if len(sentences) < 2:
                return 0.8
                
            # Analyze sentence patterns
            patterns = []
            
            for sent in sentences:
                pattern = []
                for token in sent:
                    if not token.is_punct:
                        pattern.append(token.pos_)
                patterns.append(tuple(pattern))
                
            # Calculate pattern uniqueness
            unique_patterns = len(set(patterns))
            total_patterns = len(patterns)
            
            if total_patterns > 0:
                structure_uniqueness = unique_patterns / total_patterns
                return min(1.0, structure_uniqueness * 1.5)
            else:
                return 0.8
                
        except Exception:
            return 0.7

    async def _detect_paraphrasing(self, text_content: str) -> float:
        """Detect paraphrasing patterns"""
        try:
            # Simple paraphrase detection using sentence similarity
            sentences = [s.strip() for s in text_content.split('.') if s.strip()]
            
            if len(sentences) < 2 or not self.nlp:
                return 0.9  # High score for short content or no NLP
                
            paraphrase_scores = []
            
            for i in range(len(sentences)):
                for j in range(i + 1, len(sentences)):
                    doc1 = self.nlp(sentences[i])
                    doc2 = self.nlp(sentences[j])
                    
                    similarity = doc1.similarity(doc2)
                    
                    # High similarity might indicate paraphrasing
                    if similarity > 0.8:
                        paraphrase_scores.append(0.3)  # Potential paraphrase
                    elif similarity > 0.6:
                        paraphrase_scores.append(0.7)  # Some similarity
                    else:
                        paraphrase_scores.append(1.0)  # Unique content
                        
            if paraphrase_scores:
                return np.mean(paraphrase_scores)
            else:
                return 0.9
                
        except Exception:
            return 0.8

    async def _analyze_statistical_uniqueness(self, text_content: str) -> float:
        """Analyze statistical uniqueness of language patterns"""
        try:
            words = text_content.lower().split()
            
            if len(words) < 10:
                return 0.8
                
            # Calculate word frequency distribution
            word_freq = Counter(words)
            frequencies = list(word_freq.values())
            
            # Calculate statistical measures
            mean_freq = np.mean(frequencies)
            std_freq = np.std(frequencies)
            
            # Vocabulary richness (Hapax Legomena ratio)
            hapax_count = sum(1 for freq in frequencies if freq == 1)
            hapax_ratio = hapax_count / len(words)
            
            # Unique vocabulary ratio
            unique_words = len(set(words))
            unique_ratio = unique_words / len(words)
            
            # Combine statistical measures
            statistical_score = (
                min(1.0, hapax_ratio * 2) * 0.4 +  # Hapax ratio
                min(1.0, unique_ratio * 2) * 0.4 +  # Unique word ratio
                min(1.0, std_freq / max(mean_freq, 1)) * 0.2  # Frequency variance
            )
            
            return statistical_score
            
        except Exception:
            return 0.7

    async def _analyze_citation_patterns(self, text_content: str) -> float:
        """Analyze citation and reference patterns"""
        try:
            # Look for citation patterns
            citation_patterns = [
                r'\([^)]*\d{4}[^)]*\)',  # (Author, 2024)
                r'\[[^\]]*\d+[^\]]*\]',  # [1], [Reference 1]
                r'according to\s+[A-Z][a-z]+',  # "according to Smith"
                r'as\s+[A-Z][a-z]+\s+states',  # "as Johnson states"
                r'research\s+by\s+[A-Z][a-z]+',  # "research by Brown"
            ]
            
            citation_count = 0
            for pattern in citation_patterns:
                matches = re.findall(pattern, text_content)
                citation_count += len(matches)
                
            word_count = len(text_content.split())
            
            if word_count == 0:
                return 0.5
                
            # Citation density (citations per 100 words)
            citation_density = (citation_count / word_count) * 100
            
            # Appropriate citation indicates proper sourcing
            if 1 <= citation_density <= 5:
                return 0.9  # Good citation practice
            elif 0.5 <= citation_density < 1:
                return 0.7  # Some citations
            elif citation_density > 5:
                return 0.6  # Too many citations might indicate lack of originality
            else:
                return 0.8  # No citations (could be original content)
                
        except Exception:
            return 0.7
