"""
Multilingual Support Module - Usage Examples

Comprehensive examples demonstrating the multilingual capabilities
for global content creators and influencers.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE ⚠️
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

# Import our comprehensive multilingual system
from multilingual_support import (
    create_multilingual_system,
    quick_translate,
    detect_language,
    SupportedLanguage,
    MultilingualOrchestrator,
    MessageType,
    LocalizationLevel,
    CrossLanguageStrategy,
    ContentType,
    LocalizationRequest
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_quick_translation():
    """Example 1: Quick translation for simple use cases"""
    print("🚀 Example 1: Quick Translation")
    print("=" * 50)
    
    # Quick translations to various languages
    messages = [
        ("Hello, how are you today?", SupportedLanguage.SPANISH),
        ("Bonjour, comment allez-vous?", SupportedLanguage.ENGLISH),
        ("Guten Tag, wie geht es Ihnen?", SupportedLanguage.FRENCH),
        ("こんにちは、元気ですか？", SupportedLanguage.ENGLISH),
        ("مرحبا، كيف حالك؟", SupportedLanguage.ENGLISH),
        ("Привет, как дела?", SupportedLanguage.ENGLISH),
        ("你好，你好吗？", SupportedLanguage.ENGLISH),
        ("Hola, ¿cómo estás?", SupportedLanguage.HINDI),
    ]
    
    for message, target_lang in messages:
        try:
            # Detect source language first
            detected_lang, confidence = await detect_language(
                message,
                database_url="sqlite+aiosqlite:///multilingual_examples.db"
            )
            
            # Translate message
            translation = await quick_translate(
                message,
                target_lang,
                detected_lang,
                database_url="sqlite+aiosqlite:///multilingual_examples.db"
            )
            
            print(f"Source ({detected_lang.value}, {confidence:.2f}): {message}")
            print(f"Target ({target_lang.value}): {translation}")
            print("-" * 30)
            
        except Exception as e:
            print(f"Translation failed for '{message}': {e}")
    
    print("\n")


async def example_global_content_creator():
    """Example 2: Global content creator managing international audience"""
    print("🌍 Example 2: Global Content Creator Scenario")
    print("=" * 50)
    
    # Create enterprise multilingual system
    orchestrator = await create_multilingual_system(
        "enterprise",
        database_url="sqlite+aiosqlite:///multilingual_examples.db",
        redis_host="localhost",
        redis_port=6379
    )
    
    # Initialize multilingual conversation for a global influencer
    session, contexts = await orchestrator.initialize_multilingual_conversation(
        user_id="global_influencer_001",
        primary_language=SupportedLanguage.ENGLISH,
        target_languages=[
            SupportedLanguage.SPANISH,
            SupportedLanguage.FRENCH,
            SupportedLanguage.GERMAN,
            SupportedLanguage.ITALIAN,
            SupportedLanguage.PORTUGUESE_BR,
            SupportedLanguage.JAPANESE,
            SupportedLanguage.KOREAN,
            SupportedLanguage.CHINESE_SIMPLIFIED,
            SupportedLanguage.ARABIC,
            SupportedLanguage.HINDI,
            SupportedLanguage.RUSSIAN,
            SupportedLanguage.DUTCH,
            SupportedLanguage.SWEDISH,
            SupportedLanguage.PORTUGUESE_PT,
            SupportedLanguage.TURKISH
        ],
        domain="social_media"
    )
    
    print(f"✅ Created session: {session.session_id}")
    print(f"📱 Active languages: {len(session.active_languages)}")
    
    # Content creator messages for different audiences
    content_messages = [
        ("🎉 Big announcement coming tomorrow! Can't wait to share this exciting news with all of you! #excited #announcement", SupportedLanguage.SPANISH),
        ("Thank you so much for 1 million followers! This journey has been incredible and I couldn't have done it without your amazing support! ❤️", SupportedLanguage.FRENCH),
        ("New product launch next week! This is something I've been working on for months. Who's excited? 🚀", SupportedLanguage.GERMAN),
        ("Behind the scenes of today's photoshoot! The team was amazing and the results are stunning! 📸✨", SupportedLanguage.ITALIAN),
        ("Travel day! Heading to Tokyo for an incredible collaboration. Can't wait to explore the city! ✈️🗾", SupportedLanguage.JAPANESE),
        ("Collaboration announcement! Working with an amazing brand that aligns perfectly with my values 🤝", SupportedLanguage.KOREAN),
        ("Morning routine video is live! Start your day with positivity and good energy ☀️💪", SupportedLanguage.CHINESE_SIMPLIFIED),
        ("Giving back to the community! Partnering with a charity close to my heart 💝", SupportedLanguage.ARABIC),
        ("Fitness motivation Monday! Remember, every small step counts towards your goals 🏃‍♀️💪", SupportedLanguage.HINDI),
        ("Sunday reflection: Grateful for all the opportunities and amazing people in my life 🙏✨", SupportedLanguage.RUSSIAN)
    ]
    
    for message, target_lang in content_messages:
        try:
            # Process message with cultural adaptation
            response = await orchestrator.process_multilingual_message(
                message=message,
                session_id=session.session_id,
                target_language=target_lang,
                message_type=MessageType.SOCIAL_MEDIA_POST,
                cross_language_strategy=CrossLanguageStrategy.AUTO_TRANSLATE
            )
            
            print(f"\n📝 Original: {message}")
            print(f"🌐 {target_lang.value.upper()}: {response.processed_message.localized_text}")
            print(f"📊 Confidence: {response.processed_message.confidence_score:.2f}")
            
            if response.cultural_adaptation:
                print(f"🎭 Cultural adaptation applied: {len(response.cultural_adaptation.adaptations)} changes")
            
        except Exception as e:
            print(f"❌ Failed to process message for {target_lang.value}: {e}")
    
    print("\n")


async def example_business_international_meeting():
    """Example 3: International business meeting with multiple languages"""
    print("💼 Example 3: International Business Meeting")
    print("=" * 50)
    
    # Create business-focused system
    orchestrator = await create_multilingual_system(
        "enterprise",
        database_url="sqlite+aiosqlite:///multilingual_examples.db"
    )
    
    # Business meeting with participants from different countries
    participants = [
        ("CEO_USA", SupportedLanguage.ENGLISH_US, "Welcome everyone to our quarterly review meeting. Let's discuss our global expansion strategy."),
        ("Director_Germany", SupportedLanguage.GERMAN_DE, "Vielen Dank für die Einladung. Unsere Zahlen in Europa sind sehr ermutigend."),
        ("Manager_Japan", SupportedLanguage.JAPANESE, "アジア太平洋地域での売上が20%増加しました。新しい市場機会があります。"),
        ("VP_France", SupportedLanguage.FRENCH_FR, "L'équipe française a dépassé tous les objectifs du trimestre. Nous proposons d'étendre nos opérations."),
        ("Director_Brazil", SupportedLanguage.PORTUGUESE_BR, "O mercado brasileiro está muito promissor. Precisamos investir mais em marketing digital."),
        ("Manager_India", SupportedLanguage.HINDI_IN, "भारतीय बाजार में हमारी स्थिति मजबूत हो रही है। नई तकनीक का इस्तेमाल करना चाहिए।"),
        ("CEO_China", SupportedLanguage.CHINESE_SIMPLIFIED, "中国市场的潜力巨大，我们需要本地化我们的产品和服务。"),
        ("Director_Russia", SupportedLanguage.RUSSIAN_RU, "Российский рынок показывает стабильный рост. Рекомендую увеличить инвестиции."),
        ("Manager_Spain", SupportedLanguage.SPANISH_ES, "El equipo español ha desarrollado nuevas estrategias innovadoras para el mercado europeo."),
        ("VP_Netherlands", SupportedLanguage.DUTCH_NL, "De Nederlandse tak wil graag de leidende rol nemen in duurzaamheidsinitiatieven.")
    ]
    
    # Create meeting session
    meeting_session, contexts = await orchestrator.initialize_multilingual_conversation(
        user_id="international_meeting_001",
        primary_language=SupportedLanguage.ENGLISH,
        target_languages=[p[1] for p in participants],
        domain="business_meeting"
    )
    
    print(f"🏢 Meeting started with {len(participants)} participants")
    print(f"🌐 Languages: {[p[1].value for p in participants]}")
    
    # Process each participant's message and translate to English for everyone
    for participant_id, source_lang, message in participants:
        try:
            # Translate to English for meeting minutes
            response = await orchestrator.process_multilingual_message(
                message=message,
                session_id=meeting_session.session_id,
                target_language=SupportedLanguage.ENGLISH,
                message_type=MessageType.BUSINESS_MESSAGE,
                cross_language_strategy=CrossLanguageStrategy.AUTO_TRANSLATE
            )
            
            print(f"\n👤 {participant_id} ({source_lang.value}):")
            print(f"   Original: {message}")
            print(f"   English: {response.processed_message.localized_text}")
            print(f"   Confidence: {response.processed_message.confidence_score:.2f}")
            
        except Exception as e:
            print(f"❌ Translation failed for {participant_id}: {e}")
    
    print("\n")


async def example_cultural_adaptation():
    """Example 4: Cultural adaptation for different regions"""
    print("🎭 Example 4: Cultural Adaptation Examples")
    print("=" * 50)
    
    orchestrator = await create_multilingual_system(
        "enterprise",
        database_url="sqlite+aiosqlite:///multilingual_examples.db"
    )
    
    # Business message with cultural adaptations
    business_message = "Let's schedule a meeting for tomorrow at 2 PM to discuss the urgent project deadline."
    
    cultural_targets = [
        (SupportedLanguage.JAPANESE, "High context, formal business culture"),
        (SupportedLanguage.GERMAN_DE, "Direct communication, punctual culture"),
        (SupportedLanguage.ARABIC_SA, "Relationship-based business culture"),
        (SupportedLanguage.SPANISH_MX, "Warm, relationship-oriented culture"),
        (SupportedLanguage.CHINESE_SIMPLIFIED, "Hierarchical business culture"),
        (SupportedLanguage.FRENCH_FR, "Formal business etiquette"),
        (SupportedLanguage.HINDI_IN, "Respectful, hierarchical communication"),
        (SupportedLanguage.SWEDISH_SE, "Egalitarian, consensus-based culture"),
        (SupportedLanguage.PORTUGUESE_BR, "Warm, relationship-focused culture"),
        (SupportedLanguage.RUSSIAN_RU, "Formal, hierarchical business style")
    ]
    
    for target_lang, cultural_note in cultural_targets:
        try:
            session, contexts = await orchestrator.initialize_multilingual_conversation(
                user_id="cultural_adaptation_test",
                primary_language=SupportedLanguage.ENGLISH,
                target_languages=[target_lang],
                domain="business"
            )
            
            response = await orchestrator.process_multilingual_message(
                message=business_message,
                session_id=session.session_id,
                target_language=target_lang,
                message_type=MessageType.BUSINESS_MESSAGE
            )
            
            print(f"\n🌍 {target_lang.value.upper()} ({cultural_note}):")
            print(f"   {response.processed_message.localized_text}")
            
            if response.cultural_adaptation:
                print(f"   🎭 Cultural adaptations: {len(response.cultural_adaptation.adaptations)}")
            
        except Exception as e:
            print(f"❌ Cultural adaptation failed for {target_lang.value}: {e}")
    
    print("\n")


async def example_content_localization():
    """Example 5: Advanced content localization (dates, numbers, currency)"""
    print("📅 Example 5: Content Localization Examples")
    print("=" * 50)
    
    orchestrator = await create_multilingual_system(
        "enterprise",
        database_url="sqlite+aiosqlite:///multilingual_examples.db"
    )
    
    # Content with various localizable elements
    content_examples = [
        "The event is scheduled for March 15, 2025 at 14:30.",
        "The price is $1,234.56 USD for the premium package.",
        "We sold 1,000,000 units generating €2,500,000.50 in revenue.",
        "The temperature reached 32.5°C (90.5°F) yesterday.",
        "Please call us at +1-555-123-4567 for more information.",
        "The file size is 1.5 GB and download speed is 100 Mbps.",
        "Our address is 123 Main Street, Suite 456, New York, NY 10001, USA."
    ]
    
    localization_targets = [
        SupportedLanguage.GERMAN_DE,      # DD.MM.YYYY, 14:30, €, German address format
        SupportedLanguage.FRENCH_FR,      # DD/MM/YYYY, 14h30, €, French formatting
        SupportedLanguage.JAPANESE,       # YYYY年MM月DD日, Japanese Yen, Japanese address
        SupportedLanguage.ARABIC_SA,      # Arabic numerals, Saudi Riyal, RTL format
        SupportedLanguage.HINDI_IN,       # Indian numbering system, Rupees, Indian format
        SupportedLanguage.CHINESE_SIMPLIFIED,  # Chinese date format, Yuan, Chinese addressing
        SupportedLanguage.SPANISH_MX,     # Mexican format, Mexican Peso, Spanish format
        SupportedLanguage.RUSSIAN_RU,     # Russian format, Rubles, Cyrillic
        SupportedLanguage.PORTUGUESE_BR,  # Brazilian format, Real, Portuguese
        SupportedLanguage.SWEDISH_SE      # Swedish format, Krona, Swedish conventions
    ]
    
    for content in content_examples[:3]:  # Process first 3 examples
        print(f"\n📝 Original content: {content}")
        
        for target_lang in localization_targets[:5]:  # Test with 5 languages
            try:
                session, contexts = await orchestrator.initialize_multilingual_conversation(
                    user_id="content_localization_test",
                    primary_language=SupportedLanguage.ENGLISH,
                    target_languages=[target_lang],
                    domain="general"
                )
                
                response = await orchestrator.process_multilingual_message(
                    message=content,
                    session_id=session.session_id,
                    target_language=target_lang,
                    message_type=MessageType.INFORMATIONAL
                )
                
                print(f"   🌐 {target_lang.value}: {response.processed_message.localized_text}")
                
            except Exception as e:
                print(f"   ❌ {target_lang.value}: Localization failed - {e}")
    
    print("\n")


async def example_sign_language_support():
    """Example 6: Sign language support demonstration"""
    print("🤟 Example 6: Sign Language Support")
    print("=" * 50)
    
    # Demonstrate sign language awareness
    sign_languages = [
        SupportedLanguage.AMERICAN_SIGN_LANGUAGE,
        SupportedLanguage.BRITISH_SIGN_LANGUAGE,
        SupportedLanguage.FRENCH_SIGN_LANGUAGE,
        SupportedLanguage.GERMAN_SIGN_LANGUAGE,
        SupportedLanguage.JAPANESE_SIGN_LANGUAGE
    ]
    
    for sign_lang in sign_languages:
        family = SupportedLanguage.get_language_family(sign_lang)
        script = SupportedLanguage.get_language_script(sign_lang)
        direction = SupportedLanguage.get_language_direction(sign_lang)
        
        print(f"🤟 {sign_lang.value}")
        print(f"   Family: {family}")
        print(f"   Script: {script}")
        print(f"   Direction: {direction}")
        print(f"   Note: Visual-spatial language support")
    
    print("\n")


async def example_historical_languages():
    """Example 7: Historical language preservation"""
    print("🏛️ Example 7: Historical Language Preservation")
    print("=" * 50)
    
    historical_languages = [
        SupportedLanguage.LATIN,
        SupportedLanguage.ANCIENT_GREEK,
        SupportedLanguage.OLD_ENGLISH,
        SupportedLanguage.MIDDLE_ENGLISH,
        SupportedLanguage.OLD_NORSE,
        SupportedLanguage.GOTHIC
    ]
    
    for hist_lang in historical_languages:
        family = SupportedLanguage.get_language_family(hist_lang)
        script = SupportedLanguage.get_language_script(hist_lang)
        complexity = SupportedLanguage.get_linguistic_complexity(hist_lang)
        
        print(f"🏛️ {hist_lang.value}")
        print(f"   Family: {family}")
        print(f"   Script: {script}")
        print(f"   Complexity: {complexity}")
        print(f"   Status: Historical preservation")
    
    print("\n")


async def example_tonal_language_recognition():
    """Example 8: Tonal language recognition"""
    print("🎵 Example 8: Tonal Language Recognition")
    print("=" * 50)
    
    languages_to_test = [
        SupportedLanguage.CHINESE_SIMPLIFIED,
        SupportedLanguage.CHINESE_TRADITIONAL,
        SupportedLanguage.THAI,
        SupportedLanguage.VIETNAMESE,
        SupportedLanguage.CANTONESE,
        SupportedLanguage.YORUBA,
        SupportedLanguage.ENGLISH,  # Non-tonal for comparison
        SupportedLanguage.SPANISH,  # Non-tonal for comparison
    ]
    
    for lang in languages_to_test:
        is_tonal = SupportedLanguage.is_tonal_language(lang)
        family = SupportedLanguage.get_language_family(lang)
        complexity = SupportedLanguage.get_linguistic_complexity(lang)
        
        tonal_indicator = "🎵" if is_tonal else "🔤"
        
        print(f"{tonal_indicator} {lang.value}")
        print(f"   Tonal: {'Yes' if is_tonal else 'No'}")
        print(f"   Family: {family}")
        print(f"   Complexity: {complexity}")
    
    print("\n")


async def run_all_examples():
    """Run all multilingual examples"""
    print("🌍 MULTILINGUAL SUPPORT SYSTEM - COMPREHENSIVE EXAMPLES")
    print("=" * 70)
    print("Supporting 300+ languages and dialects worldwide! 🚀")
    print("=" * 70)
    
    examples = [
        example_quick_translation,
        example_global_content_creator,
        example_business_international_meeting,
        example_cultural_adaptation,
        example_content_localization,
        example_sign_language_support,
        example_historical_languages,
        example_tonal_language_recognition
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            await example_func()
            print(f"✅ Example {i} completed successfully!")
        except Exception as e:
            print(f"❌ Example {i} failed: {e}")
        
        if i < len(examples):
            print("\n" + "="*50 + "\n")
    
    print("\n🎉 All examples completed! The multilingual system supports:")
    print(f"   📊 {len(SupportedLanguage)} languages and dialects")
    print(f"   🌍 195+ countries and regions")
    print(f"   📝 20+ writing systems")
    print(f"   🎭 50+ cultural contexts")
    print(f"   💼 25+ business cultures")
    print(f"   🤟 Sign language support")
    print(f"   🏛️ Historical language preservation")
    print(f"   🎵 Tonal language recognition")


if __name__ == "__main__":
    # Run all examples
    asyncio.run(run_all_examples())
