#!/bin/bash
# spaCy Language Models Installation Script
# Part of Ainflue Platform critical dependency resolution
# Ref: docs/final/PRIORITIES_IMMEDIATES_100_COMPLETION.md

echo "🚀 Installing spaCy language models for Ainflue Platform..."
echo "Author: Fahed Mlaiel (mlaiel@live.de)"
echo

# Check if spaCy is installed
if ! python -c "import spacy" 2>/dev/null; then
    echo "❌ spaCy not found. Please install spaCy first:"
    echo "   pip install spacy"
    exit 1
fi

echo "✅ spaCy found. Installing language models..."

# Install English model
echo "📦 Installing English core model (en_core_web_sm)..."
python -m spacy download en_core_web_sm

# Install French model  
echo "📦 Installing French core model (fr_core_news_sm)..."
python -m spacy download fr_core_news_sm

echo
echo "🎉 spaCy language models installed successfully!"
echo "Available models:"
python -c "import spacy; print('  - English:', 'en_core_web_sm' in spacy.util.get_installed_models()); print('  - French:', 'fr_core_news_sm' in spacy.util.get_installed_models())"