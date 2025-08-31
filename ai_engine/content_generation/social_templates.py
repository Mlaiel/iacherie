"""Social Media Templates - Professional template collection for social platforms

Comprehensive template system for creating high-quality social media content
across all major platforms with professional design patterns.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import random


class SocialMediaTemplates:
    """    Professional social media template collection providing:
    
    - Instagram post templates (feed, stories, reels)
    - Twitter/X thread templates  
    - LinkedIn post templates
    - TikTok caption templates
    - YouTube description templates
    - Facebook post templates
    - Platform-specific optimization
    - Engagement-driven content structures
    """    
    def __init__(self):
        """Initialize social media templates"""        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Instagram Templates
        self.instagram_templates = {
            'motivational_post': {
                'structure': "✨ {hook}\n\n{main_content}\n\n💪 {call_to_action}\n\n{hashtags}",
                'hooks': [
                    "Monday motivation coming your way!",
                    "Ready to transform your mindset?",
                    "Success starts with believing in yourself",
                    "Your potential is limitless"
                ],
                'ctas': [
                    "What's your Monday motivation? Share below! 👇",
                    "Double-tap if you needed this reminder! ❤️",
                    "Tag someone who needs to see this! 🙌",
                    "Save this for when you need motivation! 📌"
                ],
                'hashtags': "#motivation #mindset #success #mondaymotivation #inspiration #goals #hustle #entrepreneur #positivevibes #growth"
            },
            'behind_the_scenes': {
                'structure': "🎬 Behind the scenes: {title}\n\n{story}\n\n{insight}\n\n{engagement_question}\n\n{hashtags}",
                'hooks': [
                    "Ever wondered what goes on behind the scenes?",
                    "Here's what you don't see...",
                    "The real story behind",
                    "Pulling back the curtain on"
                ],
                'ctas': [
                    "What would you like to see more of? Comment below! 👇",
                    "Any questions about our process? Ask away! 💬",
                    "Share your behind-the-scenes moments! 📸"
                ],
                'hashtags': "#behindthescenes #process #reallife #authentic #transparent #journey #creation #work #team #storytelling"
            },
            'educational_carousel': {
                'structure': "📚 {topic}: {subtitle}\n\nSwipe to learn ➡️\n\n{preview}\n\n{save_cta}\n\n{hashtags}",
                'hooks': [
                    "5 things you need to know about",
                    "The ultimate guide to",
                    "Everything you should know about",
                    "Master the basics of"
                ],
                'ctas': [
                    "Save this post for later! 📌",
                    "Share with someone who needs this! 📲",
                    "Which tip resonated most with you? 💭"
                ],
                'hashtags': "#education #tips #learn #howto #guide #knowledge #skills #growth #tutorial #information"
            },
            'product_showcase': {
                'structure': "✨ {product_name}\n\n{benefits}\n\n{social_proof}\n\n{offer}\n\n{cta}\n\n{hashtags}",
                'hooks': [
                    "Introducing our latest",
                    "You asked, we delivered:",
                    "Game-changer alert:",
                    "This is exactly what you need:"
                ],
                'ctas': [
                    "Link in bio to shop now! 🛒",
                    "DM us for more details! 💌",
                    "Tag someone who needs this! 🏷️",
                    "Comment 'WANT' for direct link! 💬"
                ],
                'hashtags': "#product #new #launch #shop #quality #innovation #musthave #lifestyle #brand #shopping"
            }
        }
        
        # Twitter/X Templates
        self.twitter_templates = {
            'thread_starter': {
                'structure': "🧵 {hook}\n\nA thread on {topic} (1/{count})",
                'hooks': [
                    "Controversial opinion:",
                    "Things I wish I knew about",
                    "The harsh truth about",
                    "Quick thoughts on",
                    "Unpopular opinion about",
                    "What I learned from"
                ]
            },
            'quote_tweet': {
                'structure': "💭 {reaction}\n\n{additional_insight}\n\n{question}",
                'reactions': [
                    "This hits different.",
                    "Absolutely this.",
                    "Important thread.",
                    "Worth reading.",
                    "Spot on analysis."
                ]
            },
            'hot_take': {
                'structure': "🔥 Hot take:\n\n{opinion}\n\n{reasoning}\n\nThoughts?",
                'starters': [
                    "Hot take:",
                    "Unpopular opinion:",
                    "Controversial but true:",
                    "Let's talk about",
                    "Real talk:"
                ]
            }
        }
        
        # LinkedIn Templates
        self.linkedin_templates = {
            'professional_insight': {
                'structure': "💼 {professional_hook}\n\n{situation}\n\n{insight}\n\n{application}\n\n{question}\n\n{hashtags}",
                'hooks': [
                    "Here's what 10 years in the industry taught me:",
                    "A lesson from today's client meeting:",
                    "Industry insight that changed my perspective:",
                    "What successful leaders do differently:"
                ],
                'ctas': [
                    "What's your experience with this?",
                    "How do you handle similar situations?",
                    "What would you add to this list?",
                    "Agree or disagree? Share your thoughts."
                ],
                'hashtags': "#leadership #business #strategy #professional #industry #insights #growth #success #management #career"
            },
            'company_update': {
                'structure': "🚀 {announcement}\n\n{details}\n\n{impact}\n\n{gratitude}\n\n{future_outlook}\n\n{hashtags}",
                'starters': [
                    "Exciting company news:",
                    "Proud to announce:",
                    "Major milestone achieved:",
                    "Team update:"
                ],
                'hashtags': "#companyupdate #growth #team #milestone #achievement #business #success #announcement #proud #grateful"
            },
            'thought_leadership': {
                'structure': "🎯 {industry_trend}\n\n{analysis}\n\n{prediction}\n\n{actionable_advice}\n\n{engagement_question}\n\n{hashtags}",
                'starters': [
                    "The industry is shifting toward",
                    "Here's what I'm seeing in the market:",
                    "Future of our industry:",
                    "Emerging trend to watch:"
                ],
                'hashtags': "#thoughtleadership #industry #trends #future #innovation #strategy #insights #analysis #expert #opinion"
            }
        }
        
        # TikTok Templates
        self.tiktok_templates = {
            'trend_participation': {
                'structure': "🎵 {trend_reference}\n\n{your_take}\n\n{hashtags}",
                'starters': [
                    "POV:",
                    "Tell me you're a [profession] without telling me",
                    "This trend but make it",
                    "When you finally understand"
                ],
                'hashtags': "#fyp #trending #viral #relatable #mood #aesthetic #vibes #content #creator #fun"
            },
            'educational_content': {
                'structure': "📚 {fact_hook}\n\n{explanation}\n\n{mind_blown_element}\n\n{hashtags}",
                'hooks': [
                    "Fun fact:",
                    "Did you know:",
                    "Science says:",
                    "Plot twist:",
                    "Mind = blown:"
                ],
                'hashtags': "#learn #facts #education #mindblown #interesting #knowledge #science #cool #amazing #wow"
            },
            'lifestyle_content': {
                'structure': "✨ {lifestyle_moment}\n\n{relatability}\n\n{aesthetic_element}\n\n{hashtags}",
                'starters': [
                    "That girl energy:",
                    "Main character moment:",
                    "Living my best life:",
                    "Aesthetic vibes:"
                ],
                'hashtags': "#lifestyle #aesthetic #vibes #mood #energy #selfcare #goodvibes #life #moments #happiness"
            }
        }
        
        # YouTube Templates
        self.youtube_templates = {
            'tutorial_description': {
                'structure': "🎓 {tutorial_title}\n\n{overview}\n\n📚 TIMESTAMPS:\n{timestamps}\n\n🔔 {subscribe_cta}\n\n📱 CONNECT:\n{social_links}\n\n{hashtags}",
                'timestamps_example': "0:00 Introduction\n2:30 Step 1\n5:45 Step 2\n8:20 Step 3\n12:00 Conclusion",
                'hashtags': "#tutorial #howto #learn #education #guide #tips #stepbystep #helpful #youtube #content"
            },
            'vlog_description': {
                'structure': "📹 {vlog_title}\n\n{day_summary}\n\n{highlights}\n\n{personal_note}\n\n{engagement_cta}\n\n{social_links}\n\n{hashtags}",
                'engagement_ctas': [
                    "What was your favorite part? Let me know!",
                    "How was your day? Tell me in the comments!",
                    "What should I vlog next?",
                    "Thanks for coming along with me today!"
                ],
                'hashtags': "#vlog #dayinmylife #lifestyle #personal #authentic #reallife #daily #journey #life #sharing"
            }
        }
        
        # Facebook Templates
        self.facebook_templates = {
            'community_post': {
                'structure': "{greeting}\n\n{main_content}\n\n{community_question}\n\n{engagement_elements}",
                'greetings': [
                    "Good morning, amazing community!",
                    "Hello, wonderful people!",
                    "Hey there, Facebook family!",
                    "Happy [day], everyone!"
                ],
                'engagement_elements': [
                    "React with ❤️ if you agree!",
                    "Share your thoughts below!",
                    "Tag someone who needs to see this!",
                    "Save this post for later!"
                ]
            },
            'event_promotion': {
                'structure': "🎉 {event_announcement}\n\n📅 {date_time}\n📍 {location}\n\n{event_details}\n\n{registration_cta}\n\n{excitement_builder}",
                'excitement_builders': [
                    "Can't wait to see you there!",
                    "This is going to be amazing!",
                    "You won't want to miss this!",
                    "Limited spots available!"
                ]
            }
        }
    
    def get_template(
        self, 
        platform: str, 
        template_type: str, 
        content_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Get template for specific platform and type.
        
        Args:
            platform: Social media platform (instagram, twitter, linkedin, etc.)
            template_type: Type of template (motivational_post, thread_starter, etc.)
            content_data: Data to fill template placeholders
            
        Returns:
            Template structure and content
        """        try:
            platform_templates = getattr(self, f"{platform}_templates", {})
            template = platform_templates.get(template_type, {})
            
            if not template:
                self.logger.warning(f"Template not found: {platform}.{template_type}")
                return self._get_default_template(platform)
            
            return template
            
        except Exception as e:
            self.logger.error(f"Error getting template: {str(e)}")
            return self._get_default_template(platform)
    
    def fill_template(
        self,
        platform: str,
        template_type: str,
        content_data: Dict[str, Any]
    ) -> str:
        """        Fill template with content data.
        
        Args:
            platform: Social media platform
            template_type: Type of template
            content_data: Data to fill template
            
        Returns:
            Filled template content
        """        try:
            template = self.get_template(platform, template_type, content_data)
            
            if not template:
                return self._create_basic_content(content_data)
            
            structure = template.get('structure', '')
            
            # Fill basic placeholders
            filled_content = self._fill_basic_placeholders(structure, content_data, template)
            
            return filled_content
            
        except Exception as e:
            self.logger.error(f"Error filling template: {str(e)}")
            return self._create_basic_content(content_data)
    
    def _fill_basic_placeholders(
        self, 
        structure: str, 
        content_data: Dict[str, Any], 
        template: Dict[str, Any]
    ) -> str:
        """Fill basic placeholders in template structure"""        filled = structure
        
        # Fill direct data mappings
        for key, value in content_data.items():
            placeholder = f"{{{key}}}"
            if placeholder in filled:
                filled = filled.replace(placeholder, str(value))
        
        # Fill template-specific elements
        filled = self._fill_hooks(filled, template)
        filled = self._fill_ctas(filled, template)
        filled = self._fill_hashtags(filled, template)
        filled = self._fill_dynamic_elements(filled, template, content_data)
        
        return filled
    
    def _fill_hooks(self, content: str, template: Dict[str, Any]) -> str:
        """Fill hook placeholders"""        if '{hook}' in content:
            hooks = template.get('hooks', ['Great content coming your way!'])
            selected_hook = random.choice(hooks)
            content = content.replace('{hook}', selected_hook)
        
        if '{professional_hook}' in content:
            hooks = template.get('hooks', ['Professional insight:'])
            selected_hook = random.choice(hooks)
            content = content.replace('{professional_hook}', selected_hook)
        
        return content
    
    def _fill_ctas(self, content: str, template: Dict[str, Any]) -> str:
        """Fill call-to-action placeholders"""        cta_placeholders = ['{call_to_action}', '{cta}', '{engagement_question}', '{question}']
        
        for placeholder in cta_placeholders:
            if placeholder in content:
                ctas = template.get('ctas', ['Share your thoughts below!'])
                selected_cta = random.choice(ctas)
                content = content.replace(placeholder, selected_cta)
        
        return content
    
    def _fill_hashtags(self, content: str, template: Dict[str, Any]) -> str:
        """Fill hashtag placeholders"""        if '{hashtags}' in content:
            hashtags = template.get('hashtags', '#content #social #media')
            content = content.replace('{hashtags}', hashtags)
        
        return content
    
    def _fill_dynamic_elements(
        self, 
        content: str, 
        template: Dict[str, Any], 
        content_data: Dict[str, Any]
    ) -> str:
        """Fill dynamic elements based on content type"""        # Fill timestamps for YouTube
        if '{timestamps}' in content:
            timestamps = template.get('timestamps_example', '0:00 Introduction')
            content = content.replace('{timestamps}', timestamps)
        
        # Fill social links
        if '{social_links}' in content:
            social_links = "• Instagram: @youraccount\n• Twitter: @youraccount\n• Website: yourwebsite.com"
            content = content.replace('{social_links}', social_links)
        
        # Fill subscribe CTA
        if '{subscribe_cta}' in content:
            subscribe_cta = "SUBSCRIBE for more content like this! Hit the bell icon for notifications! 🔔"
            content = content.replace('{subscribe_cta}', subscribe_cta)
        
        # Fill engagement elements
        if '{engagement_elements}' in content:
            elements = template.get('engagement_elements', ['Share your thoughts!'])
            selected_element = random.choice(elements)
            content = content.replace('{engagement_elements}', selected_element)
        
        return content
    
    def _get_default_template(self, platform: str) -> Dict[str, Any]:
        """Get default template for platform"""        default_templates = {
            'instagram': {
                'structure': "{main_content}\n\n{call_to_action}\n\n#content #social #instagram",
                'ctas': ['Share your thoughts below! 👇']
            },
            'twitter': {
                'structure': "{main_content}\n\nThoughts? 🤔",
                'ctas': ['What do you think?']
            },
            'linkedin': {
                'structure': "{main_content}\n\nWhat's your experience with this?\n\n#professional #business",
                'ctas': ['Share your insights below.']
            },
            'tiktok': {
                'structure': "{main_content} ✨\n\n#fyp #content #viral",
                'ctas': ['Comment below! 💬']
            },
            'youtube': {
                'structure': "{main_content}\n\n🔔 Subscribe for more!\n\n#youtube #content",
                'ctas': ['Let me know in the comments!']
            },
            'facebook': {
                'structure': "{main_content}\n\nWhat are your thoughts? Share below!",
                'ctas': ['Love to hear from you!']
            }
        }
        
        return default_templates.get(platform, {
            'structure': "{main_content}",
            'ctas': ['Thanks for reading!']
        })
    
    def _create_basic_content(self, content_data: Dict[str, Any]) -> str:
        """Create basic content when template fails"""        main_content = content_data.get('main_content', '')
        if not main_content:
            main_content = content_data.get('content', '')
        if not main_content:
            main_content = content_data.get('text', 'Great content!')
        
        return f"{main_content}\n\nThanks for reading! 👍"
    
    def get_available_templates(self, platform: str) -> List[str]:
        """Get list of available templates for platform"""        try:
            platform_templates = getattr(self, f"{platform}_templates", {})
            return list(platform_templates.keys())
        except:
            return []
    
    def get_all_platforms(self) -> List[str]:
        """Get list of all supported platforms"""        return ['instagram', 'twitter', 'linkedin', 'tiktok', 'youtube', 'facebook']
    
    def customize_template(
        self,
        platform: str,
        template_type: str,
        customizations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Customize existing template with user preferences.
        
        Args:
            platform: Social media platform
            template_type: Type of template
            customizations: Custom hooks, CTAs, hashtags, etc.
            
        Returns:
            Customized template
        """        try:
            template = self.get_template(platform, template_type).copy()
            
            # Apply customizations
            if 'hooks' in customizations:
                template['hooks'] = customizations['hooks']
            
            if 'ctas' in customizations:
                template['ctas'] = customizations['ctas']
            
            if 'hashtags' in customizations:
                template['hashtags'] = customizations['hashtags']
            
            if 'structure' in customizations:
                template['structure'] = customizations['structure']
            
            return template
            
        except Exception as e:
            self.logger.error(f"Error customizing template: {str(e)}")
            return self.get_template(platform, template_type)
    
    def generate_hashtag_suggestions(
        self, 
        content: str, 
        platform: str, 
        max_hashtags: int = 10
    ) -> List[str]:
        """Generate hashtag suggestions based on content"""        content_lower = content.lower()
        
        # Platform-specific hashtag pools
        hashtag_pools = {
            'instagram': {
                'business': ['#business', '#entrepreneur', '#success', '#motivation', '#hustle'],
                'lifestyle': ['#lifestyle', '#aesthetic', '#vibes', '#mood', '#selfcare'],
                'tech': ['#technology', '#innovation', '#digital', '#tech', '#startup'],
                'fitness': ['#fitness', '#health', '#workout', '#gym', '#wellness'],
                'food': ['#food', '#cooking', '#recipe', '#delicious', '#foodie']
            },
            'linkedin': {
                'business': ['#leadership', '#business', '#strategy', '#professional', '#growth'],
                'career': ['#career', '#jobsearch', '#networking', '#skills', '#development'],
                'tech': ['#technology', '#innovation', '#digital', '#transformation', '#ai'],
                'marketing': ['#marketing', '#branding', '#content', '#socialmedia', '#advertising']
            },
            'twitter': {
                'general': ['#TwitterTips', '#SocialMedia', '#Content', '#Engagement'],
                'tech': ['#TechNews', '#Innovation', '#Digital', '#Startup', '#AI'],
                'business': ['#Business', '#Entrepreneur', '#Success', '#Growth']
            }
        }
        
        platform_hashtags = hashtag_pools.get(platform, hashtag_pools['instagram'])
        suggestions = []
        
        # Analyze content and suggest relevant hashtags
        for category, hashtags in platform_hashtags.items():
            category_keywords = {
                'business': ['business', 'entrepreneur', 'success', 'company', 'startup'],
                'lifestyle': ['life', 'style', 'daily', 'personal', 'wellness'],
                'tech': ['technology', 'digital', 'innovation', 'tech', 'ai'],
                'fitness': ['fitness', 'health', 'workout', 'exercise', 'gym'],
                'food': ['food', 'recipe', 'cooking', 'meal', 'delicious'],
                'career': ['career', 'job', 'work', 'professional', 'skill'],
                'marketing': ['marketing', 'brand', 'content', 'social', 'advertising']
            }
            
            if any(keyword in content_lower for keyword in category_keywords.get(category, [])):
                suggestions.extend(hashtags[:3])  # Add top 3 from each relevant category
        
        # Add generic platform hashtags if needed
        if len(suggestions) < max_hashtags:
            generic_hashtags = ['#content', '#social', '#media', '#engagement', '#community']
            suggestions.extend(generic_hashtags)
        
        return suggestions[:max_hashtags]


class TemplateEngine:
    """Template engine for social media content"""    
    def __init__(self):
        self.variables = {}
    
    def substitute_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """Substitute variables in template"""        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result
    
    def apply_conditional_logic(self, template: str, conditions: Dict[str, bool]) -> str:
        """Apply conditional logic to template"""        return template  # Simplified implementation


class InstagramTemplate:
    """Instagram-specific template class"""    
    def __init__(self, template_type: str = "post", **kwargs):
        self.template_type = template_type
        self.content = kwargs.get('content', '')
        self.hashtags = kwargs.get('hashtags', [])
        self.character_limit = 2200
    
    def render(self, data: Dict[str, Any]) -> str:
        """Render Instagram template with data"""        content = data.get('content', self.content)
        hashtags = ' '.join(data.get('hashtags', self.hashtags))
        return f"{content}\n\n{hashtags}"
    
    def validate_length(self, content: str) -> bool:
        """Validate content length for Instagram"""        return len(content) <= self.character_limit


class TemplateEngine:
    """Template rendering engine for social media content"""    
    def __init__(self):
        self.templates = {}
        self.variables = {}
    
    def register_template(self, name: str, template: str) -> None:
        """Register a new template"""        self.templates[name] = template
    
    def render_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """Render template with variables"""        template = self.templates.get(template_name, "")
        return template.format(**variables)
    
    def set_variable(self, key: str, value: Any) -> None:
        """Set a template variable"""        self.variables[key] = value
    
    def process_conditionals(self, template: str, conditions: Dict[str, bool]) -> str:
        """Process conditional logic in templates"""        # Simplified conditional processing
        for condition, value in conditions.items():
            if value:
                template = template.replace(f"{{if {condition}}}", "")
                template = template.replace(f"{{endif {condition}}}", "")
            else:
                # Remove conditional blocks
                start = template.find(f"{{if {condition}}}")
                end = template.find(f"{{endif {condition}}}")
                if start != -1 and end != -1:
                    template = template[:start] + template[end + len(f"{{endif {condition}}}"):]
        return template
