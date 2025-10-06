/**
 * API Route - Resend Email
 * Utilise la clé Resend configurée
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { 
      to, 
      subject, 
      html, 
      text,
      from = 'noreply@iacherie.com',
      cc,
      bcc,
      replyTo 
    } = await request.json();

    if (!to || !subject || (!html && !text)) {
      return NextResponse.json(
        { error: 'Destinataire, sujet et contenu requis' },
        { status: 400 }
      );
    }

    const emailData: any = {
      from,
      to: Array.isArray(to) ? to : [to],
      subject,
      html: html || undefined,
      text: text || undefined
    };

    if (cc) emailData.cc = cc;
    if (bcc) emailData.bcc = bcc;
    if (replyTo) emailData.reply_to = replyTo;

    // Resend API
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.RESEND_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(emailData)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Resend API error: ${error.message || response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      emailId: data.id,
      to: emailData.to,
      subject
    });

  } catch (error: any) {
    console.error('Resend Email Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
