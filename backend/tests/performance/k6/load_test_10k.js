/**
 * K6 Load Testing Script for IA-Influencer Platform
 * Tests 10K+ concurrent users with realistic behavior patterns
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
export const errorRate = new Rate('errors');
export const responseTime = new Trend('response_time');
export const requestCount = new Counter('requests');

// Test configuration
export const options = {
  stages: [
    // Ramp up to 1K users over 5 minutes
    { duration: '5m', target: 1000 },
    // Ramp up to 5K users over 10 minutes
    { duration: '10m', target: 5000 },
    // Ramp up to 10K users over 15 minutes
    { duration: '15m', target: 10000 },
    // Stay at 10K users for 30 minutes
    { duration: '30m', target: 10000 },
    // Ramp down over 10 minutes
    { duration: '10m', target: 0 },
  ],
  thresholds: {
    // Response time thresholds
    'http_req_duration': ['p(95)<500', 'p(99)<1000'],
    // Error rate threshold
    'errors': ['rate<0.05'],
    // Request rate threshold
    'http_reqs': ['rate>1000'],
  },
  // Resource limits
  noConnectionReuse: false,
  userAgent: 'K6-LoadTest-AInfluence/1.0',
};

// Base URL configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// Authentication tokens (simulated)
const AUTH_TOKENS = [
  'token_user_1', 'token_user_2', 'token_user_3',
  // Add more tokens for realistic testing
];

// Test data sets
const CONTENT_TYPES = ['video', 'image', 'audio', 'text'];
const PLATFORMS = ['youtube', 'instagram', 'tiktok', 'twitter'];

export function setup() {
  // Setup phase - run once before all VUs
  console.log('🚀 Starting K6 Load Test for IA-Influencer Platform');
  console.log(`📊 Target: 10K concurrent users`);
  console.log(`🌐 Base URL: ${BASE_URL}`);
  
  // Health check
  const healthResponse = http.get(`${BASE_URL}/health`);
  check(healthResponse, {
    'Health check status is 200': (r) => r.status === 200,
  });
  
  return {
    baseUrl: BASE_URL,
    timestamp: new Date().toISOString(),
  };
}

export default function(data) {
  // Simulate realistic user behavior
  const userType = Math.random();
  
  if (userType < 0.3) {
    // 30% - Content creators
    simulateContentCreator();
  } else if (userType < 0.6) {
    // 30% - Content consumers  
    simulateContentConsumer();
  } else if (userType < 0.8) {
    // 20% - Brands/Advertisers
    simulateBrandUser();
  } else {
    // 20% - Platform administrators
    simulateAdminUser();
  }
  
  // Random sleep between actions (1-5 seconds)
  sleep(Math.random() * 4 + 1);
}

function simulateContentCreator() {
  const sessionId = `creator_${__VU}_${__ITER}`;
  
  // 1. Login/Authentication
  authenticateUser(sessionId);
  
  // 2. Upload content
  uploadContent();
  
  // 3. Check analytics
  checkAnalytics();
  
  // 4. Manage content protection
  manageContentProtection();
  
  requestCount.add(4);
}

function simulateContentConsumer() {
  const sessionId = `consumer_${__VU}_${__ITER}`;
  
  // 1. Browse content
  browseContent();
  
  // 2. Search content
  searchContent();
  
  // 3. View content details
  viewContentDetails();
  
  requestCount.add(3);
}

function simulateBrandUser() {
  const sessionId = `brand_${__VU}_${__ITER}`;
  
  // 1. Authenticate
  authenticateUser(sessionId);
  
  // 2. Search for influencers
  searchInfluencers();
  
  // 3. View collaboration opportunities
  viewCollaborations();
  
  // 4. Check campaign analytics
  checkCampaignAnalytics();
  
  requestCount.add(4);
}

function simulateAdminUser() {
  const sessionId = `admin_${__VU}_${__ITER}`;
  
  // 1. Admin authentication
  authenticateAdmin(sessionId);
  
  // 2. Monitor platform metrics
  monitorMetrics();
  
  // 3. Review content moderation
  reviewContentModeration();
  
  requestCount.add(3);
}

function authenticateUser(sessionId) {
  const payload = {
    email: `user${__VU}@test.com`,
    password: 'testpassword123',
    session_id: sessionId,
  };
  
  const response = http.post(`${BASE_URL}/api/v1/auth/login`, JSON.stringify(payload), {
    headers: { 'Content-Type': 'application/json' },
    tags: { name: 'auth_login' },
  });
  
  const success = check(response, {
    'Login status is 200': (r) => r.status === 200,
    'Login response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  errorRate.add(!success);
  responseTime.add(response.timings.duration);
}

function uploadContent() {
  const contentData = {
    title: `Test Content ${__VU}_${__ITER}`,
    description: 'Load test content description',
    type: CONTENT_TYPES[Math.floor(Math.random() * CONTENT_TYPES.length)],
    platform: PLATFORMS[Math.floor(Math.random() * PLATFORMS.length)],
    file_size: Math.floor(Math.random() * 100000) + 10000, // 10KB-100KB
  };
  
  const response = http.post(`${BASE_URL}/api/v1/content/upload`, JSON.stringify(contentData), {
    headers: { 
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getRandomToken()}`,
    },
    tags: { name: 'content_upload' },
  });
  
  const success = check(response, {
    'Upload status is 201': (r) => r.status === 201,
    'Upload response time < 2000ms': (r) => r.timings.duration < 2000,
  });
  
  errorRate.add(!success);
  responseTime.add(response.timings.duration);
}

function browseContent() {
  const params = {
    page: Math.floor(Math.random() * 10) + 1,
    limit: 20,
    type: CONTENT_TYPES[Math.floor(Math.random() * CONTENT_TYPES.length)],
  };
  
  const response = http.get(`${BASE_URL}/api/v1/content?${new URLSearchParams(params)}`, {
    tags: { name: 'browse_content' },
  });
  
  const success = check(response, {
    'Browse status is 200': (r) => r.status === 200,
    'Browse response time < 300ms': (r) => r.timings.duration < 300,
    'Browse returns data': (r) => r.json('data') !== undefined,
  });
  
  errorRate.add(!success);
  responseTime.add(response.timings.duration);
}

function searchContent() {
  const searchTerms = ['music', 'video', 'tutorial', 'review', 'entertainment'];
  const query = searchTerms[Math.floor(Math.random() * searchTerms.length)];
  
  const response = http.get(`${BASE_URL}/api/v1/search?q=${query}&type=content`, {
    tags: { name: 'search_content' },
  });
  
  const success = check(response, {
    'Search status is 200': (r) => r.status === 200,
    'Search response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  errorRate.add(!success);
  responseTime.add(response.timings.duration);
}

function viewContentDetails() {
  const contentId = Math.floor(Math.random() * 1000) + 1;
  
  const response = http.get(`${BASE_URL}/api/v1/content/${contentId}`, {
    tags: { name: 'content_details' },
  });
  
  const success = check(response, {
    'Content details response time < 200ms': (r) => r.timings.duration < 200,
  });
  
  errorRate.add(!success);
  responseTime.add(response.timings.duration);
}

function checkAnalytics() {
  const response = http.get(`${BASE_URL}/api/v1/analytics/dashboard`, {
    headers: { 'Authorization': `Bearer ${getRandomToken()}` },
    tags: { name: 'analytics_dashboard' },
  });
  
  const success = check(response, {
    'Analytics status is 200': (r) => r.status === 200,
    'Analytics response time < 1000ms': (r) => r.timings.duration < 1000,
  });
  
  errorRate.add(!success);
  responseTime.add(response.timings.duration);
}

function manageContentProtection() {
  const response = http.get(`${BASE_URL}/api/v1/protection/status`, {
    headers: { 'Authorization': `Bearer ${getRandomToken()}` },
    tags: { name: 'content_protection' },
  });
  
  const success = check(response, {
    'Protection status is 200': (r) => r.status === 200,
    'Protection response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  errorRate.add(!success);
  responseTime.add(response.timings.duration);
}

function searchInfluencers() {
  const criteria = {
    category: ['lifestyle', 'tech', 'gaming', 'fashion'][Math.floor(Math.random() * 4)],
    min_followers: 10000,
    location: 'US',
  };
  
  const response = http.get(`${BASE_URL}/api/v1/influencers/search?${new URLSearchParams(criteria)}`, {
    headers: { 'Authorization': `Bearer ${getRandomToken()}` },
    tags: { name: 'influencer_search' },
  });
  
  const success = check(response, {
    'Influencer search status is 200': (r) => r.status === 200,
    'Influencer search response time < 800ms': (r) => r.timings.duration < 800,
  });
  
  errorRate.add(!success);
  responseTime.add(response.timings.duration);
}

function viewCollaborations() {
  const response = http.get(`${BASE_URL}/api/v1/collaborations/opportunities`, {
    headers: { 'Authorization': `Bearer ${getRandomToken()}` },
    tags: { name: 'collaborations' },
  });
  
  const success = check(response, {
    'Collaborations status is 200': (r) => r.status === 200,
    'Collaborations response time < 600ms': (r) => r.timings.duration < 600,
  });
  
  errorRate.add(!success);
  responseTime.add(response.timings.duration);
}

function checkCampaignAnalytics() {
  const response = http.get(`${BASE_URL}/api/v1/campaigns/analytics`, {
    headers: { 'Authorization': `Bearer ${getRandomToken()}` },
    tags: { name: 'campaign_analytics' },
  });
  
  const success = check(response, {
    'Campaign analytics status is 200': (r) => r.status === 200,
    'Campaign analytics response time < 1000ms': (r) => r.timings.duration < 1000,
  });
  
  errorRate.add(!success);
  responseTime.add(response.timings.duration);
}

function authenticateAdmin(sessionId) {
  const payload = {
    email: `admin${__VU}@test.com`,
    password: 'adminpassword123',
    role: 'admin',
    session_id: sessionId,
  };
  
  const response = http.post(`${BASE_URL}/api/v1/admin/auth`, JSON.stringify(payload), {
    headers: { 'Content-Type': 'application/json' },
    tags: { name: 'admin_auth' },
  });
  
  const success = check(response, {
    'Admin auth status is 200': (r) => r.status === 200,
    'Admin auth response time < 300ms': (r) => r.timings.duration < 300,
  });
  
  errorRate.add(!success);
  responseTime.add(response.timings.duration);
}

function monitorMetrics() {
  const response = http.get(`${BASE_URL}/api/v1/admin/metrics`, {
    headers: { 'Authorization': `Bearer ${getRandomToken()}` },
    tags: { name: 'admin_metrics' },
  });
  
  const success = check(response, {
    'Metrics status is 200': (r) => r.status === 200,
    'Metrics response time < 400ms': (r) => r.timings.duration < 400,
  });
  
  errorRate.add(!success);
  responseTime.add(response.timings.duration);
}

function reviewContentModeration() {
  const response = http.get(`${BASE_URL}/api/v1/admin/moderation/queue`, {
    headers: { 'Authorization': `Bearer ${getRandomToken()}` },
    tags: { name: 'content_moderation' },
  });
  
  const success = check(response, {
    'Moderation status is 200': (r) => r.status === 200,
    'Moderation response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  errorRate.add(!success);
  responseTime.add(response.timings.duration);
}

function getRandomToken() {
  return AUTH_TOKENS[Math.floor(Math.random() * AUTH_TOKENS.length)];
}

export function teardown(data) {
  // Cleanup phase - run once after all VUs finish
  console.log('🏁 K6 Load Test completed');
  console.log(`📊 Test duration: ${data.timestamp} to ${new Date().toISOString()}`);
}