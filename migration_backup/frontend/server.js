#!/usr/bin/env node

/**
 * Development Server für Dev Container Support
 * Ainflue Frontend Platform
 */

const express = require('express')
const next = require('next')

const dev = process.env.NODE_ENV !== 'production'
const app = next({ dev, dir: __dirname })
const handle = app.getRequestHandler()

const PORT = process.env.PORT || 3000
const API_URL = process.env.API_URL || 'http://localhost:8000'

app.prepare().then(() => {
  const server = express()

  // Enable trust proxy for dev containers
  server.set('trust proxy', true)

  // Health check endpoint
  server.get('/health', (req, res) => {
    res.json({ 
      status: 'healthy', 
      service: 'Ainflue Frontend',
      timestamp: new Date().toISOString(),
      port: PORT,
      backend: API_URL
    })
  })

  // API proxy endpoint test
  server.get('/api/backend-test', (req, res) => {
    res.json({
      message: 'Frontend API proxy working',
      backend_url: API_URL
    })
  })

  // Handle all other requests with Next.js
  server.all('*', (req, res) => {
    return handle(req, res)
  })

  server.listen(PORT, '0.0.0.0', (err) => {
    if (err) {
      console.error('❌ Server start error:', err)
      throw err
    }
    console.log(`🚀 Ainflue Frontend Server ready on http://0.0.0.0:${PORT}`)
    console.log(`🔗 Backend API: ${API_URL}`)
    console.log(`🌐 External access: https://shiny-lamp-r6j79jw765vf544g-3000.app.github.dev`)
    console.log(`✅ Health check: http://0.0.0.0:${PORT}/health`)
  })
}).catch(err => {
  console.error('❌ Next.js preparation error:', err)
  process.exit(1)
})