"""
🌍 LANGUAGES & TRANSLATION ROUTES - Complete Implementation
===========================================================
ALL 20 endpoints for translation, TTS, localization, language tools
Author: Fahed Mlaiel
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

router = APIRouter(prefix="/languages", tags=["Languages & Translation"])

# ============================================================================
# TRANSLATION
# ============================================================================

@router.post("/translate")
async def translate_text(text: str, source_lang: str, target_lang: str):
    """Translate text"""
    try:
        from backend.languages.translation_engine import TranslationEngine
        engine = TranslationEngine()
        await engine.initialize()
        
        translated = await engine.translate(text, source_lang, target_lang)
        return {"original": text, "translated": translated, "source": source_lang, "target": target_lang}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/translate/batch")
async def translate_batch(texts: List[str], source_lang: str, target_lang: str):
    """Translate multiple texts"""
    try:
        from backend.languages.translation_engine import TranslationEngine
        engine = TranslationEngine()
        await engine.initialize()
        
        translations = await engine.translate_batch(texts, source_lang, target_lang)
        return {"translations": translations, "source": source_lang, "target": target_lang}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/translate/document")
async def translate_document(file: UploadFile = File(...), target_lang: str = "en"):
    """Translate document"""
    try:
        from backend.languages.translation_engine import TranslationEngine
        engine = TranslationEngine()
        await engine.initialize()
        
        file_data = await file.read()
        translated = await engine.translate_document(file_data, target_lang, filename=file.filename)
        return {"message": "Document translated", "result": translated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect")
async def detect_language(text: str):
    """Detect text language"""
    try:
        from backend.languages.translation_engine import TranslationEngine
        engine = TranslationEngine()
        await engine.initialize()
        
        language = await engine.detect_language(text)
        return {"text": text, "language": language}
    except Exception as e:
        return {"text": text, "language": "unknown", "error": str(e)}

# ============================================================================
# TEXT-TO-SPEECH
# ============================================================================

@router.post("/tts")
async def text_to_speech(text: str, language: str = "en", voice: Optional[str] = None):
    """Convert text to speech"""
    try:
        from backend.languages.translation_engine import TranslationEngine
        engine = TranslationEngine()
        await engine.initialize()
        
        audio = await engine.text_to_speech(text, language, voice)
        return {"message": "Audio generated", "audio": audio}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tts/voices")
async def list_tts_voices(language: Optional[str] = None):
    """Get available TTS voices"""
    try:
        from backend.languages.translation_engine import TranslationEngine
        engine = TranslationEngine()
        await engine.initialize()
        
        voices = await engine.list_tts_voices(language)
        return {"voices": voices}
    except Exception as e:
        return {"voices": [], "error": str(e)}

# ============================================================================
# SPEECH-TO-TEXT
# ============================================================================

@router.post("/stt")
async def speech_to_text(audio: UploadFile = File(...), language: Optional[str] = None):
    """Convert speech to text"""
    try:
        from backend.languages.translation_engine import TranslationEngine
        engine = TranslationEngine()
        await engine.initialize()
        
        audio_data = await audio.read()
        text = await engine.speech_to_text(audio_data, language)
        return {"message": "Audio transcribed", "text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stt/translate")
async def transcribe_and_translate(audio: UploadFile = File(...), target_lang: str = "en"):
    """Transcribe audio and translate"""
    try:
        from backend.languages.translation_engine import TranslationEngine
        engine = TranslationEngine()
        await engine.initialize()
        
        audio_data = await audio.read()
        result = await engine.transcribe_and_translate(audio_data, target_lang)
        return {"message": "Audio transcribed and translated", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# LOCALIZATION
# ============================================================================

@router.post("/localize")
async def localize_content(content: Dict[str, Any], target_lang: str):
    """Localize content"""
    try:
        from backend.languages.translation_engine import TranslationEngine
        engine = TranslationEngine()
        await engine.initialize()
        
        localized = await engine.localize_content(content, target_lang)
        return {"message": "Content localized", "localized": localized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/locales")
async def list_locales():
    """Get supported locales"""
    try:
        from backend.languages.translation_engine import TranslationEngine
        engine = TranslationEngine()
        await engine.initialize()
        
        locales = await engine.list_locales()
        return {"locales": locales}
    except Exception as e:
        return {"locales": [], "error": str(e)}

@router.get("/locales/{locale}/strings")
async def get_locale_strings(locale: str):
    """Get locale translation strings"""
    try:
        from backend.languages.translation_engine import TranslationEngine
        engine = TranslationEngine()
        await engine.initialize()
        
        strings = await engine.get_locale_strings(locale)
        return {"locale": locale, "strings": strings}
    except Exception as e:
        return {"locale": locale, "strings": {}, "error": str(e)}

# ============================================================================
# LANGUAGE TOOLS
# ============================================================================

@router.post("/grammar/check")
async def check_grammar(text: str, language: str = "en"):
    """Check grammar"""
    try:
        from backend.languages.translation_engine import TranslationEngine
        engine = TranslationEngine()
        await engine.initialize()
        
        corrections = await engine.check_grammar(text, language)
        return {"text": text, "corrections": corrections}
    except Exception as e:
        return {"text": text, "corrections": [], "error": str(e)}

@router.post("/spelling/check")
async def check_spelling(text: str, language: str = "en"):
    """Check spelling"""
    try:
        from backend.languages.translation_engine import TranslationEngine
        engine = TranslationEngine()
        await engine.initialize()
        
        corrections = await engine.check_spelling(text, language)
        return {"text": text, "corrections": corrections}
    except Exception as e:
        return {"text": text, "corrections": [], "error": str(e)}

@router.post("/paraphrase")
async def paraphrase_text(text: str, language: str = "en"):
    """Paraphrase text"""
    try:
        from backend.languages.translation_engine import TranslationEngine
        engine = TranslationEngine()
        await engine.initialize()
        
        paraphrased = await engine.paraphrase(text, language)
        return {"original": text, "paraphrased": paraphrased}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize")
async def summarize_text(text: str, language: str = "en", max_length: Optional[int] = None):
    """Summarize text"""
    try:
        from backend.languages.translation_engine import TranslationEngine
        engine = TranslationEngine()
        await engine.initialize()
        
        summary = await engine.summarize(text, language, max_length)
        return {"original": text, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# LANGUAGE PAIRS
# ============================================================================

@router.get("/languages")
async def list_supported_languages():
    """Get supported languages"""
    try:
        from backend.languages.translation_engine import TranslationEngine
        engine = TranslationEngine()
        await engine.initialize()
        
        languages = await engine.list_supported_languages()
        return {"languages": languages}
    except Exception as e:
        return {"languages": [], "error": str(e)}

@router.get("/languages/{lang}/pairs")
async def get_language_pairs(lang: str):
    """Get available translation pairs for language"""
    try:
        from backend.languages.translation_engine import TranslationEngine
        engine = TranslationEngine()
        await engine.initialize()
        
        pairs = await engine.get_language_pairs(lang)
        return {"language": lang, "pairs": pairs}
    except Exception as e:
        return {"language": lang, "pairs": [], "error": str(e)}

# ============================================================================
# GLOSSARY & TERMINOLOGY
# ============================================================================

@router.post("/glossary/add")
async def add_glossary_term(source_lang: str, target_lang: str, source_term: str, target_term: str):
    """Add glossary term"""
    try:
        from backend.languages.translation_engine import TranslationEngine
        engine = TranslationEngine()
        await engine.initialize()
        
        await engine.add_glossary_term(source_lang, target_lang, source_term, target_term)
        return {"message": "Glossary term added", "source": source_term, "target": target_term}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/glossary/{source_lang}/{target_lang}")
async def get_glossary(source_lang: str, target_lang: str):
    """Get glossary"""
    try:
        from backend.languages.translation_engine import TranslationEngine
        engine = TranslationEngine()
        await engine.initialize()
        
        glossary = await engine.get_glossary(source_lang, target_lang)
        return {"source_lang": source_lang, "target_lang": target_lang, "glossary": glossary}
    except Exception as e:
        return {"source_lang": source_lang, "target_lang": target_lang, "glossary": {}, "error": str(e)}

# ============================================================================
# STATS & USAGE
# ============================================================================

@router.get("/stats")
async def get_translation_stats():
    """Get translation statistics"""
    try:
        from backend.languages.translation_engine import TranslationEngine
        engine = TranslationEngine()
        await engine.initialize()
        
        stats = await engine.get_translation_stats()
        return stats
    except Exception as e:
        return {"error": str(e), "stats": {}}
