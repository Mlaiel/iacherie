/*
 * Owner: Fahed Mlaiel
 * Contact: mlaiel@live.de
 * Notice: Attribution to Fahed Mlaiel is mandatory in all copies, forks, and derivatives.
 */

import { useMemo } from 'react'
import { CaseReport } from '@/lib/types'
import { generateWeeklyData } from '@/lib/statistics'

interface ImpactChartProps {
  cases: CaseReport[]
}

export function ImpactChart({ cases }: ImpactChartProps) {
  const chartData = useMemo(() => {
    return generateWeeklyData(cases)
  }, [cases])

  const maxValue = Math.max(...chartData.map(d => d.total), 1)

  return (
    <div className="space-y-4">
      {/* Chart */}
      <div className="relative h-48 flex items-end justify-between gap-2 p-4 bg-muted/30 rounded-lg">
        {chartData.map((data, index) => (
          <div key={index} className="flex flex-col items-center gap-2 flex-1">
            {/* Bars */}
            <div className="relative w-full max-w-8 h-32 bg-border rounded-sm overflow-hidden">
              {/* Animals bar (bottom) */}
              {data.animals > 0 && (
                <div 
                  className="absolute bottom-0 w-full bg-orange-500 rounded-sm transition-all duration-500"
                  style={{ 
                    height: `${(data.animals / maxValue) * 100}%`,
                    minHeight: data.animals > 0 ? '2px' : '0'
                  }}
                />
              )}
              {/* Homeless bar (top) */}
              {data.homeless > 0 && (
                <div 
                  className="absolute w-full bg-primary rounded-sm transition-all duration-500"
                  style={{ 
                    bottom: `${(data.animals / maxValue) * 100}%`,
                    height: `${(data.homeless / maxValue) * 100}%`,
                    minHeight: data.homeless > 0 ? '2px' : '0'
                  }}
                />
              )}
              {/* Total count overlay */}
              {data.total > 0 && (
                <div className="absolute -top-6 left-1/2 transform -translate-x-1/2">
                  <span className="text-xs font-semibold text-foreground bg-background/80 px-1 rounded">
                    {data.total}
                  </span>
                </div>
              )}
            </div>
            
            {/* Day label */}
            <span className="text-xs text-muted-foreground font-medium">
              {data.day}
            </span>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-primary rounded-sm" />
          <span className="text-muted-foreground">Homeless Assistance</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-orange-500 rounded-sm" />
          <span className="text-muted-foreground">Animal Care</span>
        </div>
      </div>

      {/* Summary */}
      <div className="text-center text-sm text-muted-foreground">
        Total this week: <span className="font-semibold text-foreground">
          {chartData.reduce((sum, day) => sum + day.total, 0)} cases helped
        </span>
      </div>
    </div>
  )
}