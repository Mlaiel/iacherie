/**
 * API Route - Dashboard metrics
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    // Simulate dashboard metrics data
    const metrics = {
      totalContent: 1247,
      protectedFiles: 1198,
      monthlyRevenue: 24580,
      activeMonitoring: 892,
      totalViolations: 43,
      resolvedViolations: 38,
      revenueGrowth: 12.5,
      contentGrowth: 8.3,
    };

    return NextResponse.json(metrics);
  } catch (error) {
    console.error('Error fetching dashboard metrics:', error);
    return NextResponse.json({ message: 'Internal server error' }, { status: 500 });
  }
}