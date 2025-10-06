/**
 * API Route - Multi-Platform Social Media Post
 * Poste simultanément sur Twitter, Instagram, Facebook et Reddit
 */

import { NextRequest, NextResponse } from 'next/server';

interface PostResult {
  platform: string;
  success: boolean;
  postId?: string;
  url?: string;
  error?: string;
}

export async function POST(request: NextRequest) {
  try {
    const { 
      text, 
      imageUrl, 
      platforms,
      subreddit = 'test' 
    } = await request.json();

    if (!text && !imageUrl) {
      return NextResponse.json(
        { error: 'Le texte ou l\'image est requis' },
        { status: 400 }
      );
    }

    const selectedPlatforms = platforms || ['twitter', 'instagram', 'facebook', 'reddit'];
    const results: PostResult[] = [];

    // Twitter
    if (selectedPlatforms.includes('twitter')) {
      try {
        const twitterRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/social/twitter`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text })
        });
        const data = await twitterRes.json();
        results.push({
          platform: 'twitter',
          success: data.success,
          postId: data.tweetId,
          url: data.url
        });
      } catch (error: any) {
        results.push({
          platform: 'twitter',
          success: false,
          error: error.message
        });
      }
    }

    // Instagram (nécessite une image)
    if (selectedPlatforms.includes('instagram') && imageUrl) {
      try {
        const instagramRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/social/instagram`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ imageUrl, caption: text })
        });
        const data = await instagramRes.json();
        results.push({
          platform: 'instagram',
          success: data.success,
          postId: data.postId,
          url: data.url
        });
      } catch (error: any) {
        results.push({
          platform: 'instagram',
          success: false,
          error: error.message
        });
      }
    }

    // Facebook
    if (selectedPlatforms.includes('facebook')) {
      try {
        const facebookRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/social/facebook`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text, imageUrl })
        });
        const data = await facebookRes.json();
        results.push({
          platform: 'facebook',
          success: data.success,
          postId: data.postId,
          url: data.url
        });
      } catch (error: any) {
        results.push({
          platform: 'facebook',
          success: false,
          error: error.message
        });
      }
    }

    // Reddit
    if (selectedPlatforms.includes('reddit')) {
      try {
        const redditRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/social/reddit`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title: text.slice(0, 300),
            text,
            url: imageUrl,
            subreddit
          })
        });
        const data = await redditRes.json();
        results.push({
          platform: 'reddit',
          success: data.success,
          postId: data.postId,
          url: data.url
        });
      } catch (error: any) {
        results.push({
          platform: 'reddit',
          success: false,
          error: error.message
        });
      }
    }

    const successCount = results.filter(r => r.success).length;

    return NextResponse.json({
      success: successCount > 0,
      totalPlatforms: results.length,
      successCount,
      results
    });

  } catch (error: any) {
    console.error('Multi-Platform Post Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
