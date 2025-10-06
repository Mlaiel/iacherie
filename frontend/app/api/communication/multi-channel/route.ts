/**
 * API Route - Multi-Channel Communication
 * Envoie sur Discord + SMS + Email simultanément
 */

import { NextRequest, NextResponse } from 'next/server';

interface ChannelResult {
  channel: string;
  success: boolean;
  messageId?: string;
  error?: string;
}

export async function POST(request: NextRequest) {
  try {
    const { 
      message,
      channels,
      recipients
    } = await request.json();

    if (!message) {
      return NextResponse.json(
        { error: 'Message requis' },
        { status: 400 }
      );
    }

    const selectedChannels = channels || ['discord', 'sms', 'email'];
    const results: ChannelResult[] = [];

    // Discord
    if (selectedChannels.includes('discord') && recipients?.discordChannelId) {
      try {
        const discordRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/communication/discord`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            channelId: recipients.discordChannelId,
            message
          })
        });
        const data = await discordRes.json();
        results.push({
          channel: 'discord',
          success: data.success,
          messageId: data.messageId
        });
      } catch (error: any) {
        results.push({
          channel: 'discord',
          success: false,
          error: error.message
        });
      }
    }

    // SMS
    if (selectedChannels.includes('sms') && recipients?.phone) {
      try {
        const smsRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/communication/twilio`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            to: recipients.phone,
            message
          })
        });
        const data = await smsRes.json();
        results.push({
          channel: 'sms',
          success: data.success,
          messageId: data.messageId
        });
      } catch (error: any) {
        results.push({
          channel: 'sms',
          success: false,
          error: error.message
        });
      }
    }

    // Email
    if (selectedChannels.includes('email') && recipients?.email) {
      try {
        const emailRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/communication/resend`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            to: recipients.email,
            subject: recipients.emailSubject || 'Notification IACherie',
            html: `<p>${message}</p>`
          })
        });
        const data = await emailRes.json();
        results.push({
          channel: 'email',
          success: data.success,
          messageId: data.emailId
        });
      } catch (error: any) {
        results.push({
          channel: 'email',
          success: false,
          error: error.message
        });
      }
    }

    const successCount = results.filter(r => r.success).length;

    return NextResponse.json({
      success: successCount > 0,
      totalChannels: results.length,
      successCount,
      results
    });

  } catch (error: any) {
    console.error('Multi-Channel Communication Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
