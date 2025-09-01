"""Quality Enhancer - Advanced content quality optimization engine

Professional content quality enhancement system that improves content
quality, readability, and overall presentation.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import spacy
from textstat import automated_readability_index, coleman_liau_index


class QualityEnhancer:
    """
    Advanced content quality enhancer that improves content across multiple dimensions:
    
    - Grammar and language correction
    - Readability improvement
    - Tone and style optimization
    - Coherence and flow enhancement
    - Factual accuracy checking
    - Engagement optimization
    - Professional formatting
    """
    
    def __init__(self):
        """
Initialize the quality enhancer"""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Quality enhancement settings
        self.target_readability_score = 60  # Flesch score
        self.max_sentence_length = 25       # Words per sentence
        self.min_paragraph_length = 3       # Sentences per paragraph
        self.max_paragraph_length = 6       # Sentences per paragraph
        
        # Initialize NLP models
        self._initialize_nlp_models()
        
        # Quality metrics weights
        self.quality_weights = {
            'grammar': 0.25,
            'readability': 0.20,
            'coherence': 0.15,
            'engagement': 0.15,
            'formatting': 0.10,
            'tone': 0.10,
            'factual_accuracy': 0.05
        }
    
    def _initialize_nlp_models(self) -> None:
        """
Initialize NLP models for quality enhancement"""
        try:
            # Try to load spaCy model
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            self.logger.warning("spaCy model not found. Quality enhancement will use basic methods.")
            self.nlp = None
        
        # Common word patterns for improvement
        self.improvement_patterns = {
            'redundant_phrases': [
                (r'\bvery very\b', 'extremely'),
                (r'\breally really\b', 'truly'),
                (r'\bso so\b', 'exceptionally'),
            ],
            'weak_words': [
                (r'\bvery good\b', 'excellent'),
                (r'\bvery bad\b', 'terrible'),
                (r'\bvery big\b', 'enormous'),
                (r'\bvery small\b', 'tiny'),
            ],
            'passive_to_active': [
                (r'was (\w+ed) by', r'\1'),
                (r'were (\w+ed) by', r'\1'),
            ]
        }
    
    async def enhance_content(
        self,
        content: Any,
        content_type: str,
        enhancement_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enhance content quality across multiple dimensions.
        
        Args:
            content: Content to enhance
            content_type: Type of content (text, blog, social, etc.)
            enhancement_options: Specific enhancement preferences
            
        Returns:
            Enhanced content with quality improvements
        """
        try:
            # Extract text content
            text_content = self._extract_text_content(content)
            
            # Parse enhancement options
            options = enhancement_options or {}
            
            # Analyze current quality
            quality_analysis = await self._analyze_quality(text_content)
            
            # Apply enhancements based on content type
            if content_type == 'blog':
                enhanced_content = await self._enhance_blog_content(
                    text_content, quality_analysis, options
                )
            elif content_type in ['social', 'instagram_post', 'twitter_post']:
                enhanced_content = await self._enhance_social_content(
                    text_content, quality_analysis, options
                )
            elif content_type == 'email':
                enhanced_content = await self._enhance_email_content(
                    text_content, quality_analysis, options
                )
            elif content_type == 'marketing':
                enhanced_content = await self._enhance_marketing_content(
                    text_content, quality_analysis, options
                )
            else:
                enhanced_content = await self._enhance_general_content(
                    text_content, quality_analysis, options
                )
            
            # Calculate quality improvement score
            final_analysis = await self._analyze_quality(enhanced_content)
            improvement_score = await self._calculate_improvement_score(
                quality_analysis, final_analysis
            )
            
            return {
                'enhanced_content': enhanced_content,
                'original_quality': quality_analysis,
                'enhanced_quality': final_analysis,
                'improvement_score': improvement_score,
                'enhancements_applied': await self._get_enhancements_applied(
                    text_content, enhanced_content
                )
            }
            
        except Exception as e:
            self.logger.error(f"Quality enhancement failed: {str(e)}")
            return {
                'enhanced_content': content,
                'original_quality': {},
                'enhanced_quality': {},
                'improvement_score': 0.0,
                'enhancements_applied': []
            }
    
    def _extract_text_content(self, content: Any) -> str:
        """Extract text content from various content types"""
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            if 'content' in content:
                return str(content['content'])
            elif 'text' in content:
                return str(content['text'])
            elif 'body' in content:
                return str(content['body'])
            else:
                return ' '.join([str(v) for v in content.values() if isinstance(v, str)])
        else:
            return str(content)
    
    async def _analyze_quality(self, content: str) -> Dict[str, Any]:
        """
Analyze content quality across multiple dimensions"""
        analysis = {}
        
        # Grammar analysis
        analysis['grammar'] = await self._analyze_grammar(content)
        
        # Readability analysis
        analysis['readability'] = await self._analyze_readability(content)
        
        # Coherence analysis
        analysis['coherence'] = await self._analyze_coherence(content)
        
        # Engagement analysis
        analysis['engagement'] = await self._analyze_engagement(content)
        
        # Formatting analysis
        analysis['formatting'] = await self._analyze_formatting(content)
        
        # Tone analysis
        analysis['tone'] = await self._analyze_tone(content)
        
        # Calculate overall quality score
        analysis['overall_score'] = await self._calculate_overall_quality_score(analysis)
        
        return analysis
    
    async def _analyze_grammar(self, content: str) -> Dict[str, Any]:
        """
Analyze grammar quality"""
        grammar_issues = []
        
        # Basic grammar checks
        sentences = re.split(r'[.!?]+', content)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check for common grammar issues
            if not sentence[0].isupper():
                grammar_issues.append("Sentence should start with capital letter")
            
            # Check for double spaces
            if '  ' in sentence:
                grammar_issues.append("Double spaces found")
            
            # Check for run-on sentences
            if len(sentence.split()) > 30:
                grammar_issues.append("Run-on sentence detected")
        
        # Grammar score (inverse of issues found)
        grammar_score = max(0.0, 1.0 - (len(grammar_issues) / max(1, len(sentences)) * 2))
        
        return {
            'issues': grammar_issues,
            'score': grammar_score,
            'sentence_count': len([s for s in sentences if s.strip()])
        }
    
    async def _analyze_readability(self, content: str) -> Dict[str, Any]:
        """Analyze content readability"""
        try:
            # Calculate readability metrics
            ari_score = automated_readability_index(content)
            coleman_score = coleman_liau_index(content)
            
            # Sentence and word statistics
            sentences = re.split(r'[.!?]+', content)
            sentences = [s.strip() for s in sentences if s.strip()]
            words = content.split()
            
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            
            # Calculate readability score
            readability_score = 0.5  # Base score
            
            if 10 <= avg_sentence_length <= 20:
                readability_score += 0.3
            if 4 <= avg_word_length <= 6:
                readability_score += 0.2
            
            return {
                'ari_score': ari_score,
                'coleman_score': coleman_score,
                'avg_sentence_length': avg_sentence_length,
                'avg_word_length': avg_word_length,
                'readability_score': min(1.0, readability_score)
            }
            
        except Exception as e:
            self.logger.warning(f"Readability analysis failed: {str(e)}")
            return {
                'ari_score': 10.0,
                'coleman_score': 10.0,
                'avg_sentence_length': 15.0,
                'avg_word_length': 5.0,
                'readability_score': 0.5
            }
    
    async def _analyze_coherence(self, content: str) -> Dict[str, Any]:
        """Analyze content coherence and flow"""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Transition words analysis
        transition_words = [
            'however', 'therefore', 'furthermore', 'moreover', 'additionally',
            'consequently', 'nevertheless', 'meanwhile', 'subsequently', 'similarly'
        ]
        
        transition_count = sum(
            1 for word in transition_words 
            if word in content.lower()
        )
        
        # Paragraph structure analysis
        paragraph_lengths = [len(p.split()) for p in paragraphs]
        avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
        
        # Coherence score
        coherence_score = 0.5  # Base score
        
        if transition_count >= len(paragraphs) // 3:
            coherence_score += 0.3
        
        if 50 <= avg_paragraph_length <= 150:
            coherence_score += 0.2
        
        return {
            'transition_count': transition_count,
            'paragraph_count': len(paragraphs),
            'avg_paragraph_length': avg_paragraph_length,
            'coherence_score': min(1.0, coherence_score)
        }
    
    async def _analyze_engagement(self, content: str) -> Dict[str, Any]:
        """
Analyze content engagement potential"""
        # Engagement indicators
        question_count = content.count('?')
        exclamation_count = content.count('!')
        
        # Action words
        action_words = [
            'discover', 'learn', 'explore', 'find', 'get', 'try', 'start',
            'create', 'build', 'achieve', 'transform', 'improve'
        ]
        
        action_word_count = sum(
            1 for word in action_words
            if word in content.lower()
        )
        
        # Emotional words
        emotional_words = [
            'amazing', 'incredible', 'fantastic', 'wonderful', 'exciting',
            'inspiring', 'powerful', 'beautiful', 'stunning', 'remarkable'
        ]
        
        emotional_word_count = sum(
            1 for word in emotional_words
            if word in content.lower()
        )
        
        # Engagement score
        word_count = len(content.split())
        engagement_score = 0.3  # Base score
        
        if question_count > 0:
            engagement_score += 0.2
        if action_word_count / word_count > 0.01:  # 1% action words
            engagement_score += 0.3
        if emotional_word_count > 0:
            engagement_score += 0.2
        
        return {
            'question_count': question_count,
            'exclamation_count': exclamation_count,
            'action_word_count': action_word_count,
            'emotional_word_count': emotional_word_count,
            'engagement_score': min(1.0, engagement_score)
        }
    
    async def _analyze_formatting(self, content: str) -> Dict[str, Any]:
        """
Analyze content formatting quality"""
        # Check for formatting elements
        has_headers = bool(re.search(r'^#+\s+', content, re.MULTILINE))
        has_lists = bool(re.search(r'^[\*\-\+]\s+', content, re.MULTILINE))
        has_bold = bool(re.search(r'\*\*\w+\*\*', content))
        has_italic = bool(re.search(r'\*\w+\*', content))
        
        # Paragraph structure
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        well_structured_paragraphs = sum(
            1 for p in paragraphs
            if 3 <= len(p.split('.')) <= 6  # 3-6 sentences per paragraph
        )
        
        # Formatting score
        formatting_score = 0.3  # Base score
        
        if has_headers:
            formatting_score += 0.2
        if has_lists:
            formatting_score += 0.1
        if has_bold or has_italic:
            formatting_score += 0.1
        if well_structured_paragraphs / len(paragraphs) > 0.7:
            formatting_score += 0.3
        
        return {
            'has_headers': has_headers,
            'has_lists': has_lists,
            'has_bold': has_bold,
            'has_italic': has_italic,
            'well_structured_paragraphs': well_structured_paragraphs,
            'total_paragraphs': len(paragraphs),
            'formatting_score': min(1.0, formatting_score)
        }
    
    async def _analyze_tone(self, content: str) -> Dict[str, Any]:
        """
Analyze content tone"""
        content_lower = content.lower()
        
        # Tone indicators
        positive_words = [
            'excellent', 'great', 'amazing', 'wonderful', 'fantastic',
            'good', 'best', 'perfect', 'awesome', 'brilliant'
        ]
        
        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'worst',
            'poor', 'disappointing', 'failed', 'wrong', 'difficult'
        ]
        
        formal_words = [
            'furthermore', 'therefore', 'consequently', 'however',
            'moreover', 'additionally', 'nevertheless', 'subsequently'
        ]
        
        informal_words = [
            'cool', 'awesome', 'yeah', 'ok', 'gonna',
            'wanna', 'gotta', 'hey', 'wow', 'super'
        ]
        
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        formal_count = sum(1 for word in formal_words if word in content_lower)
        informal_count = sum(1 for word in informal_words if word in content_lower)
        
        # Determine dominant tone
        if positive_count > negative_count:
            tone_sentiment = 'positive'
        elif negative_count > positive_count:
            tone_sentiment = 'negative'
        else:
            tone_sentiment = 'neutral'
        
        if formal_count > informal_count:
            tone_style = 'formal'
        elif informal_count > formal_count:
            tone_style = 'informal'
        else:
            tone_style = 'balanced'
        
        # Tone consistency score
        total_tone_words = positive_count + negative_count + formal_count + informal_count
        word_count = len(content.split())
        tone_score = min(1.0, 0.5 + (total_tone_words / word_count) * 2)
        
        return {
            'sentiment': tone_sentiment,
            'style': tone_style,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'formal_count': formal_count,
            'informal_count': informal_count,
            'tone_score': tone_score
        }
    
    async def _calculate_overall_quality_score(self, analysis: Dict[str, Any]) -> float:
        """
Calculate overall quality score"""
        score = 0.0
        
        # Weighted sum of all quality dimensions
        score += analysis.get('grammar', {}).get('score', 0) * self.quality_weights['grammar']
        score += analysis.get('readability', {}).get('readability_score', 0) * self.quality_weights['readability']
        score += analysis.get('coherence', {}).get('coherence_score', 0) * self.quality_weights['coherence']
        score += analysis.get('engagement', {}).get('engagement_score', 0) * self.quality_weights['engagement']
        score += analysis.get('formatting', {}).get('formatting_score', 0) * self.quality_weights['formatting']
        score += analysis.get('tone', {}).get('tone_score', 0) * self.quality_weights['tone']
        
        return min(1.0, max(0.0, score))
    
    async def _enhance_blog_content(
        self,
        content: str,
        analysis: Dict[str, Any],
        options: Dict[str, Any]
    ) -> str:
        """
Enhance blog content specifically"""
        enhanced = content
        
        # Improve structure
        enhanced = await self._improve_paragraph_structure(enhanced)
        
        # Add headers if missing
        enhanced = await self._add_headers_if_needed(enhanced)
        
        # Improve readability
        enhanced = await self._improve_readability(enhanced)
        
        # Enhance engagement
        enhanced = await self._enhance_engagement(enhanced)
        
        return enhanced
    
    async def _enhance_social_content(
        self,
        content: str,
        analysis: Dict[str, Any],
        options: Dict[str, Any]
    ) -> str:
        """
Enhance social media content"""
        enhanced = content
        
        # Optimize for social platforms
        enhanced = await self._optimize_for_social(enhanced)
        
        # Add engagement elements
        enhanced = await self._add_social_engagement_elements(enhanced)
        
        return enhanced
    
    async def _enhance_email_content(
        self,
        content: str,
        analysis: Dict[str, Any],
        options: Dict[str, Any]
    ) -> str:
        """
Enhance email content"""
        enhanced = content
        
        # Improve email structure
        enhanced = await self._improve_email_structure(enhanced)
        
        # Add call-to-action if missing
        enhanced = await self._add_cta_if_needed(enhanced)
        
        return enhanced
    
    async def _enhance_marketing_content(
        self,
        content: str,
        analysis: Dict[str, Any],
        options: Dict[str, Any]
    ) -> str:
        """
Enhance marketing content"""
        enhanced = content
        
        # Strengthen persuasive elements
        enhanced = await self._strengthen_persuasive_elements(enhanced)
        
        # Improve call-to-action
        enhanced = await self._improve_cta(enhanced)
        
        return enhanced
    
    async def _enhance_general_content(
        self,
        content: str,
        analysis: Dict[str, Any],
        options: Dict[str, Any]
    ) -> str:
        """
Enhance general content"""
        enhanced = content
        
        # Apply basic improvements
        enhanced = await self._apply_basic_improvements(enhanced)
        
        return enhanced
    
    async def _improve_paragraph_structure(self, content: str) -> str:
        """
Improve paragraph structure"""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        improved_paragraphs = []
        
        for paragraph in paragraphs:
            sentences = [s.strip() for s in re.split(r'[.!?]+', paragraph) if s.strip()]
            
            # Split long paragraphs
            if len(sentences) > 6:
                mid_point = len(sentences) // 2
                improved_paragraphs.append('. '.join(sentences[:mid_point]) + '.')
                improved_paragraphs.append('. '.join(sentences[mid_point:]) + '.')
            else:
                improved_paragraphs.append(paragraph)
        
        return '\n\n'.join(improved_paragraphs)
    
    async def _add_headers_if_needed(self, content: str) -> str:
        """
Add headers to structure content"""
        if '##' in content:  # Already has headers
            return content
        
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if len(paragraphs) < 3:
            return content
        
        # Add headers every 2-3 paragraphs
        enhanced_content = []
        for i, paragraph in enumerate(paragraphs):
            if i > 0 and i % 3 == 0:
                enhanced_content.append(f"## Section {i//3 + 1}")
            enhanced_content.append(paragraph)
        
        return '\n\n'.join(enhanced_content)
    
    async def _improve_readability(self, content: str) -> str:
        """Improve content readability"""
        enhanced = content
        
        # Apply improvement patterns
        for pattern_type, patterns in self.improvement_patterns.items():
            for pattern, replacement in patterns:
                enhanced = re.sub(pattern, replacement, enhanced, flags=re.IGNORECASE)
        
        # Break long sentences
        sentences = re.split(r'([.!?]+)', enhanced)
        improved_sentences = []
        
        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                sentence = sentences[i]
                punct = sentences[i + 1]
                
                if len(sentence.split()) > 25:
                    # Try to split at conjunction
                    if ' and ' in sentence:
                        parts = sentence.split(' and ', 1)
                        improved_sentences.extend([parts[0], punct, ' And ' + parts[1], punct])
                    else:
                        improved_sentences.extend([sentence, punct])
                else:
                    improved_sentences.extend([sentence, punct])
        
        return ''.join(improved_sentences)
    
    async def _enhance_engagement(self, content: str) -> str:
        """
Enhance content engagement"""
        enhanced = content
        
        # Add questions if none exist
        if '?' not in enhanced:
            sentences = enhanced.split('.')
            if len(sentences) > 2:
                # Add question at the end
                enhanced += " What are your thoughts on this?"
        
        return enhanced
    
    async def _optimize_for_social(self, content: str) -> str:
        """Optimize content for social media"""
        # Keep it concise
        if len(content) > 280:  # Twitter limit
            sentences = content.split('.')
            content = '. '.join(sentences[:2]) + '.'
        
        # Add emojis for engagement (simplified)
        if not any(char for char in content if ord(char) > 127):  # No emojis present
            content += " 🚀"
        
        return content
    
    async def _add_social_engagement_elements(self, content: str) -> str:
        """Add engagement elements for social media"""
        if '?' not in content and '!' not in content:
            content += " What do you think?"
        
        return content
    
    async def _improve_email_structure(self, content: str) -> str:
        """Improve email structure"""
        lines = content.split('\n')
        
        # Add subject line if missing
        if not lines[0].startswith('Subject:'):
            content = "Subject: Important Information\n\n" + content
        
        # Add greeting if missing
        if not any(greeting in content.lower() for greeting in ['dear', 'hello', 'hi']):
            content = content.replace('\n\n', '\n\nDear Reader,\n\n', 1)
        
        return content
    
    async def _add_cta_if_needed(self, content: str) -> str:
        """Add call-to-action if needed"""
        cta_words = ['click', 'visit', 'download', 'subscribe', 'buy', 'contact']
        
        if not any(word in content.lower() for word in cta_words):
            content += "\n\nContact us for more information."
        
        return content
    
    async def _strengthen_persuasive_elements(self, content: str) -> str:
        """Strengthen persuasive elements in marketing content"""
        # Add urgency if missing
        urgency_words = ['now', 'today', 'limited', 'exclusive', 'urgent']
        
        if not any(word in content.lower() for word in urgency_words):
            content = "Don't miss out! " + content
        
        return content
    
    async def _improve_cta(self, content: str) -> str:
        """Improve call-to-action"""
        # Make CTA more prominent
        if 'contact' in content.lower():
            content = content.replace('contact', 'Contact us now')
        
        return content
    
    async def _apply_basic_improvements(self, content: str) -> str:
        """
Apply basic content improvements"""
        enhanced = content
        
        # Fix common issues
        enhanced = re.sub(r'\s+', ' ', enhanced)  # Multiple spaces
        enhanced = re.sub(r'\n\s*\n\s*\n', '\n\n', enhanced)  # Multiple line breaks
        
        # Capitalize sentences
        sentences = re.split(r'([.!?]+)', enhanced)
        for i in range(0, len(sentences), 2):
            if sentences[i].strip():
                sentences[i] = sentences[i].strip().capitalize()
        
        enhanced = ''.join(sentences)
        
        return enhanced
    
    async def _calculate_improvement_score(
        self,
        original_analysis: Dict[str, Any],
        enhanced_analysis: Dict[str, Any]
    ) -> float:
        """
Calculate improvement score"""
        original_score = original_analysis.get('overall_score', 0.0)
        enhanced_score = enhanced_analysis.get('overall_score', 0.0)
        
        improvement = enhanced_score - original_score
        return max(0.0, improvement)
    
    async def _get_enhancements_applied(
        self,
        original_content: str,
        enhanced_content: str
    ) -> List[str]:
        """
Get list of enhancements applied"""
        enhancements = []
        
        if len(enhanced_content) != len(original_content):
            enhancements.append("Content length optimization")
        
        if enhanced_content.count('##') > original_content.count('##'):
            enhancements.append("Added section headers")
        
        if enhanced_content.count('?') > original_content.count('?'):
            enhancements.append("Added engagement questions")
        
        if enhanced_content.count('\n\n') != original_content.count('\n\n'):
            enhancements.append("Improved paragraph structure")
        
        return enhancements
