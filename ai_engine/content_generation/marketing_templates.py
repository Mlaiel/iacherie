"""Marketing Templates - Professional marketing content templates

Comprehensive template system for creating high-converting marketing content
across different channels and campaign types.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import random


class MarketingTemplates:
    """    Professional marketing template collection providing:
    
    - Email marketing campaigns
    - Sales page templates
    - Landing page copy
    - Ad copy templates
    - Product launch templates
    - Lead magnet templates
    - Newsletter templates
    - Conversion-optimized structures
    """    
    def __init__(self):
        """Initialize marketing templates"""        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Email Marketing Templates
        self.email_templates = {
            'welcome_series': {
                'structure': """Subject: Welcome to {brand_name}! Here's what's next 👋

Hi {first_name},

{personal_welcome}

{value_proposition}

## What You Can Expect

{expectations}

## Your Next Step

{next_action}

## Quick Favor

{engagement_request}

Best regards,
{sender_name}
{brand_name}

P.S. {ps_message}

---
{unsubscribe_footer}""",
                'welcomes': [
                    "Welcome to our community! I'm thrilled you've joined us.",
                    "You just made an amazing decision by joining {brand_name}!",
                    "Welcome aboard! Get ready for some incredible content.",
                    "So excited to have you as part of our family!"
                ]
            },
            'sales_email': {
                'structure': """Subject: {urgency_subject}

Hi {first_name},

{personalized_opener}

{problem_agitation}

{solution_introduction}

## Here's What You Get:

{benefits_list}

{social_proof}

{offer_details}

{urgency_element}

{call_to_action}

Questions? Just reply to this email.

{sender_signature}

P.S. {ps_offer}""",
                'urgency_subjects': [
                    "Only {hours} hours left",
                    "{offer} ends tonight",
                    "Last chance for {benefit}",
                    "Don't miss out on {value}"
                ]
            },
            'newsletter': {
                'structure': """Subject: {newsletter_title} - {main_topic}

Hi {first_name},

{greeting}

## This Week's Highlights

{content_summary}

## Featured Article

{featured_content}

## Quick Tips

{tips_section}

## Community Spotlight

{community_content}

## What's Coming Next

{upcoming_content}

{newsletter_footer}""",
                'greetings': [
                    "Hope you're having an amazing week!",
                    "Ready for this week's insights?",
                    "Another week, another dose of valuable content!",
                    "Time for your weekly dose of inspiration!"
                ]
            }
        }
        
        # Sales Page Templates
        self.sales_templates = {
            'product_launch': {
                'structure': """# {product_name}: {headline}

## The Problem

{problem_description}

{pain_points}

## The Solution

{solution_overview}

## Introducing {product_name}

{product_description}

## How It Works

{process_steps}

## What You Get

{features_benefits}

## Social Proof

{testimonials}

{case_studies}

## Pricing

{pricing_section}

{guarantee}

## FAQ

{faq_section}

## Don't Wait

{urgency_section}

{final_cta}""",
                'headlines': [
                    "Finally, A Solution That Actually Works",
                    "The {category} Tool You've Been Waiting For",
                    "Transform Your {area} in {timeframe}",
                    "The Secret to {desired_outcome}"
                ]
            },
            'service_page': {
                'structure': """# {service_name}: {value_proposition}

## Are You Struggling With {problem}?

{problem_elaboration}

## How We Help

{solution_overview}

## Our Process

{methodology}

## What's Included

{service_details}

## Success Stories

{client_results}

## Investment

{pricing_philosophy}

{pricing_options}

## Ready to Get Started?

{application_process}

{contact_cta}""",
                'value_propositions': [
                    "Get {result} Without {pain_point}",
                    "The {superlative} {service_type} Service",
                    "Achieve {goal} in {timeframe}",
                    "Professional {service} That Delivers"
                ]
            }
        }
        
        # Landing Page Templates
        self.landing_templates = {
            'lead_magnet': {
                'structure': """# Get Your Free {lead_magnet_name}

