"""Blog Templates - Professional blog content templates and structures

Comprehensive template system for creating high-quality blog content
with optimized structures for different types of blog posts.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import random


class BlogTemplates:
    """    Professional blog template collection providing:
    
    - How-to and tutorial templates
    - List-based content templates  
    - Thought leadership templates
    - Product review templates
    - News and analysis templates
    - Personal story templates
    - SEO-optimized structures
    - Engagement-driven layouts
    """    
    def __init__(self):
        """Initialize blog templates"""        self.logger = logging.getLogger(self.__class__.__name__)
        
        # How-to/Tutorial Templates
        self.tutorial_templates = {
            'step_by_step_guide': {
                'structure': """# How to {title}: A Complete Guide

## Introduction

{hook}

{problem_statement}

{solution_overview}

## What You'll Need

{requirements_list}

## Step-by-Step Instructions

{steps}

## Pro Tips

{pro_tips}

## Common Mistakes to Avoid

{mistakes}

## Conclusion

{conclusion}

{call_to_action}""",
                'hooks': [
                    "Ever wondered how to {topic}? You're in the right place.",
                    "Struggling with {topic}? This guide will change everything.",
                    "Master {topic} with this comprehensive step-by-step guide.",
                    "Ready to become an expert at {topic}? Let's dive in."
                ]
            },
            'beginner_tutorial': {
                'structure': """# {title} for Beginners: Everything You Need to Know

## Why This Matters

{importance}

## Getting Started

{basics}

## Core Concepts

{concepts}

## Practical Examples

{examples}

## Next Steps

{progression}

## Resources for Learning More

{resources}""",
                'hooks': [
                    "New to {topic}? Don't worry - we've all been there.",
                    "Starting your {topic} journey? This guide is for you.",
                    "Complete beginner to {topic}? Perfect timing."
                ]
            }
        }
        
        # List-based Templates
        self.list_templates = {
            'top_tips': {
                'structure': """# {number} {adjective} Tips for {topic}

## Introduction

{intro}

{tips_list}

## Bonus Tip

{bonus_tip}

## Conclusion

{conclusion}

{engagement_cta}""",
                'adjectives': ['Essential', 'Proven', 'Game-Changing', 'Expert', 'Insider'],
                'intro_hooks': [
                    "Want to excel at {topic}? These tips will get you there.",
                    "Looking to improve your {topic} skills? You're in luck.",
                    "Ready to take your {topic} to the next level?"
                ]
            },
            'best_practices': {
                'structure': """# {number} Best Practices for {topic} in {year}

## Why Best Practices Matter

{importance}

## The Best Practices

{practices_list}

## Implementation Strategy

{implementation}

## Measuring Success

{metrics}

## Final Thoughts

{conclusion}""",
                'practices_intro': [
                    "Here are the best practices that actually work:",
                    "These proven strategies will transform your approach:",
                    "Industry experts swear by these practices:"
                ]
            }
        }
        
        # Thought Leadership Templates
        self.thought_leadership_templates = {
            'industry_analysis': {
                'structure': """# The Future of {industry}: {prediction}

## Current State of the Industry

{current_analysis}

## Emerging Trends

{trends}

## Challenges Ahead

{challenges}

## Opportunities

{opportunities}

## My Prediction

{prediction_detail}

## What This Means for You

{implications}

## Conclusion

{final_thoughts}""",
                'hooks': [
                    "The {industry} landscape is shifting rapidly.",
                    "Big changes are coming to {industry}.",
                    "Here's what I see happening in {industry}."
                ]
            },
            'opinion_piece': {
                'structure': """# {controversial_statement}

## Setting the Context

{context}

## The Common Belief

{conventional_wisdom}

## Why I Disagree

{counterargument}

## Evidence Supporting My View

{evidence}

## Implications

{consequences}

## What This Means for You

{actionable_advice}

## Conclusion

