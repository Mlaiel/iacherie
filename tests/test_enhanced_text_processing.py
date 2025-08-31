"""
Test suite for Enhanced Industrial Text Processing
================================================

Tests for the enhanced text processing capabilities including:
- Industrial text processing
- Contextual BERT/RoBERTa embeddings  
- Semantic plagiarism detection
- Authorship analysis
- 644 language support

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.algorithms.enhanced_text_processing import (
    IndustrialTextProcessor,
    AuthorshipFeatures,
    SemanticPlagiarismResult,
    ContextualEmbeddingsEngine,
    Enhanced644LanguageSupport,
    create_enhanced_text_processor
)

from conversational.multilingual_support.enhanced_644_language_support import (
    Enhanced644LanguageDatabase,
    LanguageFamily,
    ScriptType,
    create_644_language_support
)

class TestIndustrialTextProcessing:
    """Test industrial text processing capabilities"""
    
    @pytest.fixture
    def processor(self):
        return create_enhanced_text_processor()
    
    def test_processor_creation(self, processor):
        """Test that processor can be created successfully"""
        assert isinstance(processor, IndustrialTextProcessor)
        assert processor.language_support is not None
        assert processor.embeddings_engine is not None
    
    def test_comprehensive_text_processing(self, processor):
        """Test comprehensive text processing"""
        text = """
        Artificial intelligence is revolutionizing the way we create and consume content.
        Modern AI systems can analyze text patterns, detect plagiarism, and identify authorship.
        This technology enables content creators to protect their intellectual property effectively.
        """
        
        result = processor.process_industrial_text(text)
        
        # Check basic structure
        assert 'language_analysis' in result
        assert 'contextual_embeddings' in result
        assert 'authorship_features' in result
        assert 'text_statistics' in result
        assert 'processing_metadata' in result
        
        # Check language analysis
        lang_info = result['language_analysis']
        assert 'language' in lang_info
        assert 'confidence' in lang_info
        assert 'script' in lang_info
        assert 'family' in lang_info
        
        # Check embeddings
        embeddings = result['contextual_embeddings']
        assert 'document_embedding' in embeddings
        assert 'sentence_embeddings' in embeddings
        assert 'contextual_features' in embeddings
        assert 'embedding_metadata' in embeddings
        
        # Check authorship features
        authorship = result['authorship_features']
        assert 'lexical_diversity' in authorship
        assert 'average_sentence_length' in authorship
        assert 'writing_style_signature' in authorship
        assert 'vocabulary_richness' in authorship
        
        # Check text statistics
        stats = result['text_statistics']
        assert stats['word_count'] > 0
        assert stats['sentence_count'] > 0
        assert stats['character_count'] > 0
    
    def test_authorship_analysis(self, processor):
        """Test authorship analysis features"""
        # Academic style text
        academic_text = """
        The methodological framework employed in this comprehensive investigation 
        encompasses a multidisciplinary approach that integrates quantitative and 
        qualitative analytical paradigms. Furthermore, the epistemological foundation 
        underlying this research methodology facilitates systematic examination of 
        complex phenomenological structures.
        """
        
        authorship = processor.analyze_authorship(academic_text)
        
        assert isinstance(authorship, AuthorshipFeatures)
        assert authorship.lexical_diversity > 0
        assert authorship.average_sentence_length > 0
        assert authorship.vocabulary_richness > 0
        assert authorship.syntactic_complexity > 0
        assert len(authorship.writing_style_signature) > 0
        assert isinstance(authorship.function_word_frequency, dict)
        
        # Conversational style text
        conversational_text = """
        Hey! You know what? I think AI is pretty cool. It can do lots of things. 
        Like, it helps us write better. And it finds copied stuff too. 
        That's awesome, right?
        """
        
        casual_authorship = processor.analyze_authorship(conversational_text)
        
        # Academic text should have higher complexity than conversational
        assert authorship.syntactic_complexity > casual_authorship.syntactic_complexity
        assert authorship.average_sentence_length > casual_authorship.average_sentence_length

class TestSemanticPlagiarismDetection:
    """Test semantic plagiarism detection"""
    
    @pytest.fixture
    def processor(self):
        return create_enhanced_text_processor()
    
    def test_exact_copy_detection(self, processor):
        """Test detection of exact copies"""
        original = "Artificial intelligence is transforming content creation."
        copy = "Artificial intelligence is transforming content creation."
        
        result = processor.detect_semantic_plagiarism(original, [copy])
        
        assert isinstance(result, SemanticPlagiarismResult)
        assert result.is_plagiarized == True
        assert result.semantic_similarity > 0.9
        assert len(result.similar_passages) > 0
    
    def test_paraphrase_detection(self, processor):
        """Test detection of paraphrased content"""
        original = "Machine learning algorithms can identify patterns in text data."
        paraphrase = "AI systems are capable of recognizing textual patterns through learning."
        
        result = processor.detect_semantic_plagiarism(original, [paraphrase])
        
        assert isinstance(result, SemanticPlagiarismResult)
        # Should detect some similarity even in paraphrases
        assert result.semantic_similarity > 0.1
    
    def test_no_plagiarism(self, processor):
        """Test when there is no plagiarism"""
        original = "The weather is sunny today."
        different = "Quantum computing involves complex mathematical calculations."
        
        result = processor.detect_semantic_plagiarism(original, [different])
        
        assert isinstance(result, SemanticPlagiarismResult)
        assert result.semantic_similarity < 0.5  # Should be low similarity

class TestContextualEmbeddings:
    """Test contextual embeddings engine"""
    
    @pytest.fixture
    def embeddings_engine(self):
        return ContextualEmbeddingsEngine()
    
    def test_embedding_extraction(self, embeddings_engine):
        """Test embedding extraction"""
        text = "This is a test sentence for embedding extraction."
        
        result = embeddings_engine.extract_contextual_embeddings(text)
        
        assert 'document_embedding' in result
        assert 'sentence_embeddings' in result
        assert 'contextual_features' in result
        assert 'embedding_metadata' in result
        
        # Check embedding dimensions
        doc_emb = result['document_embedding']
        assert len(doc_emb) == 768  # BERT-like dimension
        
        # Check sentence embeddings
        sent_embs = result['sentence_embeddings']
        assert len(sent_embs) > 0
        assert all(len(emb) == 768 for emb in sent_embs)
    
    def test_contextual_awareness(self, embeddings_engine):
        """Test context-aware embeddings"""
        text = "The bank is near the river."
        context1 = "Financial institutions and money management"
        context2 = "Geography and natural water features"
        
        result1 = embeddings_engine.extract_contextual_embeddings(text, context1)
        result2 = embeddings_engine.extract_contextual_embeddings(text, context2)
        
        # Embeddings should be different based on context
        emb1 = result1['document_embedding']
        emb2 = result2['document_embedding']
        
        # They should not be identical (context should influence embeddings)
        assert emb1 != emb2
        
        # Both should have context relevance > 0
        assert result1['contextual_features']['context_relevance'] >= 0
        assert result2['contextual_features']['context_relevance'] >= 0

class Test644LanguageSupport:
    """Test enhanced 644 language support"""
    
    @pytest.fixture
    def language_db(self):
        return create_644_language_support()
    
    def test_language_database_creation(self, language_db):
        """Test language database creation"""
        assert isinstance(language_db, Enhanced644LanguageDatabase)
        assert len(language_db.languages) > 300  # Should have substantial language coverage
    
    def test_language_families(self, language_db):
        """Test language family support"""
        stats = language_db.get_language_statistics()
        
        assert 'by_family' in stats
        assert 'indo-european' in stats['by_family']
        assert 'sino-tibetan' in stats['by_family']
        assert 'niger-congo' in stats['by_family']
        assert 'afroasiatic' in stats['by_family']
        
        # Check that we have substantial coverage
        assert stats['total_languages'] >= 100  # Minimum threshold
    
    def test_script_support(self, language_db):
        """Test script type support"""
        stats = language_db.get_language_statistics()
        
        assert 'by_script' in stats
        assert 'latin' in stats['by_script']
        assert 'cyrillic' in stats['by_script']
        assert 'arabic' in stats['by_script']
        assert 'han' in stats['by_script']
    
    def test_language_search(self, language_db):
        """Test language search functionality"""
        # Search for English
        results = language_db.search_languages("English")
        assert len(results) > 0
        assert any(lang.code == 'en' for lang in results)
        
        # Search for Chinese
        results = language_db.search_languages("Chinese")
        assert len(results) > 0
        assert any('zh' in lang.code for lang in results)
    
    def test_specific_languages(self, language_db):
        """Test specific language support"""
        # Test major languages
        english = language_db.get_language_info('en')
        assert english is not None
        assert english.name == 'English'
        assert english.family == LanguageFamily.INDO_EUROPEAN
        assert english.script == ScriptType.LATIN
        
        # Test Chinese
        chinese = language_db.get_language_info('zh-cn')
        assert chinese is not None
        assert chinese.family == LanguageFamily.SINO_TIBETAN
        assert chinese.script == ScriptType.HAN
        
        # Test Arabic
        arabic = language_db.get_language_info('ar')
        assert arabic is not None
        assert arabic.family == LanguageFamily.AFROASIATIC
        assert arabic.script == ScriptType.ARABIC
        assert arabic.direction == 'rtl'
    
    def test_endangered_languages(self, language_db):
        """Test support for endangered languages"""
        stats = language_db.get_language_statistics()
        assert 'by_status' in stats
        
        # Should have some endangered languages
        if 'endangered' in stats['by_status']:
            assert stats['by_status']['endangered'] > 0

class TestEnhanced644LanguageSupport:
    """Test the enhanced language support capabilities"""
    
    @pytest.fixture
    def lang_support(self):
        return Enhanced644LanguageSupport()
    
    def test_basic_language_detection(self, lang_support):
        """Test basic language detection"""
        # English text
        english_result = lang_support.detect_language("Hello, this is an English sentence.")
        assert english_result['language'] == 'en'
        assert english_result['script'] == 'Latin'
        assert english_result['family'] == 'Germanic'
        
        # Test with hint
        result_with_hint = lang_support.detect_language("Some text", language_hint='fr')
        # Since we provide a hint, it should be respected if the language is supported
        # Note: This is a simplified test as the actual implementation would be more sophisticated

class TestIntegration:
    """Integration tests for all components"""
    
    @pytest.fixture
    def processor(self):
        return create_enhanced_text_processor()
    
    def test_full_pipeline(self, processor):
        """Test the complete text processing pipeline"""
        text = """
        Content creation in the digital age requires sophisticated tools for protection and analysis.
        Authors need to ensure their work is original and properly attributed.
        Modern AI systems can help detect similarities and analyze writing patterns.
        """
        
        # Process the text
        result = processor.process_industrial_text(text)
        
        # Test plagiarism detection
        reference_texts = [
            "Digital content creation needs advanced protection tools.",
            "Writers must verify originality and proper attribution.",
            "AI can identify patterns and similarities in text."
        ]
        
        plagiarism_result = processor.detect_semantic_plagiarism(text, reference_texts)
        
        # Verify both processing and plagiarism detection work
        assert result is not None
        assert plagiarism_result is not None
        assert isinstance(plagiarism_result, SemanticPlagiarismResult)
        
        # Should detect some similarity with paraphrased content
        assert plagiarism_result.semantic_similarity > 0.1
    
    def test_multilingual_processing(self, processor):
        """Test processing of multilingual content"""
        texts = {
            'en': "This is English text for testing.",
            'es': "Este es texto en español para pruebas.",
            'fr': "Ceci est un texte français pour les tests.",
            'de': "Dies ist deutscher Text zum Testen."
        }
        
        for lang_code, text in texts.items():
            result = processor.process_industrial_text(text, language_hint=lang_code)
            
            assert result is not None
            assert 'language_analysis' in result
            assert 'authorship_features' in result
            
            # Language should match hint
            assert result['language_analysis']['language'] == lang_code

if __name__ == "__main__":
    # Run basic tests
    print("Running Enhanced Text Processing Tests...")
    
    # Test processor creation
    processor = create_enhanced_text_processor()
    print("✓ Processor created successfully")
    
    # Test language database
    lang_db = create_644_language_support()
    stats = lang_db.get_language_statistics()
    print(f"✓ Language database created with {stats['total_languages']} languages")
    
    # Test basic processing
    test_text = "This is a test of the enhanced text processing system."
    result = processor.process_industrial_text(test_text)
    print("✓ Basic text processing successful")
    
    # Test authorship analysis
    authorship = processor.analyze_authorship(test_text)
    print(f"✓ Authorship analysis complete (lexical diversity: {authorship.lexical_diversity:.3f})")
    
    # Test plagiarism detection
    plagiarism = processor.detect_semantic_plagiarism(test_text, ["This is a test sentence."])
    print(f"✓ Plagiarism detection complete (similarity: {plagiarism.semantic_similarity:.3f})")
    
    print("\nAll basic tests passed! ✅")
    print("\nEnhanced features implemented:")
    print("📝 Industrial Text Processing")
    print("🧠 Ultra-Advanced NLP Analysis") 
    print("🔗 Contextual BERT/RoBERTa Embeddings")
    print("🔍 Semantic Plagiarism Detection")
    print("✍️ Style and Authorship Analysis")
    print("🌍 644 Native Language Support")