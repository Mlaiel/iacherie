/**
 * ☁️ AZURE ACTIVE DIRECTORY API ROUTE
 * Microsoft Cloud Integration
 */

import { NextRequest, NextResponse } from 'next/server';

const AZURE_TENANT_ID = process.env.AZURE_TENANT_ID;
const AZURE_CLIENT_ID = process.env.AZURE_CLIENT_ID;
const AZURE_CLIENT_SECRET = process.env.AZURE_CLIENT_SECRET;

export async function POST(req: NextRequest) {
  try {
    const { action, ...params } = await req.json();

    if (!AZURE_TENANT_ID || !AZURE_CLIENT_ID || !AZURE_CLIENT_SECRET) {
      return NextResponse.json(
        { error: 'Azure credentials not configured' },
        { status: 500 }
      );
    }

    // Obtenir token d'accès
    if (action === 'get_token') {
      const tokenResponse = await fetch(
        `https://login.microsoftonline.com/${AZURE_TENANT_ID}/oauth2/v2.0/token`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: new URLSearchParams({
            client_id: AZURE_CLIENT_ID,
            client_secret: AZURE_CLIENT_SECRET,
            scope: 'https://graph.microsoft.com/.default',
            grant_type: 'client_credentials'
          })
        }
      );

      const data = await tokenResponse.json();
      return NextResponse.json({ success: true, token: data.access_token });
    }

    return NextResponse.json({ error: 'Invalid action' }, { status: 400 });

  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    provider: 'Azure Active Directory',
    status: AZURE_TENANT_ID ? 'configured' : 'not_configured',
    tenant: AZURE_TENANT_ID || 'not_set'
  });
}
