/**
 * API Route - Discord Bot Commands
 * Utilise les 4 clés Discord configurées
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { command, channelId, message, embed } = await request.json();

    if (!channelId) {
      return NextResponse.json(
        { error: 'Channel ID requis' },
        { status: 400 }
      );
    }

    let payload: any = {};

    if (message) {
      payload.content = message;
    }

    if (embed) {
      payload.embeds = [{
        title: embed.title,
        description: embed.description,
        color: embed.color || 0x5865F2,
        fields: embed.fields || [],
        footer: embed.footer ? { text: embed.footer } : undefined,
        timestamp: new Date().toISOString()
      }];
    }

    // Envoyer le message via Discord API
    const response = await fetch(
      `https://discord.com/api/v10/channels/${channelId}/messages`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bot ${process.env.DISCORD_BOT_TOKEN}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Discord API error: ${error.message || response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      messageId: data.id,
      channelId: data.channel_id,
      timestamp: data.timestamp
    });

  } catch (error: any) {
    console.error('Discord Bot Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

// GET - Récupérer les messages d'un canal
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const channelId = searchParams.get('channelId');
    const limit = searchParams.get('limit') || '50';

    if (!channelId) {
      return NextResponse.json(
        { error: 'Channel ID requis' },
        { status: 400 }
      );
    }

    const response = await fetch(
      `https://discord.com/api/v10/channels/${channelId}/messages?limit=${limit}`,
      {
        headers: {
          'Authorization': `Bot ${process.env.DISCORD_BOT_TOKEN}`
        }
      }
    );

    if (!response.ok) {
      throw new Error(`Discord API error: ${response.statusText}`);
    }

    const messages = await response.json();

    return NextResponse.json({
      success: true,
      count: messages.length,
      messages: messages.map((msg: any) => ({
        id: msg.id,
        author: msg.author.username,
        content: msg.content,
        timestamp: msg.timestamp,
        embeds: msg.embeds
      }))
    });

  } catch (error: any) {
    console.error('Discord GET Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