## {hook_headline}

{hook_description}

## What You'll Get:

{benefits_list}

## Who This Is For:

{target_audience}

## Download Your Free {lead_magnet_name} Now

{opt_in_form}

{trust_signals}

## What Others Are Saying:

{testimonials}

{privacy_assurance}""",
                'hooks': [
                    "The {category} Guide That Changed Everything",
                    "Discover the {secret} Top {professionals} Use",
                    "Get the {resource} That {benefit}",
                    "Free {timeframe} {category} Crash Course"
                ]
            },
            'webinar_registration': {
                'structure': """# Free Training: {webinar_title}

## {urgency_headline}

{training_description}

## In This Training You'll Discover:

{learning_outcomes}

## About Your Host

{host_bio}

{host_credentials}

## Register Now - It's Free!

{registration_form}

## When: {webinar_date}

{time_details}

{replay_availability}

{final_cta}""",
                'urgency_headlines': [
                    "Limited Seats Available - Register Now",
                    "This Week Only: Free {topic} Masterclass",
                    "Join {number}+ People Learning {skill}",
                    "Last Chance to Register for {event}"
                ]
            }
        }
        
        # Ad Copy Templates
        self.ad_templates = {
            'facebook_ad': {
                'structure': """{hook}

{problem_statement}

{solution_introduction}

{benefits}

{social_proof}

{call_to_action}

{hashtags}""",
                'hooks': [
                    "Stop scrolling! This is for you if...",
                    "Attention {target_audience}:",
                    "Finally! A solution to {problem}",
                    "This changed everything for {customer_type}"
                ]
            },
            'google_ad': {
                'structure': """Headline 1: {headline_1}
Headline 2: {headline_2}
Headline 3: {headline_3}

Description 1: {description_1}
Description 2: {description_2}

Display URL: {display_url}
Final URL: {final_url}""",
                'headline_formulas': [
                    "{Benefit} in {Timeframe}",
                    "Get {Result} Today",
                    "{Number}% More {Benefit}",
                    "Free {Lead_Magnet}"
                ]
            }
        }
        
        # Product Launch Templates
        self.launch_templates = {
            'pre_launch': {
                'structure': """# Something Big Is Coming...

## The Announcement

{teaser_content}

## What We're Building

{product_preview}

{problem_solving}

## Why Now?

{timing_explanation}

## Early Bird List

{early_access_offer}

{sign_up_cta}

## Stay Tuned

{communication_plan}""",
                'teasers': [
                    "We've been working on something special...",
                    "The solution you've been asking for is almost here",
                    "Big announcement coming {date}",
                    "This will change how you {action}"
                ]
            },
            'launch_day': {
                'structure': """# It's Here! Introducing {product_name}

## The Wait Is Over

{launch_announcement}

{excitement_builder}

## What {product_name} Does

{product_overview}

{key_benefits}

## Launch Special

{launch_offer}

{urgency_element}

## Get Started Now

{purchase_cta}

{guarantee}

## Thank You

