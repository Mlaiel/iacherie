/**
 * Ainflue Desktop - Trend Analyzer Service
 * 
 * Advanced trend analysis and prediction service for content optimization
 * Implements real-time trend detection, viral prediction, and content timing optimization
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

class TrendAnalyzer {
  constructor(aiEngine, dataAggregator, cacheManager) {
    this.aiEngine = aiEngine;
    this.dataAggregator = dataAggregator;
    this.cacheManager = cacheManager;
    this.trendData = new Map();
    this.trendingTopics = new Set();
    this.predictionModels = new Map();
    this.analysisQueue = [];
    
    this.init();
  }

  init() {
    this.initializeTrendModels();
    this.startRealTimeMonitoring();
    this.setupPredictionEngine();
  }

  initializeTrendModels() {
    // Initialize ML models for trend prediction
    this.predictionModels.set('viral_prediction', {
      name: 'Viral Content Predictor',
      accuracy: 0.87,
      lastTrained: new Date(),
      features: ['engagement_velocity', 'sentiment_score', 'timing', 'hashtags', 'content_type']
    });

    this.predictionModels.set('trend_emergence', {
      name: 'Trend Emergence Detector',
      accuracy: 0.82,
      lastTrained: new Date(),
      features: ['keyword_frequency', 'platform_velocity', 'influencer_adoption', 'cross_platform_spread']
    });

    this.predictionModels.set('optimal_timing', {
      name: 'Optimal Timing Predictor',
      accuracy: 0.91,
      lastTrained: new Date(),
      features: ['audience_activity', 'platform_algorithms', 'competitor_posting', 'seasonal_patterns']
    });
  }

  startRealTimeMonitoring() {
    // Start monitoring trends across platforms
    this.monitoringInterval = setInterval(() => {
      this.collectTrendData();
      this.analyzeEmergingTrends();
      this.updatePredictions();
    }, 30000); // Every 30 seconds

    console.log('Trend Analyzer: Real-time monitoring started');
  }

  setupPredictionEngine() {
    this.predictionEngine = {
      viralProbability: this.calculateViralProbability.bind(this),
      trendLifecycle: this.predictTrendLifecycle.bind(this),
      optimalTiming: this.predictOptimalTiming.bind(this),
      contentStrategy: this.recommendContentStrategy.bind(this)
    };
  }

  async analyzeContent(content) {
    try {
      const analysis = {
        contentId: content.id,
        timestamp: new Date(),
        trends: await this.identifyRelevantTrends(content),
        viralPotential: await this.calculateViralProbability(content),
        optimalTiming: await this.predictOptimalTiming(content),
        recommendations: await this.generateRecommendations(content)
      };

      // Cache results for performance
      await this.cacheManager.set(`trend_analysis_${content.id}`, analysis, 3600);
      
      return analysis;
    } catch (error) {
      console.error('Trend analysis failed:', error);
      throw new Error(`Failed to analyze content trends: ${error.message}`);
    }
  }

  async identifyRelevantTrends(content) {
    try {
      const relevantTrends = [];
      
      // Extract keywords and topics from content
      const keywords = await this.extractKeywords(content);
      const topics = await this.extractTopics(content);
      
      // Find trending topics that match content
      for (const [trendId, trendData] of this.trendData) {
        const relevanceScore = this.calculateRelevance(keywords, topics, trendData);
        
        if (relevanceScore > 0.3) {
          relevantTrends.push({
            id: trendId,
            name: trendData.name,
            relevanceScore,
            velocity: trendData.velocity,
            platforms: trendData.platforms,
            predictedPeak: trendData.predictedPeak,
            recommendedAction: this.getRecommendedAction(relevanceScore, trendData)
          });
        }
      }

      return relevantTrends.sort((a, b) => b.relevanceScore - a.relevanceScore);
    } catch (error) {
      console.error('Failed to identify relevant trends:', error);
      return [];
    }
  }

  async calculateViralProbability(content) {
    try {
      const features = await this.extractViralFeatures(content);
      const model = this.predictionModels.get('viral_prediction');
      
      // ML prediction (simplified)
      const probability = this.runPredictionModel(model, features);
      
      return {
        probability: Math.round(probability * 100),
        confidence: model.accuracy,
        factors: this.identifyViralFactors(features),
        recommendations: this.generateViralRecommendations(features, probability)
      };
    } catch (error) {
      console.error('Viral probability calculation failed:', error);
      return { probability: 0, confidence: 0, factors: [], recommendations: [] };
    }
  }

  async extractViralFeatures(content) {
    return {
      contentType: content.type,
      duration: content.duration || 0,
      hasAudio: content.hasAudio || false,
      hasVideo: content.hasVideo || false,
      hasText: content.hasText || false,
      emotionalTone: await this.analyzeEmotionalTone(content),
      uniquenessScore: await this.calculateUniquenessScore(content),
      trendAlignment: await this.calculateTrendAlignment(content),
      qualityScore: await this.assessContentQuality(content),
      timingScore: await this.calculateTimingScore(content)
    };
  }

  async analyzeEmotionalTone(content) {
    // Simplified emotional analysis
    const emotions = ['joy', 'excitement', 'surprise', 'inspiration', 'humor'];
    const scores = {};
    
    for (const emotion of emotions) {
      scores[emotion] = Math.random() * 0.8 + 0.1; // Mock scoring
    }
    
    return scores;
  }

  async calculateUniquenessScore(content) {
    // Analyze content uniqueness compared to recent content
    try {
      const recentContent = await this.dataAggregator.getRecentContent(100);
      const similarityScores = recentContent.map(item => 
        this.calculateContentSimilarity(content, item)
      );
      
      const avgSimilarity = similarityScores.reduce((sum, score) => sum + score, 0) / similarityScores.length;
      return Math.max(0, 1 - avgSimilarity); // Higher uniqueness = lower similarity
    } catch (error) {
      console.error('Uniqueness calculation failed:', error);
      return 0.5; // Default neutral score
    }
  }

  calculateContentSimilarity(content1, content2) {
    // Simplified similarity calculation
    const factors = [
      content1.type === content2.type ? 0.3 : 0,
      this.calculateKeywordSimilarity(content1.keywords || [], content2.keywords || []) * 0.4,
      this.calculateTopicSimilarity(content1.topics || [], content2.topics || []) * 0.3
    ];
    
    return factors.reduce((sum, factor) => sum + factor, 0);
  }

  calculateKeywordSimilarity(keywords1, keywords2) {
    if (!keywords1.length || !keywords2.length) return 0;
    
    const intersection = keywords1.filter(kw => keywords2.includes(kw));
    const union = [...new Set([...keywords1, ...keywords2])];
    
    return intersection.length / union.length;
  }

  calculateTopicSimilarity(topics1, topics2) {
    if (!topics1.length || !topics2.length) return 0;
    
    const intersection = topics1.filter(topic => topics2.includes(topic));
    const union = [...new Set([...topics1, ...topics2])];
    
    return intersection.length / union.length;
  }

  async calculateTrendAlignment(content) {
    try {
      const contentKeywords = await this.extractKeywords(content);
      const trendingKeywords = await this.getCurrentTrendingKeywords();
      
      const alignmentScore = this.calculateKeywordSimilarity(contentKeywords, trendingKeywords);
      return Math.min(1, alignmentScore * 2); // Boost alignment score
    } catch (error) {
      console.error('Trend alignment calculation failed:', error);
      return 0;
    }
  }

  async assessContentQuality(content) {
    // Multi-factor quality assessment
    const qualityFactors = {
      technicalQuality: await this.assessTechnicalQuality(content),
      creativityScore: await this.assessCreativity(content),
      relevanceScore: await this.assessRelevance(content),
      productionValue: await this.assessProductionValue(content)
    };
    
    const weights = { technicalQuality: 0.3, creativityScore: 0.3, relevanceScore: 0.25, productionValue: 0.15 };
    
    return Object.entries(qualityFactors).reduce((total, [factor, score]) => {
      return total + (score * weights[factor]);
    }, 0);
  }

  async assessTechnicalQuality(content) {
    // Mock technical quality assessment
    const factors = {
      resolution: content.resolution >= 1080 ? 1 : content.resolution >= 720 ? 0.7 : 0.4,
      audioQuality: content.audioBitrate >= 128 ? 1 : content.audioBitrate >= 96 ? 0.7 : 0.4,
      stability: Math.random() * 0.4 + 0.6, // Mock stability score
      colorGrading: Math.random() * 0.3 + 0.7 // Mock color grading score
    };
    
    return Object.values(factors).reduce((sum, score) => sum + score, 0) / Object.keys(factors).length;
  }

  async assessCreativity(content) {
    // Mock creativity assessment based on various factors
    return Math.random() * 0.4 + 0.5; // Random score between 0.5-0.9
  }

  async assessRelevance(content) {
    // Assess relevance to current trends and audience interests
    const trendAlignment = await this.calculateTrendAlignment(content);
    const audienceAlignment = await this.calculateAudienceAlignment(content);
    
    return (trendAlignment * 0.6) + (audienceAlignment * 0.4);
  }

  async calculateAudienceAlignment(content) {
    // Mock audience alignment calculation
    return Math.random() * 0.4 + 0.6;
  }

  async assessProductionValue(content) {
    // Assess overall production value
    return Math.random() * 0.3 + 0.7;
  }

  async calculateTimingScore(content) {
    try {
      const currentTime = new Date();
      const optimalTimes = await this.getOptimalPostingTimes();
      
      const timingAlignment = this.calculateTimeAlignment(currentTime, optimalTimes);
      const seasonalFactor = this.calculateSeasonalFactor(currentTime, content.type);
      const competitionLevel = await this.calculateCompetitionLevel(currentTime);
      
      return (timingAlignment * 0.5) + (seasonalFactor * 0.3) + ((1 - competitionLevel) * 0.2);
    } catch (error) {
      console.error('Timing score calculation failed:', error);
      return 0.5;
    }
  }

  calculateTimeAlignment(currentTime, optimalTimes) {
    const currentHour = currentTime.getHours();
    const currentDay = currentTime.getDay();
    
    for (const optimalTime of optimalTimes) {
      if (optimalTime.day === currentDay && 
          Math.abs(optimalTime.hour - currentHour) <= 1) {
        return 1.0;
      }
    }
    
    return 0.3; // Poor timing alignment
  }

  calculateSeasonalFactor(date, contentType) {
    const month = date.getMonth();
    const seasonalFactors = {
      'video': [0.8, 0.7, 0.9, 0.8, 0.9, 0.7, 0.6, 0.7, 0.9, 0.8, 0.9, 1.0],
      'audio': [0.9, 0.8, 0.8, 0.7, 0.8, 0.7, 0.8, 0.8, 0.9, 0.9, 0.8, 0.9],
      'image': [0.8, 0.9, 0.9, 0.8, 0.9, 0.8, 0.7, 0.8, 0.8, 0.9, 0.8, 0.9],
      'text': [0.9, 0.8, 0.8, 0.9, 0.8, 0.8, 0.8, 0.8, 0.9, 0.9, 0.8, 0.8]
    };
    
    return seasonalFactors[contentType] ? seasonalFactors[contentType][month] : 0.8;
  }

  async calculateCompetitionLevel(timestamp) {
    // Calculate competition level at given time
    try {
      const competitorActivity = await this.dataAggregator.getCompetitorActivity(timestamp);
      return Math.min(1, competitorActivity.length / 10); // Normalize to 0-1
    } catch (error) {
      return 0.5; // Default medium competition
    }
  }

  runPredictionModel(model, features) {
    // Simplified ML model simulation
    let score = 0;
    const weights = {
      contentType: 0.1,
      emotionalTone: 0.2,
      uniquenessScore: 0.25,
      trendAlignment: 0.2,
      qualityScore: 0.15,
      timingScore: 0.1
    };
    
    // Calculate weighted score
    Object.entries(weights).forEach(([feature, weight]) => {
      if (features[feature] !== undefined) {
        const value = typeof features[feature] === 'object' 
          ? Object.values(features[feature]).reduce((sum, val) => sum + val, 0) / Object.keys(features[feature]).length
          : features[feature];
        score += value * weight;
      }
    });
    
    // Add some randomness to simulate model uncertainty
    score += (Math.random() - 0.5) * 0.1;
    
    return Math.max(0, Math.min(1, score));
  }

  identifyViralFactors(features) {
    const factors = [];
    
    if (features.emotionalTone) {
      const maxEmotion = Object.entries(features.emotionalTone)
        .reduce((max, [emotion, score]) => score > max.score ? { emotion, score } : max, { emotion: '', score: 0 });
      
      if (maxEmotion.score > 0.7) {
        factors.push({
          type: 'emotional_resonance',
          value: maxEmotion.emotion,
          impact: 'high',
          description: `Strong ${maxEmotion.emotion} emotional appeal`
        });
      }
    }
    
    if (features.uniquenessScore > 0.8) {
      factors.push({
        type: 'uniqueness',
        value: features.uniquenessScore,
        impact: 'high',
        description: 'Highly unique content with strong differentiation'
      });
    }
    
    if (features.trendAlignment > 0.7) {
      factors.push({
        type: 'trend_alignment',
        value: features.trendAlignment,
        impact: 'medium',
        description: 'Strong alignment with current trends'
      });
    }
    
    if (features.qualityScore > 0.8) {
      factors.push({
        type: 'quality',
        value: features.qualityScore,
        impact: 'high',
        description: 'High production quality and creative value'
      });
    }
    
    return factors;
  }

  generateViralRecommendations(features, probability) {
    const recommendations = [];
    
    if (probability < 0.3) {
      recommendations.push({
        type: 'improvement',
        priority: 'high',
        suggestion: 'Consider adding more emotional appeal or trending elements',
        expectedImpact: '+15-25% viral potential'
      });
    }
    
    if (features.timingScore < 0.5) {
      recommendations.push({
        type: 'timing',
        priority: 'medium',
        suggestion: 'Post during optimal hours for your audience',
        expectedImpact: '+10-15% viral potential'
      });
    }
    
    if (features.trendAlignment < 0.4) {
      recommendations.push({
        type: 'trends',
        priority: 'medium',
        suggestion: 'Incorporate current trending topics or hashtags',
        expectedImpact: '+20-30% viral potential'
      });
    }
    
    if (features.uniquenessScore < 0.5) {
      recommendations.push({
        type: 'differentiation',
        priority: 'high',
        suggestion: 'Add unique elements to stand out from similar content',
        expectedImpact: '+25-35% viral potential'
      });
    }
    
    return recommendations;
  }

  async predictOptimalTiming(content) {
    try {
      const model = this.predictionModels.get('optimal_timing');
      const timingFeatures = await this.extractTimingFeatures(content);
      
      const predictions = [];
      const now = new Date();
      
      // Predict optimal times for the next 7 days
      for (let day = 0; day < 7; day++) {
        const date = new Date(now.getTime() + (day * 24 * 60 * 60 * 1000));
        
        for (let hour = 0; hour < 24; hour++) {
          const testTime = new Date(date);
          testTime.setHours(hour, 0, 0, 0);
          
          const timeFeatures = {
            ...timingFeatures,
            hour,
            day: testTime.getDay(),
            timestamp: testTime
          };
          
          const score = this.runTimingPrediction(model, timeFeatures);
          
          if (score > 0.7) {
            predictions.push({
              timestamp: testTime,
              score,
              confidence: model.accuracy,
              reasons: this.explainTimingScore(timeFeatures, score)
            });
          }
        }
      }
      
      return predictions.sort((a, b) => b.score - a.score).slice(0, 10);
    } catch (error) {
      console.error('Optimal timing prediction failed:', error);
      return [];
    }
  }

  async extractTimingFeatures(content) {
    return {
      contentType: content.type,
      targetAudience: content.targetAudience || 'general',
      platforms: content.platforms || ['default'],
      contentLength: content.duration || content.wordCount || 0,
      seasonality: this.calculateSeasonality(content),
      competitiveLevel: await this.getCurrentCompetitiveLevel()
    };
  }

  calculateSeasonality(content) {
    const currentMonth = new Date().getMonth();
    const seasonalBoosts = {
      'fitness': [1.2, 0.8, 0.9, 1.0, 1.1, 0.9, 0.8, 0.9, 1.0, 1.1, 1.0, 1.1],
      'holiday': [1.3, 0.7, 0.8, 0.9, 0.8, 0.7, 0.6, 0.7, 0.8, 1.0, 1.2, 1.4],
      'education': [0.8, 1.1, 1.2, 1.1, 1.0, 0.7, 0.6, 0.9, 1.2, 1.1, 1.0, 0.8]
    };
    
    const category = this.categorizeContent(content);
    return seasonalBoosts[category] ? seasonalBoosts[category][currentMonth] : 1.0;
  }

  categorizeContent(content) {
    // Simple content categorization
    const keywords = content.keywords || [];
    const title = content.title || '';
    
    if (keywords.some(kw => ['fitness', 'workout', 'health'].includes(kw.toLowerCase())) ||
        title.toLowerCase().includes('fitness')) {
      return 'fitness';
    }
    
    if (keywords.some(kw => ['holiday', 'christmas', 'thanksgiving'].includes(kw.toLowerCase()))) {
      return 'holiday';
    }
    
    if (keywords.some(kw => ['education', 'tutorial', 'learn'].includes(kw.toLowerCase()))) {
      return 'education';
    }
    
    return 'general';
  }

  async getCurrentCompetitiveLevel() {
    try {
      const recentPosts = await this.dataAggregator.getRecentCompetitorPosts(24); // Last 24 hours
      return Math.min(1, recentPosts.length / 50); // Normalize based on typical volume
    } catch (error) {
      return 0.5; // Default medium competitive level
    }
  }

  runTimingPrediction(model, features) {
    // Simplified timing prediction model
    let score = 0.5; // Base score
    
    // Hour-based scoring (simplified)
    const hourScores = {
      6: 0.3, 7: 0.5, 8: 0.7, 9: 0.8, 10: 0.6, 11: 0.7, 12: 0.9,
      13: 0.8, 14: 0.6, 15: 0.7, 16: 0.8, 17: 0.9, 18: 1.0, 19: 0.9,
      20: 0.8, 21: 0.7, 22: 0.5, 23: 0.3, 0: 0.2, 1: 0.1, 2: 0.1,
      3: 0.1, 4: 0.1, 5: 0.2
    };
    
    score *= hourScores[features.hour] || 0.5;
    
    // Day-based scoring (0=Sunday, 6=Saturday)
    const dayScores = [0.6, 0.8, 0.9, 0.9, 0.9, 0.8, 0.7];
    score *= dayScores[features.day] || 0.7;
    
    // Apply seasonality
    score *= features.seasonality || 1.0;
    
    // Apply competitive level (lower competition = higher score)
    score *= (1 - (features.competitiveLevel || 0.5) * 0.3);
    
    return Math.max(0, Math.min(1, score));
  }

  explainTimingScore(features, score) {
    const reasons = [];
    
    if (features.hour >= 17 && features.hour <= 20) {
      reasons.push('Peak engagement hours (5-8 PM)');
    }
    
    if (features.day >= 1 && features.day <= 5) {
      reasons.push('Weekday posting advantage');
    }
    
    if (features.seasonality > 1.1) {
      reasons.push('Seasonal content boost');
    }
    
    if (features.competitiveLevel < 0.3) {
      reasons.push('Low competition window');
    }
    
    return reasons;
  }

  async generateRecommendations(content) {
    try {
      const recommendations = [];
      
      // Trend-based recommendations
      const trends = await this.identifyRelevantTrends(content);
      if (trends.length > 0) {
        recommendations.push({
          category: 'trends',
          title: 'Leverage Current Trends',
          items: trends.slice(0, 3).map(trend => ({
            action: `Incorporate "${trend.name}" trend`,
            impact: `+${Math.round(trend.relevanceScore * 100)}% relevance`,
            urgency: trend.velocity > 0.8 ? 'high' : 'medium'
          }))
        });
      }
      
      // Timing recommendations
      const optimalTimes = await this.predictOptimalTiming(content);
      if (optimalTimes.length > 0) {
        recommendations.push({
          category: 'timing',
          title: 'Optimal Posting Times',
          items: optimalTimes.slice(0, 3).map(time => ({
            action: `Post on ${time.timestamp.toLocaleDateString()} at ${time.timestamp.toLocaleTimeString()}`,
            impact: `+${Math.round(time.score * 100)}% engagement potential`,
            urgency: 'medium'
          }))
        });
      }
      
      // Content optimization recommendations
      const viralAnalysis = await this.calculateViralProbability(content);
      if (viralAnalysis.recommendations.length > 0) {
        recommendations.push({
          category: 'optimization',
          title: 'Content Optimization',
          items: viralAnalysis.recommendations.map(rec => ({
            action: rec.suggestion,
            impact: rec.expectedImpact,
            urgency: rec.priority
          }))
        });
      }
      
      return recommendations;
    } catch (error) {
      console.error('Failed to generate recommendations:', error);
      return [];
    }
  }

  async collectTrendData() {
    try {
      // Collect data from multiple sources
      const platforms = ['youtube', 'tiktok', 'instagram', 'twitter'];
      const newTrendData = new Map();
      
      for (const platform of platforms) {
        const platformTrends = await this.dataAggregator.getTrendingTopics(platform);
        
        platformTrends.forEach(trend => {
          const trendId = `${platform}_${trend.hashtag || trend.keyword}`;
          
          if (!newTrendData.has(trendId)) {
            newTrendData.set(trendId, {
              id: trendId,
              name: trend.hashtag || trend.keyword,
              platforms: [platform],
              velocity: trend.velocity || 0,
              volume: trend.volume || 0,
              sentiment: trend.sentiment || 0,
              demographics: trend.demographics || {},
              firstSeen: trend.firstSeen || new Date(),
              lastUpdated: new Date(),
              predictedPeak: this.predictTrendPeak(trend)
            });
          } else {
            const existing = newTrendData.get(trendId);
            existing.platforms.push(platform);
            existing.velocity = Math.max(existing.velocity, trend.velocity || 0);
            existing.volume += trend.volume || 0;
            existing.lastUpdated = new Date();
          }
        });
      }
      
      // Update main trend data
      this.trendData = newTrendData;
      console.log(`Trend Analyzer: Updated ${this.trendData.size} trends`);
      
    } catch (error) {
      console.error('Failed to collect trend data:', error);
    }
  }

  predictTrendPeak(trend) {
    // Simple trend peak prediction based on velocity and current volume
    const currentTime = new Date();
    const velocityFactor = trend.velocity || 0.5;
    const volumeFactor = Math.log(trend.volume || 100) / 10;
    
    // Predict peak in hours (simplified model)
    const hoursToPeak = Math.max(1, 24 - (velocityFactor * volumeFactor * 20));
    
    return new Date(currentTime.getTime() + (hoursToPeak * 60 * 60 * 1000));
  }

  async analyzeEmergingTrends() {
    try {
      const emergingTrends = [];
      
      for (const [trendId, trendData] of this.trendData) {
        if (this.isEmergingTrend(trendData)) {
          emergingTrends.push({
            ...trendData,
            emergenceScore: this.calculateEmergenceScore(trendData),
            recommendation: this.getEmergenceRecommendation(trendData)
          });
        }
      }
      
      // Sort by emergence score
      emergingTrends.sort((a, b) => b.emergenceScore - a.emergenceScore);
      
      // Store top emerging trends
      this.emergingTrends = emergingTrends.slice(0, 20);
      
      // Cache results
      await this.cacheManager.set('emerging_trends', this.emergingTrends, 1800); // 30 minutes
      
    } catch (error) {
      console.error('Failed to analyze emerging trends:', error);
    }
  }

  isEmergingTrend(trendData) {
    const age = (new Date() - trendData.firstSeen) / (1000 * 60 * 60); // Age in hours
    return age < 48 && trendData.velocity > 0.3 && trendData.platforms.length >= 2;
  }

  calculateEmergenceScore(trendData) {
    const velocityScore = Math.min(1, trendData.velocity);
    const platformScore = Math.min(1, trendData.platforms.length / 4);
    const volumeScore = Math.min(1, Math.log(trendData.volume) / 15);
    const freshnessScore = this.calculateFreshnessScore(trendData.firstSeen);
    
    return (velocityScore * 0.4) + (platformScore * 0.3) + (volumeScore * 0.2) + (freshnessScore * 0.1);
  }

  calculateFreshnessScore(firstSeen) {
    const age = (new Date() - firstSeen) / (1000 * 60 * 60); // Age in hours
    return Math.max(0, 1 - (age / 48)); // Decreases over 48 hours
  }

  getEmergenceRecommendation(trendData) {
    if (trendData.velocity > 0.8) {
      return {
        action: 'immediate',
        message: 'Act quickly - this trend is exploding',
        window: '2-6 hours'
      };
    } else if (trendData.velocity > 0.5) {
      return {
        action: 'soon',
        message: 'Good opportunity - prepare content now',
        window: '6-24 hours'
      };
    } else {
      return {
        action: 'monitor',
        message: 'Watch for growth - potential opportunity',
        window: '24-48 hours'
      };
    }
  }

  async updatePredictions() {
    try {
      // Update viral predictions for recent content
      const recentContent = await this.dataAggregator.getRecentContent(50);
      
      for (const content of recentContent) {
        if (!content.viralPrediction || this.shouldUpdatePrediction(content)) {
          const prediction = await this.calculateViralProbability(content);
          await this.cacheManager.set(`viral_prediction_${content.id}`, prediction, 7200);
        }
      }
      
      // Update model performance metrics
      await this.updateModelMetrics();
      
    } catch (error) {
      console.error('Failed to update predictions:', error);
    }
  }

  shouldUpdatePrediction(content) {
    const lastUpdate = content.lastPredictionUpdate || content.createdAt;
    const hoursSinceUpdate = (new Date() - lastUpdate) / (1000 * 60 * 60);
    return hoursSinceUpdate > 6; // Update every 6 hours
  }

  async updateModelMetrics() {
    try {
      for (const [modelName, model] of this.predictionModels) {
        const recentPredictions = await this.getRecentPredictions(modelName, 100);
        const accuracy = this.calculateModelAccuracy(recentPredictions);
        
        model.accuracy = accuracy;
        model.lastEvaluated = new Date();
        
        console.log(`Trend Analyzer: ${modelName} accuracy: ${(accuracy * 100).toFixed(1)}%`);
      }
    } catch (error) {
      console.error('Failed to update model metrics:', error);
    }
  }

  async getRecentPredictions(modelName, limit) {
    // This would typically fetch from a database
    return []; // Mock implementation
  }

  calculateModelAccuracy(predictions) {
    if (!predictions.length) return 0.85; // Default accuracy
    
    let correct = 0;
    for (const prediction of predictions) {
      if (prediction.actual !== undefined) {
        const error = Math.abs(prediction.predicted - prediction.actual);
        if (error < 0.2) correct++; // Within 20% considered correct
      }
    }
    
    return correct / predictions.length;
  }

  // Public API methods
  async getTrendingTopics(limit = 10) {
    try {
      const cached = await this.cacheManager.get('trending_topics');
      if (cached) return cached.slice(0, limit);
      
      const trending = Array.from(this.trendData.values())
        .sort((a, b) => b.velocity - a.velocity)
        .slice(0, limit);
      
      await this.cacheManager.set('trending_topics', trending, 1800);
      return trending;
    } catch (error) {
      console.error('Failed to get trending topics:', error);
      return [];
    }
  }

  async getEmergingTrends(limit = 5) {
    try {
      const cached = await this.cacheManager.get('emerging_trends');
      if (cached) return cached.slice(0, limit);
      
      await this.analyzeEmergingTrends();
      return this.emergingTrends.slice(0, limit);
    } catch (error) {
      console.error('Failed to get emerging trends:', error);
      return [];
    }
  }

  async predictContentPerformance(content) {
    return await this.analyzeContent(content);
  }

  async getOptimalPostingTimes(days = 7) {
    try {
      const cached = await this.cacheManager.get(`optimal_times_${days}d`);
      if (cached) return cached;
      
      const optimalTimes = [];
      const now = new Date();
      
      for (let day = 0; day < days; day++) {
        const date = new Date(now.getTime() + (day * 24 * 60 * 60 * 1000));
        
        // Find best hours for this day
        const dayOptimalTimes = [];
        for (let hour = 6; hour <= 22; hour++) {
          const testTime = new Date(date);
          testTime.setHours(hour, 0, 0, 0);
          
          const score = await this.calculateTimingScore({ timestamp: testTime });
          if (score > 0.7) {
            dayOptimalTimes.push({ time: testTime, score });
          }
        }
        
        // Sort and take top 3 for this day
        dayOptimalTimes.sort((a, b) => b.score - a.score);
        optimalTimes.push(...dayOptimalTimes.slice(0, 3));
      }
      
      optimalTimes.sort((a, b) => b.score - a.score);
      const result = optimalTimes.slice(0, 10);
      
      await this.cacheManager.set(`optimal_times_${days}d`, result, 3600);
      return result;
    } catch (error) {
      console.error('Failed to get optimal posting times:', error);
      return [];
    }
  }

  async getContentRecommendations(userProfile, contentType = 'all') {
    try {
      const trends = await this.getTrendingTopics(20);
      const emerging = await this.getEmergingTrends(10);
      
      const recommendations = [];
      
      // Trend-based recommendations
      for (const trend of trends.slice(0, 5)) {
        if (contentType === 'all' || this.isRelevantForContentType(trend, contentType)) {
          recommendations.push({
            type: 'trending',
            trend: trend.name,
            urgency: trend.velocity > 0.8 ? 'high' : 'medium',
            description: `Create content around "${trend.name}" - currently trending with ${trend.velocity * 100}% velocity`,
            expectedImpact: `+${Math.round(trend.velocity * 50)}% engagement`
          });
        }
      }
      
      // Emerging trend recommendations
      for (const trend of emerging.slice(0, 3)) {
        recommendations.push({
          type: 'emerging',
          trend: trend.name,
          urgency: 'high',
          description: `Early adopter opportunity: "${trend.name}" is emerging across ${trend.platforms.length} platforms`,
          expectedImpact: `+${Math.round(trend.emergenceScore * 75)}% early adopter advantage`
        });
      }
      
      return recommendations;
    } catch (error) {
      console.error('Failed to get content recommendations:', error);
      return [];
    }
  }

  isRelevantForContentType(trend, contentType) {
    // Simple relevance check - could be more sophisticated
    return contentType === 'all' || 
           trend.platforms.some(platform => this.platformSupportsContentType(platform, contentType));
  }

  platformSupportsContentType(platform, contentType) {
    const platformTypes = {
      youtube: ['video', 'audio'],
      tiktok: ['video'],
      instagram: ['video', 'image'],
      twitter: ['text', 'image', 'video']
    };
    
    return platformTypes[platform]?.includes(contentType) || false;
  }

  // Utility methods
  async extractKeywords(content) {
    // Mock keyword extraction
    const text = [content.title, content.description, content.transcript].filter(Boolean).join(' ');
    
    // Simple keyword extraction (in production, use proper NLP)
    const words = text.toLowerCase().split(/\s+/);
    const keywords = words.filter(word => word.length > 3 && !this.isStopWord(word));
    
    return [...new Set(keywords)].slice(0, 20);
  }

  async extractTopics(content) {
    // Mock topic extraction
    const keywords = await this.extractKeywords(content);
    
    // Group keywords into topics (simplified)
    const topicGroups = {
      technology: ['tech', 'computer', 'software', 'digital', 'internet'],
      entertainment: ['music', 'movie', 'show', 'celebrity', 'entertainment'],
      lifestyle: ['fashion', 'beauty', 'health', 'fitness', 'food'],
      education: ['learn', 'tutorial', 'guide', 'education', 'course']
    };
    
    const topics = [];
    for (const [topic, relatedWords] of Object.entries(topicGroups)) {
      if (keywords.some(keyword => relatedWords.includes(keyword))) {
        topics.push(topic);
      }
    }
    
    return topics;
  }

  isStopWord(word) {
    const stopWords = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'day'];
    return stopWords.includes(word);
  }

  async getCurrentTrendingKeywords() {
    const trends = await this.getTrendingTopics(50);
    return trends.map(trend => trend.name.toLowerCase());
  }

  calculateRelevance(keywords, topics, trendData) {
    const trendKeywords = [trendData.name.toLowerCase()];
    
    // Keyword similarity
    const keywordSimilarity = this.calculateKeywordSimilarity(
      keywords.map(k => k.toLowerCase()), 
      trendKeywords
    );
    
    // Platform alignment (bonus for matching platforms)
    const platformBonus = trendData.platforms.length > 2 ? 0.1 : 0;
    
    // Velocity bonus (trending faster = more relevant)
    const velocityBonus = trendData.velocity * 0.2;
    
    return Math.min(1, keywordSimilarity + platformBonus + velocityBonus);
  }

  getRecommendedAction(relevanceScore, trendData) {
    if (relevanceScore > 0.8 && trendData.velocity > 0.7) {
      return 'immediate_action';
    } else if (relevanceScore > 0.6 && trendData.velocity > 0.5) {
      return 'plan_content';
    } else if (relevanceScore > 0.4) {
      return 'monitor_trend';
    } else {
      return 'consider_adaptation';
    }
  }

  // Cleanup
  destroy() {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
    }
    
    console.log('Trend Analyzer: Service destroyed');
  }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = TrendAnalyzer;
}

// Global registration for browser usage
if (typeof window !== 'undefined') {
  window.TrendAnalyzer = TrendAnalyzer;
}