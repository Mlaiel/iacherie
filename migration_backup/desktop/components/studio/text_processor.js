/**
 * Ainflue Desktop - Professional Text Processor
 * 
 * Advanced text editing and processing tools for content creators
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

const { EventEmitter } = require('events');

class TextProcessor extends EventEmitter {
  constructor() {
    super();
    this.document = null;
    this.history = [];
    this.historyIndex = -1;
    this.formats = new Map();
    this.plugins = new Map();
    this.spellChecker = null;
    this.grammarChecker = null;
    
    this.initializeFormats();
    this.initializePlugins();
  }

  /**
   * Initialize text formats
   */
  initializeFormats() {
    this.formats.set('markdown', {
      name: 'Markdown',
      extensions: ['.md', '.markdown'],
      parser: (text) => this.parseMarkdown(text),
      exporter: (doc) => this.exportMarkdown(doc)
    });

    this.formats.set('html', {
      name: 'HTML',
      extensions: ['.html', '.htm'],
      parser: (text) => this.parseHTML(text),
      exporter: (doc) => this.exportHTML(doc)
    });

    this.formats.set('plain', {
      name: 'Plain Text',
      extensions: ['.txt'],
      parser: (text) => this.parsePlainText(text),
      exporter: (doc) => this.exportPlainText(doc)
    });

    this.formats.set('rtf', {
      name: 'Rich Text Format',
      extensions: ['.rtf'],
      parser: (text) => this.parseRTF(text),
      exporter: (doc) => this.exportRTF(doc)
    });

    this.formats.set('json', {
      name: 'JSON Document',
      extensions: ['.json'],
      parser: (text) => this.parseJSON(text),
      exporter: (doc) => this.exportJSON(doc)
    });
  }

  /**
   * Initialize text processing plugins
   */
  initializePlugins() {
    this.plugins.set('wordCount', {
      name: 'Word Count',
      process: (text) => this.countWords(text)
    });

    this.plugins.set('readabilityScore', {
      name: 'Readability Score',
      process: (text) => this.calculateReadability(text)
    });

    this.plugins.set('sentimentAnalysis', {
      name: 'Sentiment Analysis',
      process: (text) => this.analyzeSentiment(text)
    });

    this.plugins.set('keywordExtractor', {
      name: 'Keyword Extractor',
      process: (text) => this.extractKeywords(text)
    });

    this.plugins.set('textSummarizer', {
      name: 'Text Summarizer',
      process: (text) => this.summarizeText(text)
    });

    this.plugins.set('languageDetector', {
      name: 'Language Detector',
      process: (text) => this.detectLanguage(text)
    });
  }

  /**
   * Create new document
   */
  createDocument(type = 'plain', content = '') {
    this.document = {
      id: Date.now().toString(),
      type,
      content,
      metadata: {
        created: new Date(),
        modified: new Date(),
        wordCount: 0,
        characterCount: 0,
        title: 'Untitled Document'
      },
      formatting: {
        font: 'Arial',
        fontSize: 12,
        lineHeight: 1.5,
        textAlign: 'left',
        color: '#000000',
        backgroundColor: '#ffffff'
      },
      structure: {
        headings: [],
        paragraphs: [],
        lists: [],
        links: [],
        images: []
      }
    };

    this.updateDocumentContent(content);
    this.saveState();
    
    this.emit('documentCreated', this.document);
    return this.document.id;
  }

  /**
   * Load document from text
   */
  async loadDocument(text, format = 'plain') {
    try {
      if (!this.formats.has(format)) {
        throw new Error(`Unsupported format: ${format}`);
      }

      const formatter = this.formats.get(format);
      const parsedDocument = formatter.parser(text);
      
      this.document = {
        ...parsedDocument,
        id: Date.now().toString(),
        metadata: {
          ...parsedDocument.metadata,
          loaded: new Date()
        }
      };

      this.analyzeDocument();
      this.saveState();
      
      this.emit('documentLoaded', { format, document: this.document });
      return this.document.id;
    } catch (error) {
      this.emit('error', new Error(`Failed to load document: ${error.message}`));
      return null;
    }
  }

  /**
   * Update document content
   */
  updateDocumentContent(content) {
    if (!this.document) return false;

    this.document.content = content;
    this.document.metadata.modified = new Date();
    
    this.analyzeDocument();
    this.saveState();
    
    this.emit('contentChanged', {
      wordCount: this.document.metadata.wordCount,
      characterCount: this.document.metadata.characterCount
    });
    
    return true;
  }

  /**
   * Analyze document structure and metadata
   */
  analyzeDocument() {
    if (!this.document) return;

    const content = this.document.content;
    
    // Update basic metrics
    this.document.metadata.wordCount = this.countWords(content).words;
    this.document.metadata.characterCount = content.length;
    
    // Analyze structure
    this.document.structure = {
      headings: this.extractHeadings(content),
      paragraphs: this.extractParagraphs(content),
      lists: this.extractLists(content),
      links: this.extractLinks(content),
      images: this.extractImages(content)
    };
  }

  /**
   * Count words in text
   */
  countWords(text) {
    const words = text.trim().split(/\s+/).filter(word => word.length > 0);
    const sentences = text.split(/[.!?]+/).filter(sentence => sentence.trim().length > 0);
    const paragraphs = text.split(/\n\s*\n/).filter(para => para.trim().length > 0);
    
    return {
      words: words.length,
      characters: text.length,
      charactersNoSpaces: text.replace(/\s/g, '').length,
      sentences: sentences.length,
      paragraphs: paragraphs.length,
      averageWordsPerSentence: sentences.length > 0 ? Math.round(words.length / sentences.length) : 0,
      averageSentencesPerParagraph: paragraphs.length > 0 ? Math.round(sentences.length / paragraphs.length) : 0
    };
  }

  /**
   * Calculate readability score (Flesch Reading Ease)
   */
  calculateReadability(text) {
    const stats = this.countWords(text);
    
    if (stats.sentences === 0 || stats.words === 0) {
      return { score: 0, level: 'N/A' };
    }

    const avgSentenceLength = stats.words / stats.sentences;
    const avgSyllablesPerWord = this.countSyllables(text) / stats.words;
    
    const score = 206.835 - (1.015 * avgSentenceLength) - (84.6 * avgSyllablesPerWord);
    
    let level;
    if (score >= 90) level = 'Very Easy';
    else if (score >= 80) level = 'Easy';
    else if (score >= 70) level = 'Fairly Easy';
    else if (score >= 60) level = 'Standard';
    else if (score >= 50) level = 'Fairly Difficult';
    else if (score >= 30) level = 'Difficult';
    else level = 'Very Difficult';
    
    return {
      score: Math.round(score),
      level,
      avgSentenceLength: Math.round(avgSentenceLength * 10) / 10,
      avgSyllablesPerWord: Math.round(avgSyllablesPerWord * 10) / 10
    };
  }

  /**
   * Count syllables in text (approximation)
   */
  countSyllables(text) {
    const words = text.toLowerCase().match(/\b\w+\b/g) || [];
    let syllableCount = 0;
    
    words.forEach(word => {
      const vowels = word.match(/[aeiouy]+/g) || [];
      let count = vowels.length;
      
      // Adjust for silent e
      if (word.endsWith('e') && count > 1) count--;
      
      // Minimum one syllable per word
      if (count === 0) count = 1;
      
      syllableCount += count;
    });
    
    return syllableCount;
  }

  /**
   * Analyze sentiment of text
   */
  analyzeSentiment(text) {
    // Simplified sentiment analysis
    const positiveWords = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'happy', 'joy'];
    const negativeWords = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'sad', 'angry', 'disappointed'];
    
    const words = text.toLowerCase().match(/\b\w+\b/g) || [];
    let positiveCount = 0;
    let negativeCount = 0;
    
    words.forEach(word => {
      if (positiveWords.includes(word)) positiveCount++;
      if (negativeWords.includes(word)) negativeCount++;
    });
    
    const total = positiveCount + negativeCount;
    let sentiment = 'neutral';
    let score = 0;
    
    if (total > 0) {
      score = (positiveCount - negativeCount) / total;
      if (score > 0.2) sentiment = 'positive';
      else if (score < -0.2) sentiment = 'negative';
    }
    
    return {
      sentiment,
      score: Math.round(score * 100) / 100,
      positive: positiveCount,
      negative: negativeCount,
      total: words.length
    };
  }

  /**
   * Extract keywords from text
   */
  extractKeywords(text, limit = 10) {
    // Simple keyword extraction based on frequency
    const stopWords = new Set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'shall', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them']);
    
    const words = text.toLowerCase()
      .match(/\b\w{3,}\b/g) || []
      .filter(word => !stopWords.has(word));
    
    const frequency = {};
    words.forEach(word => {
      frequency[word] = (frequency[word] || 0) + 1;
    });
    
    return Object.entries(frequency)
      .sort(([,a], [,b]) => b - a)
      .slice(0, limit)
      .map(([word, count]) => ({ word, count, frequency: count / words.length }));
  }

  /**
   * Summarize text (extractive summary)
   */
  summarizeText(text, maxSentences = 3) {
    const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 10);
    
    if (sentences.length <= maxSentences) {
      return {
        summary: text,
        original: sentences.length,
        summarized: sentences.length,
        compression: 1.0
      };
    }
    
    // Score sentences based on word frequency
    const words = text.toLowerCase().match(/\b\w+\b/g) || [];
    const wordFreq = {};
    words.forEach(word => {
      wordFreq[word] = (wordFreq[word] || 0) + 1;
    });
    
    const sentenceScores = sentences.map(sentence => {
      const sentenceWords = sentence.toLowerCase().match(/\b\w+\b/g) || [];
      const score = sentenceWords.reduce((sum, word) => sum + (wordFreq[word] || 0), 0) / sentenceWords.length;
      return { sentence: sentence.trim(), score };
    });
    
    const topSentences = sentenceScores
      .sort((a, b) => b.score - a.score)
      .slice(0, maxSentences)
      .sort((a, b) => sentences.indexOf(a.sentence) - sentences.indexOf(b.sentence));
    
    const summary = topSentences.map(s => s.sentence).join('. ') + '.';
    
    return {
      summary,
      original: sentences.length,
      summarized: maxSentences,
      compression: maxSentences / sentences.length
    };
  }

  /**
   * Detect language of text
   */
  detectLanguage(text) {
    // Simplified language detection based on common words
    const languages = {
      english: ['the', 'and', 'of', 'to', 'a', 'in', 'is', 'it', 'you', 'that'],
      german: ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich'],
      french: ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir'],
      spanish: ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se'],
      arabic: ['في', 'من', 'إلى', 'على', 'هذا', 'هذه', 'التي', 'الذي', 'كان', 'كل']
    };
    
    const words = text.toLowerCase().match(/\b\w+\b/g) || [];
    const scores = {};
    
    Object.entries(languages).forEach(([lang, commonWords]) => {
      scores[lang] = words.filter(word => commonWords.includes(word)).length;
    });
    
    const detectedLang = Object.entries(scores).reduce((a, b) => scores[a[0]] > scores[b[0]] ? a : b);
    const confidence = detectedLang[1] / words.length;
    
    return {
      language: detectedLang[0],
      confidence: Math.round(confidence * 100) / 100,
      scores
    };
  }

  /**
   * Extract headings from text
   */
  extractHeadings(text) {
    const headings = [];
    const lines = text.split('\n');
    
    lines.forEach((line, index) => {
      // Markdown style headings
      const mdMatch = line.match(/^(#{1,6})\s+(.+)$/);
      if (mdMatch) {
        headings.push({
          level: mdMatch[1].length,
          text: mdMatch[2],
          line: index
        });
      }
    });
    
    return headings;
  }

  /**
   * Extract paragraphs from text
   */
  extractParagraphs(text) {
    return text.split(/\n\s*\n/)
      .filter(para => para.trim().length > 0)
      .map((para, index) => ({
        index,
        text: para.trim(),
        wordCount: this.countWords(para).words
      }));
  }

  /**
   * Extract lists from text
   */
  extractLists(text) {
    const lists = [];
    const lines = text.split('\n');
    let currentList = null;
    
    lines.forEach((line, index) => {
      const listMatch = line.match(/^(\s*)([-*+]|\d+\.)\s+(.+)$/);
      
      if (listMatch) {
        const [, indent, marker, content] = listMatch;
        const level = Math.floor(indent.length / 2);
        const isOrdered = /\d+\./.test(marker);
        
        if (!currentList || currentList.type !== (isOrdered ? 'ordered' : 'unordered')) {
          currentList = {
            type: isOrdered ? 'ordered' : 'unordered',
            startLine: index,
            items: []
          };
          lists.push(currentList);
        }
        
        currentList.items.push({
          level,
          content,
          line: index
        });
      } else if (currentList && line.trim() === '') {
        // Continue current list
      } else if (currentList) {
        currentList.endLine = index - 1;
        currentList = null;
      }
    });
    
    return lists;
  }

  /**
   * Extract links from text
   */
  extractLinks(text) {
    const links = [];
    
    // Markdown links
    const mdLinks = text.matchAll(/\[([^\]]+)\]\(([^)]+)\)/g);
    for (const match of mdLinks) {
      links.push({
        type: 'markdown',
        text: match[1],
        url: match[2],
        position: match.index
      });
    }
    
    // Plain URLs
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const urls = text.matchAll(urlRegex);
    for (const match of urls) {
      links.push({
        type: 'url',
        text: match[1],
        url: match[1],
        position: match.index
      });
    }
    
    return links;
  }

  /**
   * Extract images from text
   */
  extractImages(text) {
    const images = [];
    
    // Markdown images
    const mdImages = text.matchAll(/!\[([^\]]*)\]\(([^)]+)\)/g);
    for (const match of mdImages) {
      images.push({
        type: 'markdown',
        alt: match[1],
        src: match[2],
        position: match.index
      });
    }
    
    return images;
  }

  /**
   * Format text with styles
   */
  formatText(startPos, endPos, formatting) {
    if (!this.document) return false;
    
    // This would typically integrate with a rich text editor
    // For now, we'll store formatting metadata
    if (!this.document.formatting.ranges) {
      this.document.formatting.ranges = [];
    }
    
    this.document.formatting.ranges.push({
      start: startPos,
      end: endPos,
      style: formatting
    });
    
    this.saveState();
    this.emit('textFormatted', { startPos, endPos, formatting });
    return true;
  }

  /**
   * Export document in specified format
   */
  exportDocument(format = 'plain') {
    if (!this.document || !this.formats.has(format)) return null;
    
    try {
      const formatter = this.formats.get(format);
      const exported = formatter.exporter(this.document);
      
      this.emit('documentExported', { format, size: exported.length });
      return exported;
    } catch (error) {
      this.emit('error', new Error(`Failed to export document: ${error.message}`));
      return null;
    }
  }

  /**
   * Parse markdown text
   */
  parseMarkdown(text) {
    return {
      type: 'markdown',
      content: text,
      metadata: {
        created: new Date(),
        modified: new Date(),
        title: this.extractTitle(text),
        wordCount: this.countWords(text).words,
        characterCount: text.length
      },
      formatting: {
        font: 'Consolas',
        fontSize: 12,
        lineHeight: 1.6
      }
    };
  }

  /**
   * Parse plain text
   */
  parsePlainText(text) {
    return {
      type: 'plain',
      content: text,
      metadata: {
        created: new Date(),
        modified: new Date(),
        title: this.extractTitle(text),
        wordCount: this.countWords(text).words,
        characterCount: text.length
      },
      formatting: {
        font: 'Arial',
        fontSize: 12,
        lineHeight: 1.5
      }
    };
  }

  /**
   * Extract title from text
   */
  extractTitle(text) {
    const firstLine = text.split('\n')[0].trim();
    
    // Remove markdown heading markers
    const title = firstLine.replace(/^#+\s*/, '').substring(0, 50);
    
    return title || 'Untitled Document';
  }

  /**
   * Export as markdown
   */
  exportMarkdown(document) {
    return document.content;
  }

  /**
   * Export as plain text
   */
  exportPlainText(document) {
    return document.content.replace(/[#*_`\[\]()]/g, '');
  }

  /**
   * Save current state
   */
  saveState() {
    if (!this.document) return;
    
    if (this.historyIndex < this.history.length - 1) {
      this.history = this.history.slice(0, this.historyIndex + 1);
    }
    
    this.history.push(JSON.parse(JSON.stringify(this.document)));
    this.historyIndex++;
    
    if (this.history.length > 50) {
      this.history.shift();
      this.historyIndex--;
    }
    
    this.emit('stateChanged', {
      canUndo: this.canUndo(),
      canRedo: this.canRedo()
    });
  }

  /**
   * Undo last action
   */
  undo() {
    if (!this.canUndo()) return false;
    
    this.historyIndex--;
    this.document = JSON.parse(JSON.stringify(this.history[this.historyIndex]));
    
    this.emit('documentChanged', this.document);
    return true;
  }

  /**
   * Redo last action
   */
  redo() {
    if (!this.canRedo()) return false;
    
    this.historyIndex++;
    this.document = JSON.parse(JSON.stringify(this.history[this.historyIndex]));
    
    this.emit('documentChanged', this.document);
    return true;
  }

  /**
   * Check if can undo
   */
  canUndo() {
    return this.historyIndex > 0;
  }

  /**
   * Check if can redo
   */
  canRedo() {
    return this.historyIndex < this.history.length - 1;
  }

  /**
   * Get available formats
   */
  getAvailableFormats() {
    return Array.from(this.formats.entries()).map(([key, format]) => ({
      id: key,
      name: format.name,
      extensions: format.extensions
    }));
  }

  /**
   * Get available plugins
   */
  getAvailablePlugins() {
    return Array.from(this.plugins.entries()).map(([key, plugin]) => ({
      id: key,
      name: plugin.name
    }));
  }

  /**
   * Run plugin on current document
   */
  runPlugin(pluginId) {
    if (!this.document || !this.plugins.has(pluginId)) return null;
    
    const plugin = this.plugins.get(pluginId);
    const result = plugin.process(this.document.content);
    
    this.emit('pluginExecuted', { pluginId, result });
    return result;
  }
}

module.exports = TextProcessor;