{gratitude_message}""",
                'announcements': [
                    "Today marks a special day for our community",
                    "We're officially launching {product_name}!",
                    "The product you've been waiting for is here",
                    "Launch day is finally here!"
                ]
            }
        }
        
        # Conversion optimization elements
        self.conversion_elements = {
            'urgency_triggers': [
                "Limited time offer",
                "Only {quantity} left",
                "Offer expires in {time}",
                "Early bird pricing ends soon",
                "Last chance",
                "Don't miss out"
            ],
            'trust_signals': [
                "30-day money-back guarantee",
                "Used by {number}+ customers",
                "Featured in {publication}",
                "{rating}-star rated",
                "SSL secured checkout",
                "No spam, unsubscribe anytime"
            ],
            'social_proof_types': [
                "Customer testimonials",
                "Case studies",
                "Usage statistics",
                "Media mentions",
                "Expert endorsements",
                "Customer logos"
            ]
        }
    
    def get_template(
        self, 
        template_category: str, 
        template_type: str,
        content_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Get marketing template for specific category and type.
        
        Args:
            template_category: Category (email, sales, landing, ad, launch)
            template_type: Specific template type
            content_data: Data to customize template
            
        Returns:
            Template structure and metadata
        """        try:
            category_templates = getattr(self, f"{template_category}_templates", {})
            template = category_templates.get(template_type, {})
            
            if not template:
                self.logger.warning(f"Template not found: {template_category}.{template_type}")
                return self._get_default_marketing_template(template_category)
            
            return template
            
        except Exception as e:
            self.logger.error(f"Error getting template: {str(e)}")
            return self._get_default_marketing_template(template_category)
    
    def fill_template(
        self,
        template_category: str,
        template_type: str,
        content_data: Dict[str, Any]
    ) -> str:
        """        Fill marketing template with content data.
        
        Args:
            template_category: Template category
            template_type: Template type
            content_data: Data to fill template
            
        Returns:
            Complete marketing content
        """        try:
            template = self.get_template(template_category, template_type, content_data)
            
            if not template:
                return self._create_basic_marketing_content(content_data)
            
            structure = template.get('structure', '')
            
            # Fill template with marketing-specific optimizations
            filled_content = self._fill_marketing_placeholders(structure, content_data, template)
            
            # Apply conversion optimizations
            filled_content = self._apply_conversion_optimizations(filled_content, content_data)
            
            return filled_content
            
        except Exception as e:
            self.logger.error(f"Error filling template: {str(e)}")
            return self._create_basic_marketing_content(content_data)
    
    def _fill_marketing_placeholders(
        self, 
        structure: str, 
        content_data: Dict[str, Any], 
        template: Dict[str, Any]
    ) -> str:
        """Fill placeholders in marketing template"""        filled = structure
        
        # Fill direct data mappings
        for key, value in content_data.items():
            placeholder = f"{{{key}}}"
            if placeholder in filled:
                filled = filled.replace(placeholder, str(value))
        
        # Fill marketing-specific elements
        filled = self._fill_marketing_hooks(filled, template, content_data)
        filled = self._fill_benefits_lists(filled, content_data)
        filled = self._fill_social_proof(filled, content_data)
        filled = self._fill_urgency_elements(filled, content_data)
        filled = self._fill_ctas(filled, content_data)
        
        return filled
    
    def _fill_marketing_hooks(self, content: str, template: Dict[str, Any], content_data: Dict[str, Any]) -> str:
        """Fill marketing hook placeholders"""        # Fill welcome messages
        if '{personal_welcome}' in content:
            welcomes = template.get('welcomes', ['Welcome to our community!'])
            selected_welcome = random.choice(welcomes)
            brand_name = content_data.get('brand_name', 'our brand')
            selected_welcome = selected_welcome.replace('{brand_name}', brand_name)
            content = content.replace('{personal_welcome}', selected_welcome)
        
        # Fill hook headlines
        if '{hook_headline}' in content:
            hooks = template.get('hooks', ['Amazing content inside!'])
            selected_hook = random.choice(hooks)
            # Fill hook variables
            for key, value in content_data.items():
                selected_hook = selected_hook.replace(f'{{{key}}}', str(value))
            content = content.replace('{hook_headline}', selected_hook)
        
        # Fill urgency headlines
        if '{urgency_headline}' in content:
            urgency_headlines = template.get('urgency_headlines', ['Act now!'])
            selected_headline = random.choice(urgency_headlines)
            content = content.replace('{urgency_headline}', selected_headline)
        
        return content
    
    def _fill_benefits_lists(self, content: str, content_data: Dict[str, Any]) -> str:
        """Fill benefits and features lists"""        # Fill benefits list
        if '{benefits_list}' in content:
            benefits = content_data.get('benefits', [])
            if benefits:
                benefits_formatted = '\n'.join([f"✅ {benefit}" for benefit in benefits])
                content = content.replace('{benefits_list}', benefits_formatted)
        
        # Fill features benefits
        if '{features_benefits}' in content:
            features = content_data.get('features', [])
            if features:
                features_formatted = '\n'.join([
                    f"### {feature.get('name', '')}\n{feature.get('benefit', '')}\n" 
                    for feature in features
                ])
                content = content.replace('{features_benefits}', features_formatted)
        
        # Fill learning outcomes
        if '{learning_outcomes}' in content:
            outcomes = content_data.get('learning_outcomes', [])
            if outcomes:
                outcomes_formatted = '\n'.join([f"✓ {outcome}" for outcome in outcomes])
                content = content.replace('{learning_outcomes}', outcomes_formatted)
        
        return content
    
    def _fill_social_proof(self, content: str, content_data: Dict[str, Any]) -> str:
        """Fill social proof elements"""        # Fill testimonials
        if '{testimonials}' in content:
            testimonials = content_data.get('testimonials', [])
            if testimonials:
                testimonials_formatted = '\n'.join([
                    f'> "{testimonial.get("quote", "")}" - {testimonial.get("author", "Customer")}'
                    for testimonial in testimonials
                ])
                content = content.replace('{testimonials}', testimonials_formatted)
        
        # Fill case studies
        if '{case_studies}' in content:
            case_studies = content_data.get('case_studies', [])
            if case_studies:
                studies_formatted = '\n'.join([
                    f"**{study.get('title', '')}**: {study.get('result', '')}"
                    for study in case_studies
                ])
                content = content.replace('{case_studies}', studies_formatted)
        
        # Fill trust signals
        if '{trust_signals}' in content:
            trust_signals = self.conversion_elements['trust_signals'][:3]
            signals_formatted = '\n'.join([f"🔒 {signal}" for signal in trust_signals])
            content = content.replace('{trust_signals}', signals_formatted)
        
        return content
    
    def _fill_urgency_elements(self, content: str, content_data: Dict[str, Any]) -> str:
        """Fill urgency and scarcity elements"""        # Fill urgency element
        if '{urgency_element}' in content:
            urgency_triggers = self.conversion_elements['urgency_triggers']
            selected_urgency = random.choice(urgency_triggers)
            
            # Customize with data
            if '{time}' in selected_urgency:
                time_limit = content_data.get('time_limit', '24 hours')
                selected_urgency = selected_urgency.replace('{time}', time_limit)
            if '{quantity}' in selected_urgency:
                quantity = content_data.get('quantity', '50')
                selected_urgency = selected_urgency.replace('{quantity}', quantity)
            
            content = content.replace('{urgency_element}', f"⏰ {selected_urgency}")
        
        # Fill urgency section
        if '{urgency_section}' in content:
            urgency_section = f"""## ⏰ Limited Time Offer

{content_data.get('urgency_reason', 'This special pricing won\'t last long.')}

{content_data.get('consequence', 'Don\'t miss your chance to save.')}"""            content = content.replace('{urgency_section}', urgency_section)
        
        return content
    
    def _fill_ctas(self, content: str, content_data: Dict[str, Any]) -> str:
        """Fill call-to-action elements"""        # Fill main CTA
        if '{call_to_action}' in content:
            cta_text = content_data.get('cta_text', 'Get Started Now')
            cta_url = content_data.get('cta_url', '#')
            cta = f"[{cta_text}]({cta_url}) 👈 Click here!"
            content = content.replace('{call_to_action}', cta)
        
        # Fill purchase CTA
        if '{purchase_cta}' in content:
            product_name = content_data.get('product_name', 'this product')
            cta = f"🛒 **[Get {product_name} Now]({content_data.get('purchase_url', '#')})**"
            content = content.replace('{purchase_cta}', cta)
        
        # Fill sign up CTA
        if '{sign_up_cta}' in content:
            cta = f"📧 **[Join the Early Bird List]({content_data.get('signup_url', '#')})**"
            content = content.replace('{sign_up_cta}', cta)
        
        return content
    
    def _apply_conversion_optimizations(self, content: str, content_data: Dict[str, Any]) -> str:
        """Apply conversion rate optimization techniques"""        # Add guarantee if not present
        if '{guarantee}' in content:
            guarantee_text = content_data.get('guarantee', '30-day money-back guarantee')
            guarantee = f"🛡️ **{guarantee_text}** - Risk-free purchase!"
            content = content.replace('{guarantee}', guarantee)
        
        # Add pricing section
        if '{pricing_section}' in content:
            price = content_data.get('price', '$97')
            original_price = content_data.get('original_price', '$197')
            pricing = f"""### Special Launch Price: ~~{original_price}~~ **{price}**

Save {int(original_price.replace('$', '')) - int(price.replace('$', ''))}$ today only!"""            content = content.replace('{pricing_section}', pricing)
        
        # Add FAQ section
        if '{faq_section}' in content:
            faqs = content_data.get('faqs', [
                {'q': 'How quickly will I see results?', 'a': 'Most customers see results within the first week.'},
                {'q': 'Is there a guarantee?', 'a': 'Yes! 30-day money-back guarantee.'},
                {'q': 'Do I need any special skills?', 'a': 'No experience required - we guide you step by step.'}
            ])
            faq_formatted = '\n'.join([
                f"**Q: {faq['q']}**\nA: {faq['a']}\n"
                for faq in faqs
            ])
            content = content.replace('{faq_section}', faq_formatted)
        
        return content
    
    def _get_default_marketing_template(self, category: str) -> Dict[str, Any]:
        """Get default template for marketing category"""        default_templates = {
            'email': {
                'structure': """Subject: {subject}

Hi {first_name},

{message}

{call_to_action}

Best regards,
{sender_name}""",
            },
            'sales': {
                'structure': """# {headline}

## The Problem
{problem}

## The Solution
{solution}

## Get Started
{call_to_action}""",
            },
            'landing': {
                'structure': """# {headline}

{description}

## Benefits:
{benefits}

{call_to_action}""",
            },
            'ad': {
                'structure': """{hook}

{benefits}

{call_to_action}""",
            }
        }
        
        return default_templates.get(category, {
            'structure': "{content}\n\n{call_to_action}"
        })
    
    def _create_basic_marketing_content(self, content_data: Dict[str, Any]) -> str:
        """Create basic marketing content when template fails"""        headline = content_data.get('headline', content_data.get('title', 'Amazing Offer'))
        content = content_data.get('content', content_data.get('message', 'Great value inside!'))
        cta = content_data.get('cta_text', 'Get Started Now')
        
        return f"""# {headline}

{content}

## Ready to Get Started?

**[{cta}](#{cta.lower().replace(' ', '-')})**

---

*Questions? Just reach out - we're here to help!*"""    
    def optimize_for_conversion(self, content: str, optimization_type: str = 'general') -> str:
        """Apply conversion rate optimization to marketing content"""        optimizations = {
            'urgency': [
                'Limited time offer',
                'Only available today',
                'Last chance'
            ],
            'scarcity': [
                'Limited quantity available',
                'Only 50 spots left',
                'Exclusive access'
            ],
            'social_proof': [
                'Join 10,000+ satisfied customers',
                'Trusted by industry leaders',
                '5-star rated'
            ],
            'risk_reversal': [
                '30-day money-back guarantee',
                'No risk, all reward',
                'Try risk-free'
            ]
        }
        
        if optimization_type in optimizations:
            optimization_text = random.choice(optimizations[optimization_type])
            content += f"\n\n🎯 **{optimization_text}**"
        
        return content
    
    def generate_subject_lines(self, content_type: str, data: Dict[str, Any]) -> List[str]:
        """Generate email subject line variations"""        subject_formulas = {
            'sales': [
                "{benefit} in just {timeframe}",
                "Your {desired_outcome} is waiting",
                "Last chance: {offer}",
                "{urgency}: {benefit}"
            ],
            'newsletter': [
                "{week_number}: {main_topic}",
                "Inside: {featured_content}",
                "This week: {highlights}",
                "{brand_name} Weekly: {topic}"
            ],
            'welcome': [
                "Welcome to {brand_name}! Here's what's next",
                "You're in! Let's get started",
                "Welcome aboard, {first_name}!",
                "Your {brand_name} journey begins now"
            ]
        }
        
        formulas = subject_formulas.get(content_type, ["Important update from {brand_name}"])
        
        # Fill formulas with data
        subject_lines = []
        for formula in formulas:
            filled_formula = formula
            for key, value in data.items():
                filled_formula = filled_formula.replace(f'{{{key}}}', str(value))
            subject_lines.append(filled_formula)
        
        return subject_lines
    
    def A_B_test_variations(self, content: str, variation_type: str) -> Dict[str, str]:
        """Generate A/B test variations of marketing content"""        variations = {}
        
        if variation_type == 'headline':
            # Extract current headline
            lines = content.split('\n')
            current_headline = lines[0] if lines[0].startswith('#') else "# Original Headline"
            
            # Generate variations
            variations['original'] = content
            variations['benefit_focused'] = content.replace(
                current_headline, 
                "# Get [Specific Benefit] in [Timeframe]"
            )
            variations['urgency_focused'] = content.replace(
                current_headline,
                "# Limited Time: [Benefit] - Act Now"
            )
            variations['question_focused'] = content.replace(
                current_headline,
                "# Ready to [Desired Outcome]?"
            )
        
        elif variation_type == 'cta':
            variations['original'] = content
            variations['action_focused'] = content.replace(
                'Get Started', 'Start My Transformation'
            )
            variations['benefit_focused'] = content.replace(
                'Get Started', 'Claim My [Benefit]'
            )
            variations['urgency_focused'] = content.replace(
                'Get Started', 'Get Instant Access'
            )
        
        return variations


