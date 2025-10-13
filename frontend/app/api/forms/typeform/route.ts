/**
 * 📝 TYPEFORM API - Gestion de formulaires et enquêtes
 */

import { NextRequest, NextResponse } from 'next/server';

const TYPEFORM_API_KEY = process.env.TYPEFORM_API_KEY;

export async function POST(req: NextRequest) {
  try {
    const { action, formId, data } = await req.json();

    if (!TYPEFORM_API_KEY) {
      return NextResponse.json(
        { error: 'Typeform API key not configured' },
        { status: 500 }
      );
    }

    let endpoint = '';
    let method = 'GET';
    let body = null;

    switch (action) {
      case 'create_form':
        endpoint = 'https://api.typeform.com/forms';
        method = 'POST';
        body = JSON.stringify(data);
        break;

      case 'get_form':
        endpoint = `https://api.typeform.com/forms/${formId}`;
        break;

      case 'get_responses':
        endpoint = `https://api.typeform.com/forms/${formId}/responses`;
        break;

      case 'list_forms':
        endpoint = 'https://api.typeform.com/forms';
        break;

      default:
        return NextResponse.json(
          { error: 'Invalid action' },
          { status: 400 }
        );
    }

    const response = await fetch(endpoint, {
      method,
      headers: {
        'Authorization': `Bearer ${TYPEFORM_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Typeform API error: ${error}`);
    }

    const result = await response.json();

    return NextResponse.json({
      success: true,
      data: result
    });

  } catch (error) {
    console.error('Typeform route error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

// GET - Liste des formulaires
export async function GET() {
  try {
    if (!TYPEFORM_API_KEY) {
      return NextResponse.json(
        { error: 'Typeform API key not configured' },
        { status: 500 }
      );
    }

    const response = await fetch('https://api.typeform.com/forms', {
      headers: {
        'Authorization': `Bearer ${TYPEFORM_API_KEY}`
      }
    });

    const data = await response.json();

    return NextResponse.json({
      success: true,
      forms: data.items || [],
      total: data.total_items || 0
    });

  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
