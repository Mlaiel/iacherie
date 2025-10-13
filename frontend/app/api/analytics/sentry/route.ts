/**
 * API Route - Sentry Error Tracking
 * Utilise la clé Sentry configurée
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { 
      error,
      level = 'error', // debug, info, warning, error, fatal
      tags = {},
      extra = {},
      user = {}
    } = await request.json();

    if (!error) {
      return NextResponse.json(
        { error: 'Error details requis' },
        { status: 400 }
      );
    }

    // Parse Sentry DSN
    const dsn = process.env.SENTRY_DSN!;
    const dsnParts = dsn.match(/https:\/\/(.+)@(.+)\/(.+)/);
    if (!dsnParts) {
      throw new Error('Invalid Sentry DSN');
    }

    const [, publicKey, host, projectId] = dsnParts;

    // Sentry Event
    const sentryEvent = {
      event_id: generateEventId(),
      timestamp: Date.now() / 1000,
      platform: 'javascript',
      level,
      logger: 'iacherie-frontend',
      exception: {
        values: [{
          type: error.name || 'Error',
          value: error.message || error,
          stacktrace: error.stack ? {
            frames: parseStackTrace(error.stack)
          } : undefined
        }]
      },
      tags: {
        ...tags,
        environment: process.env.NODE_ENV || 'development'
      },
      extra,
      user
    };

    // Envoyer à Sentry
    const response = await fetch(
      `https://${host}/api/${projectId}/store/`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Sentry-Auth': `Sentry sentry_version=7, sentry_key=${publicKey}, sentry_timestamp=${Math.floor(Date.now() / 1000)}`
        },
        body: JSON.stringify(sentryEvent)
      }
    );

    if (!response.ok) {
      throw new Error(`Sentry API error: ${response.statusText}`);
    }

    return NextResponse.json({
      success: true,
      eventId: sentryEvent.event_id,
      tracked: true
    });

  } catch (error: any) {
    console.error('Sentry Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

function generateEventId(): string {
  return Array.from({ length: 32 }, () => 
    Math.floor(Math.random() * 16).toString(16)
  ).join('');
}

function parseStackTrace(stack: string): any[] {
  return stack.split('\n').map(line => {
    const match = line.match(/at (.+) \((.+):(\d+):(\d+)\)/);
    if (match) {
      return {
        function: match[1],
        filename: match[2],
        lineno: parseInt(match[3]),
        colno: parseInt(match[4])
      };
    }
    return null;
  }).filter(Boolean);
}
