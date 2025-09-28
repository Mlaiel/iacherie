/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  eslint: {
    ignoreDuringBuilds: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001',
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8765',
    NEXT_PUBLIC_ANALYTICS_WS: process.env.NEXT_PUBLIC_ANALYTICS_WS || 'ws://localhost:8000/ws/dashboards',
    NEXT_PUBLIC_NOTIFICATIONS_WS: process.env.NEXT_PUBLIC_NOTIFICATIONS_WS || 'ws://localhost:8000/ws/notifications',
    NEXT_PUBLIC_METRICS_WS: process.env.NEXT_PUBLIC_METRICS_WS || 'ws://localhost:8000/ws/metrics',
    NEXT_PUBLIC_ENABLE_WEBSOCKETS: process.env.NEXT_PUBLIC_ENABLE_WEBSOCKETS || 'true',
  },
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
        pathname: '/**',
      },
      {
        protocol: 'http',
        hostname: '127.0.0.1',
        port: '8000',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'api.ainflue.com',
        pathname: '/**',
      },
    ],
  },
  async rewrites() {
    return [
      // AI API proxy vers le bon port
      {
        source: '/api/ai/:path*',
        destination: 'http://localhost:8001/api/ai/:path*',
      },
      // Monitoring API proxy
      {
        source: '/api/monitoring/:path*',
        destination: 'http://localhost:8001/api/monitoring/:path*',
      },
      // Les téléchargements /api/download/* utilisent notre route locale
      // Analytics API proxy
      {
        source: '/analytics/:path*',
        destination: 'http://localhost:8000/analytics/:path*',
      },
      // Auth API proxy
      {
        source: '/auth/:path*',
        destination: 'http://localhost:8000/auth/:path*',
      },
      // Health checks proxy
      {
        source: '/health/:path*',
        destination: 'http://localhost:8000/health/:path*',
      },
      // Metrics proxy
      {
        source: '/metrics',
        destination: 'http://localhost:8000/metrics',
      },
    ];
  },
  // PWA Configuration + CORS Headers
  async headers() {
    return [
      {
        source: '/manifest.json',
        headers: [
          {
            key: 'Content-Type',
            value: 'application/manifest+json',
          },
        ],
      },
      {
        source: '/sw.js',
        headers: [
          {
            key: 'Content-Type',
            value: 'application/javascript',
          },
          {
            key: 'Service-Worker-Allowed',
            value: '/',
          },
        ],
      },
      // CORS headers for API integration
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          // Development CORS
          {
            key: 'Access-Control-Allow-Origin',
            value: process.env.NODE_ENV === 'development' ? '*' : 'https://ainflue.com',
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET, POST, PUT, DELETE, OPTIONS',
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'X-Requested-With, Content-Type, Authorization',
          },
        ],
      },
    ];
  },
  // Webpack configuration for WebSocket support
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        ws: false,
      };
    }
    return config;
  },
};

module.exports = nextConfig;