/**
 * 🔧 GITHUB API ROUTE
 * Repository automation & management
 */

import { NextRequest, NextResponse } from 'next/server';

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;

export async function POST(req: NextRequest) {
  try {
    const { action, owner, repo, ...params } = await req.json();

    if (!GITHUB_TOKEN) {
      return NextResponse.json(
        { error: 'GitHub token not configured' },
        { status: 500 }
      );
    }

    let endpoint = '';
    let method = 'GET';
    let body = null;

    switch (action) {
      case 'list_repos':
        endpoint = 'https://api.github.com/user/repos';
        break;

      case 'get_repo':
        endpoint = `https://api.github.com/repos/${owner}/${repo}`;
        break;

      case 'create_issue':
        endpoint = `https://api.github.com/repos/${owner}/${repo}/issues`;
        method = 'POST';
        body = JSON.stringify(params);
        break;

      case 'list_commits':
        endpoint = `https://api.github.com/repos/${owner}/${repo}/commits`;
        break;

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }

    const response = await fetch(endpoint, {
      method,
      headers: {
        'Authorization': `Bearer ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github+json',
        'Content-Type': 'application/json'
      },
      body
    });

    const data = await response.json();
    return NextResponse.json({ success: true, data });

  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    provider: 'GitHub API',
    status: GITHUB_TOKEN ? 'active' : 'not_configured'
  });
}