{final_stance}""",
                'hooks': [
                    "This might be controversial, but hear me out.",
                    "I'm about to challenge conventional wisdom.",
                    "Unpopular opinion incoming:"
                ]
            }
        }
        
        # Product Review Templates
        self.review_templates = {
            'comprehensive_review': {
                'structure': """# {product_name} Review: {verdict}

## Product Overview

{overview}

## Key Features

{features}

## Pros and Cons

### Pros
{pros}

### Cons
{cons}

## Performance Analysis

{performance}

## Comparison with Competitors

{comparison}

## Who Should Buy This?

{target_audience}

## Final Verdict

{final_rating}

{recommendation}""",
                'verdicts': ['Worth Every Penny', 'A Solid Choice', 'Has Potential', 'Skip This One'],
                'rating_scales': ['⭐⭐⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐', '⭐⭐', '⭐']
            },
            'quick_review': {
                'structure': """# Quick Take: {product_name}

## The Bottom Line

{summary}

## What I Loved

{highlights}

## What Could Be Better

{improvements}

## Should You Buy It?

{recommendation}

## Rating: {rating}"""            }
        }
        
        # News and Analysis Templates
        self.news_templates = {
            'news_analysis': {
                'structure': """# {headline}: What This Really Means

## What Happened

{facts}

## Why This Matters

{significance}

## Industry Impact

{industry_implications}

## What Experts Are Saying

{expert_opinions}

## What's Next

{predictions}

## Key Takeaways

{takeaways}""",
                'hooks': [
                    "Big news just dropped in {industry}.",
                    "Everyone's talking about {event}. Here's my take.",
                    "This {event} changes everything."
                ]
            },
            'trend_report': {
                'structure': """# {trend_name}: The {timeframe} Trend Report

## Executive Summary

{summary}

## Key Statistics

{stats}

## What's Driving This Trend

{drivers}

## Case Studies

{examples}

## Impact on {industry}

{impact}

## Future Outlook

{forecast}

## Action Items

{recommendations}"""            }
        }
        
        # Personal Story Templates
        self.story_templates = {
            'lesson_learned': {
                'structure': """# What {experience} Taught Me About {lesson}

## The Setup

{background}

## The Challenge

{problem}

## What I Did

{actions}

## The Results

{outcomes}

## The Lesson

{learning}

## How You Can Apply This

{application}

## Final Thoughts

{reflection}""",
                'hooks': [
                    "Sometimes the best lessons come from unexpected places.",
                    "I learned this lesson the hard way.",
                    "Here's a story that changed my perspective."
                ]
            },
            'success_story': {
                'structure': """# How I {achievement} in {timeframe}

## Where I Started

{starting_point}

## The Goal

{objective}

## The Strategy

{approach}

## Challenges I Faced

{obstacles}

## Breakthrough Moments

{breakthroughs}

## The Results

{results}

## Key Lessons

{lessons}

## Your Turn

{encouragement}"""            }
        }
        
        # SEO-optimized structures
        self.seo_structures = {
            'pillar_content': {
                'structure': """# The Complete Guide to {topic}

## Table of Contents
{toc}

## Introduction

{intro}

## Chapter 1: {chapter1_title}
{chapter1_content}

## Chapter 2: {chapter2_title}  
{chapter2_content}

## Chapter 3: {chapter3_title}
{chapter3_content}

## Conclusion

{conclusion}

## Related Resources

{internal_links}

## FAQ

{faq_section}""",
                'word_count_target': 3000
            },
            'keyword_focused': {
                'structure': """# {primary_keyword}: {compelling_title}

## Introduction
{keyword_intro}

## What is {primary_keyword}?
{definition}

## Benefits of {primary_keyword}
{benefits}

## How to {action} {primary_keyword}
{how_to}

## Best {primary_keyword} {tools/strategies}
{recommendations}

## Common {primary_keyword} Mistakes
{mistakes}

## Conclusion
{keyword_conclusion}""",
                'keyword_density_target': 0.02  # 2% keyword density
            }
        }
    
    def get_template(
        self, 
        template_category: str, 
        template_type: str,
        content_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Get blog template for specific category and type.
        
        Args:
            template_category: Category (tutorial, list, thought_leadership, etc.)
            template_type: Specific template type
            content_data: Data to customize template
            
        Returns:
            Template structure and metadata
        """        try:
            category_templates = getattr(self, f"{template_category}_templates", {})
            template = category_templates.get(template_type, {})
            
            if not template:
                self.logger.warning(f"Template not found: {template_category}.{template_type}")
                return self._get_default_blog_template()
            
            return template
            
        except Exception as e:
            self.logger.error(f"Error getting template: {str(e)}")
            return self._get_default_blog_template()
    
    def fill_template(
        self,
        template_category: str,
        template_type: str,
        content_data: Dict[str, Any]
    ) -> str:
        """        Fill blog template with content data.
        
        Args:
            template_category: Template category
            template_type: Template type
            content_data: Data to fill template
            
        Returns:
            Complete blog post content
        """        try:
            template = self.get_template(template_category, template_type, content_data)
            
            if not template:
                return self._create_basic_blog_post(content_data)
            
            structure = template.get('structure', '')
            
            # Fill template with content
            filled_content = self._fill_blog_placeholders(structure, content_data, template)
            
            # Apply SEO optimizations
            filled_content = self._apply_seo_optimizations(filled_content, content_data)
            
            return filled_content
            
        except Exception as e:
            self.logger.error(f"Error filling template: {str(e)}")
            return self._create_basic_blog_post(content_data)
    
    def _fill_blog_placeholders(
        self, 
        structure: str, 
        content_data: Dict[str, Any], 
        template: Dict[str, Any]
    ) -> str:
        """Fill placeholders in blog template"""        filled = structure
        
        # Fill direct data mappings
        for key, value in content_data.items():
            placeholder = f"{{{key}}}"
            if placeholder in filled:
                filled = filled.replace(placeholder, str(value))
        
        # Fill template-specific elements
        filled = self._fill_hooks(filled, template, content_data)
        filled = self._fill_lists(filled, content_data)
        filled = self._fill_sections(filled, content_data)
        filled = self._fill_meta_elements(filled, content_data)
        
        return filled
    
    def _fill_hooks(self, content: str, template: Dict[str, Any], content_data: Dict[str, Any]) -> str:
        """Fill hook placeholders with engaging openers"""        hooks = template.get('hooks', [])
        
        if '{hook}' in content and hooks:
            selected_hook = random.choice(hooks)
            # Replace topic placeholder in hook
            topic = content_data.get('topic', content_data.get('title', 'this topic'))
            selected_hook = selected_hook.replace('{topic}', topic)
            content = content.replace('{hook}', selected_hook)
        
        return content
    
    def _fill_lists(self, content: str, content_data: Dict[str, Any]) -> str:
        """Fill list-based content sections"""        # Fill tips list
        if '{tips_list}' in content:
            tips = content_data.get('tips', [])
            if tips:
                tips_formatted = '\n'.join([f"## {i+1}. {tip}" for i, tip in enumerate(tips)])
                content = content.replace('{tips_list}', tips_formatted)
        
        # Fill steps
        if '{steps}' in content:
            steps = content_data.get('steps', [])
            if steps:
                steps_formatted = '\n'.join([f"### Step {i+1}: {step}" for i, step in enumerate(steps)])
                content = content.replace('{steps}', steps_formatted)
        
        # Fill features
        if '{features}' in content:
            features = content_data.get('features', [])
            if features:
                features_formatted = '\n'.join([f"- {feature}" for feature in features])
                content = content.replace('{features}', features_formatted)
        
        # Fill pros
        if '{pros}' in content:
            pros = content_data.get('pros', [])
            if pros:
                pros_formatted = '\n'.join([f"✅ {pro}" for pro in pros])
                content = content.replace('{pros}', pros_formatted)
        
        # Fill cons
        if '{cons}' in content:
            cons = content_data.get('cons', [])
            if cons:
                cons_formatted = '\n'.join([f"❌ {con}" for con in cons])
                content = content.replace('{cons}', cons_formatted)
        
        return content
    
    def _fill_sections(self, content: str, content_data: Dict[str, Any]) -> str:
        """Fill major content sections"""        # Generate table of contents if needed
        if '{toc}' in content:
            toc = self._generate_table_of_contents(content)
            content = content.replace('{toc}', toc)
        
        # Fill FAQ section
        if '{faq_section}' in content:
            faqs = content_data.get('faqs', [])
            if faqs:
                faq_formatted = '\n'.join([
                    f"### Q: {faq.get('question', '')}\n\nA: {faq.get('answer', '')}\n" 
                    for faq in faqs
                ])
                content = content.replace('{faq_section}', faq_formatted)
        
        # Fill internal links
        if '{internal_links}' in content:
            links = content_data.get('related_links', [])
            if links:
                links_formatted = '\n'.join([f"- [{link.get('title', '')}]({link.get('url', '#')})" for link in links])
                content = content.replace('{internal_links}', links_formatted)
        
        return content
    
    def _fill_meta_elements(self, content: str, content_data: Dict[str, Any]) -> str:
        """Fill meta elements like ratings, dates, etc."""        # Fill rating
        if '{rating}' in content:
            rating = content_data.get('rating', 4)
            stars = '⭐' * int(rating)
            content = content.replace('{rating}', f"{stars} ({rating}/5)")
        
        # Fill year
        if '{year}' in content:
            year = content_data.get('year', datetime.now().year)
            content = content.replace('{year}', str(year))
        
        # Fill timeframe
        if '{timeframe}' in content:
            timeframe = content_data.get('timeframe', '2024')
            content = content.replace('{timeframe}', timeframe)
        
        return content
    
    def _generate_table_of_contents(self, content: str) -> str:
        """Generate table of contents from headers"""        lines = content.split('\n')
        toc_items = []
        
        for line in lines:
            if line.startswith('## ') and not line.startswith('## Table of Contents'):
                header = line.replace('## ', '').strip()
                anchor = header.lower().replace(' ', '-').replace(':', '')
                toc_items.append(f"- [{header}](#{anchor})")
        
        return '\n'.join(toc_items)
    
    def _apply_seo_optimizations(self, content: str, content_data: Dict[str, Any]) -> str:
        """Apply SEO optimizations to blog content"""        # Add meta description as comment
        meta_description = content_data.get('meta_description', '')
        if not meta_description:
            # Generate from first paragraph
            first_paragraph = content.split('\n\n')[1] if '\n\n' in content else content[:160]
            meta_description = first_paragraph[:150] + '...'
        
        seo_content = f"<!-- Meta Description: {meta_description} -->\n\n{content}"
        
        # Add structured data markup comment
        seo_content += "\n\n<!-- Add structured data markup for better SEO -->"
        
        return seo_content
    
    def _get_default_blog_template(self) -> Dict[str, Any]:
        """Get default blog template"""        return {
            'structure': """# {title}

## Introduction

{intro}

## Main Content

{main_content}

## Conclusion

{conclusion}

## Call to Action

{call_to_action}""",
            'hooks': ['Welcome to this comprehensive guide on {topic}.']
        }
    
    def _create_basic_blog_post(self, content_data: Dict[str, Any]) -> str:
        """Create basic blog post when template fails"""        title = content_data.get('title', 'Blog Post')
        content = content_data.get('content', content_data.get('main_content', 'Great content here!'))
        
        return f"""# {title}

{content}

## Conclusion

Thanks for reading! Share your thoughts in the comments below.

---

*What did you think of this post? Let me know in the comments!*"""    
    def get_available_templates(self, category: str) -> List[str]:
        """Get available templates for category"""        try:
            category_templates = getattr(self, f"{category}_templates", {})
            return list(category_templates.keys())
        except:
            return []
    
    def get_all_categories(self) -> List[str]:
        """Get all template categories"""        return [
            'tutorial', 'list', 'thought_leadership', 'review', 
            'news', 'story', 'seo'
        ]
    
    def optimize_for_readability(self, content: str) -> str:
        """Optimize blog content for readability"""        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            # Add spacing around headers
            if line.startswith('#'):
                if optimized_lines and optimized_lines[-1].strip():
                    optimized_lines.append('')
                optimized_lines.append(line)
                optimized_lines.append('')
            # Break up long paragraphs
            elif len(line) > 300 and '.' in line:
                sentences = line.split('. ')
                mid_point = len(sentences) // 2
                optimized_lines.append('. '.join(sentences[:mid_point]) + '.')
                optimized_lines.append('')
                optimized_lines.append('. '.join(sentences[mid_point:]))
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def add_internal_linking_suggestions(self, content: str, related_topics: List[str]) -> str:
        """Add internal linking suggestions"""        if not related_topics:
            return content
        
        suggestions = "\n\n## Related Articles\n\n"
        for topic in related_topics[:5]:  # Limit to 5 suggestions
            suggestions += f"- [Learn more about {topic}](#{topic.lower().replace(' ', '-')})\n"
        
        return content + suggestions
    
    def generate_social_sharing_snippets(self, content: str, title: str) -> Dict[str, str]:
        """Generate social media sharing snippets from blog content"""        # Extract key points for social sharing
        first_paragraph = content.split('\n\n')[1] if '\n\n' in content else content[:200]
        
        snippets = {
            'twitter': f"📝 New blog post: {title}\n\n{first_paragraph[:200]}...\n\nRead more: [link] #blog #content",
            'linkedin': f"📖 I just published a new article: {title}\n\n{first_paragraph[:300]}...\n\nWhat are your thoughts on this topic? Share in the comments!\n\n#blog #article #content",
            'facebook': f"New blog post alert! 📚\n\n{title}\n\n{first_paragraph[:400]}...\n\nCheck it out and let me know what you think in the comments! 👇"
        }
        
        return snippets


class ArticleTemplate:
    """Article template class for blog post generation"""    
    def __init__(self, template_type: str = "standard", **kwargs):
        self.template_type = template_type
        self.title = kwargs.get('title', '')
        self.content_sections = kwargs.get('sections', [])
        self.metadata = kwargs.get('metadata', {})
    
    def render(self, data: Dict[str, Any]) -> str:
        """Render the article template with data"""        return f"# {data.get('title', 'Article Title')}\n\n{data.get('content', 'Article content goes here.')}"
    
    def get_structure(self) -> Dict[str, Any]:
        """Get the template structure"""        return {
            'sections': self.content_sections,
            'metadata': self.metadata
        }


class ArticleTemplate:
    """Article template for structured blog content"""    
    def __init__(self, **kwargs):
        self.title = kwargs.get('title', '')
        self.subtitle = kwargs.get('subtitle', '')
        self.content_sections = kwargs.get('sections', [])
        self.metadata = kwargs.get('metadata', {})
        self.category = kwargs.get('category', 'general')
        self.tags = kwargs.get('tags', [])
    
    def render(self, data: Dict[str, Any]) -> str:
        """Render the article template with data"""        title = data.get('title', self.title)
        content = data.get('content', 'Article content goes here.')
        return f"# {title}\n\n{content}"
    
    def get_structure(self) -> Dict[str, Any]:
        """Get the template structure"""        return {
            'title': self.title,
            'subtitle': self.subtitle,
            'sections': self.content_sections,
            'metadata': self.metadata,
            'category': self.category,
            'tags': self.tags
        }
