import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest, { params }: { params: { contentId: string } }) {
  try {
    const { contentId } = params;
    console.log('📥 Route proxy téléchargement appelée pour:', contentId);
    
    // Appel au backend
    const backendUrl = `http://localhost:8000/api/download/${contentId}`;
    console.log('🔗 Appel backend:', backendUrl);
    
    const backendResponse = await fetch(backendUrl);
    
    console.log('📡 Réponse backend:', backendResponse.status, backendResponse.statusText);
    
    if (!backendResponse.ok) {
      console.error('❌ Backend erreur:', backendResponse.status);
      return new NextResponse(`Erreur backend: ${backendResponse.status}`, { status: backendResponse.status });
    }
    
    // Récupération des headers du backend
    const contentType = backendResponse.headers.get('content-type') || 'application/octet-stream';
    const contentDisposition = backendResponse.headers.get('content-disposition') || `attachment; filename=iacherie_${contentId}`;
    
    console.log('📋 Headers backend:', { contentType, contentDisposition });
    
    // Stream du contenu
    const fileBuffer = await backendResponse.arrayBuffer();
    console.log('📦 Taille fichier:', fileBuffer.byteLength, 'bytes');
    
    return new NextResponse(fileBuffer, {
      status: 200,
      headers: {
        'Content-Type': contentType,
        'Content-Disposition': contentDisposition,
        'Content-Length': fileBuffer.byteLength.toString(),
      },
    });
    
  } catch (error) {
    console.error('Erreur de téléchargement:', error);
    return new NextResponse('Erreur lors du téléchargement', { status: 500 });
  }
}