/**
 * API Route - IPGeolocation
 * Utilise la clé IPGeolocation configurée
 */

import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering for this route
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = request.nextUrl;
    const ip = searchParams.get('ip') || '';
    const fields = searchParams.get('fields') || 'geo,time_zone,currency';

    let url = `https://api.ipgeolocation.io/ipgeo?apiKey=${process.env.IPGEOLOCATION_API_KEY}`;
    if (ip) url += `&ip=${ip}`;
    if (fields) url += `&fields=${fields}`;

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`IPGeolocation API error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      ip: data.ip,
      location: {
        country: data.country_name,
        countryCode: data.country_code2,
        city: data.city,
        region: data.state_prov,
        latitude: data.latitude,
        longitude: data.longitude,
        zipCode: data.zipcode
      },
      timezone: {
        name: data.time_zone?.name,
        offset: data.time_zone?.offset,
        currentTime: data.time_zone?.current_time
      },
      currency: {
        code: data.currency?.code,
        name: data.currency?.name,
        symbol: data.currency?.symbol
      },
      isp: data.isp,
      organization: data.organization
    });

  } catch (error: any) {
    console.error('IPGeolocation Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
