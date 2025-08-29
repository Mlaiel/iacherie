/**
 * API Route - Dashboard metrics
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

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

    res.status(200).json(metrics);
  } catch (error) {
    console.error('Error fetching dashboard metrics:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
}