class CampaignTemplate:
    """Marketing campaign template for structured campaigns"""    
    def __init__(self, **kwargs):
        self.campaign_type = kwargs.get('campaign_type', 'email')
        self.title = kwargs.get('title', '')
        self.description = kwargs.get('description', '')
        self.target_audience = kwargs.get('target_audience', '')
        self.objectives = kwargs.get('objectives', [])
        self.channels = kwargs.get('channels', [])
        self.budget = kwargs.get('budget', 0)
        self.duration = kwargs.get('duration', 30)  # days
        self.kpis = kwargs.get('kpis', [])
    
    def render(self, data: Dict[str, Any]) -> str:
        """Render campaign template with data"""        title = data.get('title', self.title)
        description = data.get('description', self.description)
        return f"# {title}\n\n{description}"
    
    def get_structure(self) -> Dict[str, Any]:
        """Get campaign template structure"""        return {
            'campaign_type': self.campaign_type,
            'title': self.title,
            'description': self.description,
            'target_audience': self.target_audience,
            'objectives': self.objectives,
            'channels': self.channels,
            'budget': self.budget,
            'duration': self.duration,
            'kpis': self.kpis
        }


class CampaignType:
    """Campaign type enumeration"""    EMAIL = "email"
    SOCIAL_MEDIA = "social_media"
    CONTENT = "content"
    PAID_ADS = "paid_ads"
    INFLUENCER = "influencer"
    SEO = "seo"
    WEBINAR = "webinar"
    PRODUCT_LAUNCH = "product_launch"
