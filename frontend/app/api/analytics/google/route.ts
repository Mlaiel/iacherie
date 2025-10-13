/**
 * API Route - Google Analytics Tracking
 * Utilise les 2 clés Google Analytics configurées
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { 
      eventName, 
      eventParams = {},
      userId,
      sessionId 
    } = await request.json();

    if (!eventName) {
      return NextResponse.json(
        { error: 'Event name requis' },
        { status: 400 }
      );
    }

    // Google Analytics 4 Measurement Protocol
    const response = await fetch(
      `https://www.google-analytics.com/mp/collect?measurement_id=${process.env.GOOGLE_ANALYTICS_MEASUREMENT_ID}&api_secret=${process.env.GOOGLE_ANALYTICS_API_SECRET}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          client_id: userId || 'anonymous',
          events: [{
            name: eventName,
            params: {
              ...eventParams,
              session_id: sessionId || Date.now().toString(),
              engagement_time_msec: eventParams.engagement_time_msec || '100'
            }
          }]
        })
      }
    );

    if (!response.ok) {
      throw new Error(`Google Analytics error: ${response.statusText}`);
    }

    return NextResponse.json({
      success: true,
      eventName,
      tracked: true
    });

  } catch (error: any) {
    console.error('Google Analytics Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

// GET - Récupérer les statistiques (nécessite Google Analytics Data API)
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const startDate = searchParams.get('startDate') || '7daysAgo';
    const endDate = searchParams.get('endDate') || 'today';

    // Note: Nécessite OAuth2 pour accéder aux données
    // Implémentation simplifiée pour démonstration

    return NextResponse.json({
      success: true,
      message: 'Pour accéder aux données, configurez Google Analytics Data API avec OAuth2',
      period: { startDate, endDate }
    });

  } catch (error: any) {
    console.error('Google Analytics GET Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
