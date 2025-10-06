/**
 * API Route - Twilio SMS
 * Utilise les 3 clés Twilio configurées
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { to, message, mediaUrl } = await request.json();

    if (!to || !message) {
      return NextResponse.json(
        { error: 'Destinataire et message requis' },
        { status: 400 }
      );
    }

    const formData = new URLSearchParams({
      To: to,
      From: process.env.TWILIO_PHONE_NUMBER!,
      Body: message
    });

    if (mediaUrl) {
      formData.append('MediaUrl', mediaUrl);
    }

    // Twilio API
    const response = await fetch(
      `https://api.twilio.com/2010-04-01/Accounts/${process.env.TWILIO_ACCOUNT_SID}/Messages.json`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${Buffer.from(
            `${process.env.TWILIO_ACCOUNT_SID}:${process.env.TWILIO_AUTH_TOKEN}`
          ).toString('base64')}`,
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Twilio API error: ${error.message || response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      messageId: data.sid,
      status: data.status,
      to: data.to,
      from: data.from,
      dateCreated: data.date_created
    });

  } catch (error: any) {
    console.error('Twilio SMS Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

// GET - Récupérer l'historique des messages
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = searchParams.get('limit') || '20';

    const response = await fetch(
      `https://api.twilio.com/2010-04-01/Accounts/${process.env.TWILIO_ACCOUNT_SID}/Messages.json?PageSize=${limit}`,
      {
        headers: {
          'Authorization': `Basic ${Buffer.from(
            `${process.env.TWILIO_ACCOUNT_SID}:${process.env.TWILIO_AUTH_TOKEN}`
          ).toString('base64')}`
        }
      }
    );

    if (!response.ok) {
      throw new Error(`Twilio API error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      count: data.messages.length,
      messages: data.messages.map((msg: any) => ({
        sid: msg.sid,
        to: msg.to,
        from: msg.from,
        body: msg.body,
        status: msg.status,
        dateCreated: msg.date_created
      }))
    });

  } catch (error: any) {
    console.error('Twilio GET Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
