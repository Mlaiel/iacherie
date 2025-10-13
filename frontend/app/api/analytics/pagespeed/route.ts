/**
 * API Route - PageSpeed Insights
 * Utilise la clé PageSpeed configurée
 */

import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering for this route
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = request.nextUrl;
    const url = searchParams.get('url');
    const strategy = searchParams.get('strategy') || 'mobile'; // mobile ou desktop

    if (!url) {
      return NextResponse.json(
        { error: 'URL requise' },
        { status: 400 }
      );
    }

    const response = await fetch(
      `https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=${encodeURIComponent(url)}&strategy=${strategy}&key=${process.env.PAGESPEED_API_KEY}`
    );

    if (!response.ok) {
      throw new Error(`PageSpeed API error: ${response.statusText}`);
    }

    const data = await response.json();

    // Extraction des métriques importantes
    const lighthouseResult = data.lighthouseResult;
    const metrics = lighthouseResult.audits;

    return NextResponse.json({
      success: true,
      url: data.id,
      strategy,
      scores: {
        performance: lighthouseResult.categories.performance.score * 100,
        accessibility: lighthouseResult.categories.accessibility.score * 100,
        bestPractices: lighthouseResult.categories['best-practices'].score * 100,
        seo: lighthouseResult.categories.seo.score * 100
      },
      metrics: {
        firstContentfulPaint: metrics['first-contentful-paint'].displayValue,
        largestContentfulPaint: metrics['largest-contentful-paint'].displayValue,
        totalBlockingTime: metrics['total-blocking-time'].displayValue,
        cumulativeLayoutShift: metrics['cumulative-layout-shift'].displayValue,
        speedIndex: metrics['speed-index'].displayValue
      },
      opportunities: Object.values(metrics)
        .filter((audit: any) => audit.score !== null && audit.score < 0.9)
        .map((audit: any) => ({
          title: audit.title,
          description: audit.description,
          score: audit.score
        }))
        .slice(0, 5)
    });

  } catch (error: any) {
    console.error('PageSpeed Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
