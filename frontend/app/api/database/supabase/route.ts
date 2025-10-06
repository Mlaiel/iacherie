/**
 * API Route - Supabase Operations
 */

import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// Vérifier si Supabase est configuré
if (!supabaseUrl || !supabaseKey) {
  console.warn('⚠️ Supabase not configured. API routes will return mock data.');
}

const supabase = supabaseUrl && supabaseKey 
  ? createClient(supabaseUrl, supabaseKey)
  : null;

// GET - Query data
export async function GET(request: NextRequest) {
  try {
    if (!supabase) {
      return NextResponse.json(
        { error: 'Supabase not configured', data: [] },
        { status: 503 }
      );
    }

    const { searchParams } = new URL(request.url);
    const table = searchParams.get('table');
    const limit = searchParams.get('limit') || '10';

    if (!table) {
      return NextResponse.json(
        { error: 'Table name requise' },
        { status: 400 }
      );
    }

    const { data, error } = await supabase
      .from(table)
      .select('*')
      .limit(parseInt(limit));

    if (error) throw error;

    return NextResponse.json({
      success: true,
      data
    });

  } catch (error: any) {
    console.error('Supabase GET Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

// POST - Insert data
export async function POST(request: NextRequest) {
  try {
    if (!supabase) {
      return NextResponse.json(
        { error: 'Supabase not configured' },
        { status: 503 }
      );
    }

    const { table, data } = await request.json();

    if (!table || !data) {
      return NextResponse.json(
        { error: 'Table et data requis' },
        { status: 400 }
      );
    }

    const { data: insertedData, error } = await supabase
      .from(table)
      .insert(data)
      .select();

    if (error) throw error;

    return NextResponse.json({
      success: true,
      data: insertedData
    });

  } catch (error: any) {
    console.error('Supabase POST Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
