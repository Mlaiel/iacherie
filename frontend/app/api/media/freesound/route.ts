/**
 * API Route - FreeSound Audio
 * Utilise les 2 clés FreeSound configurées
 */

import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('query') || 'music';
    const filter = searchParams.get('filter') || ''; // duration:[0 TO 10]
    const page = searchParams.get('page') || '1';

    let url = `https://freesound.org/apiv2/search/text/?query=${encodeURIComponent(query)}&page=${page}&fields=id,name,description,url,previews,duration,download&token=${process.env.FREESOUND_API_KEY}`;
    if (filter) url += `&filter=${encodeURIComponent(filter)}`;

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`FreeSound API error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      total: data.count,
      sounds: data.results.map((sound: any) => ({
        id: sound.id,
        name: sound.name,
        description: sound.description,
        url: sound.url,
        duration: sound.duration,
        previews: {
          mp3Low: sound.previews['preview-lq-mp3'],
          mp3High: sound.previews['preview-hq-mp3'],
          oggLow: sound.previews['preview-lq-ogg'],
          oggHigh: sound.previews['preview-hq-ogg']
        },
        downloadUrl: sound.download
      }))
    });

  } catch (error: any) {
    console.error('FreeSound API Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

// POST - Télécharger un son
export async function POST(request: NextRequest) {
  try {
    const { soundId } = await request.json();

    if (!soundId) {
      return NextResponse.json(
        { error: 'Sound ID requis' },
        { status: 400 }
      );
    }

    const response = await fetch(
      `https://freesound.org/apiv2/sounds/${soundId}/download/?token=${process.env.FREESOUND_API_KEY}`
    );

    if (!response.ok) {
      throw new Error(`FreeSound download error: ${response.statusText}`);
    }

    // L'API retourne directement le fichier
    const audioBlob = await response.blob();

    return new NextResponse(audioBlob, {
      headers: {
        'Content-Type': 'audio/mpeg',
        'Content-Disposition': `attachment; filename="sound-${soundId}.mp3"`
      }
    });

  } catch (error: any) {
    console.error('FreeSound Download Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
