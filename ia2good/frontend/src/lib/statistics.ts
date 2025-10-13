/*
 * Owner: Fahed Mlaiel
 * Contact: mlaiel@live.de
 * Notice: Attribution to Fahed Mlaiel is mandatory in all copies, forks, and derivatives.
 */

import { CaseReport, VolunteerActivity } from './types'

export function calculateImpactStats(cases: CaseReport[], activities: VolunteerActivity[]) {
  const helpedCases = cases.filter(c => c.status === 'helped')
  const homelessHelped = helpedCases.filter(c => c.type === 'homeless').length
  const animalsHelped = helpedCases.filter(c => c.type === 'animal').length
  
  // Calculate weekly progress
  const oneWeekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
  const weeklyActivities = activities.filter(a => 
    new Date(a.timestamp) >= oneWeekAgo && a.action === 'helped'
  )
  
  // Calculate active streak (simplified - consecutive days with activity)
  const today = new Date().toDateString()
  const todayActivities = activities.filter(a => 
    new Date(a.timestamp).toDateString() === today
  )
  
  return {
    totalCasesHelped: helpedCases.length,
    totalReports: cases.length,
    peopleHelped: homelessHelped,
    animalsHelped: animalsHelped,
    weeklyProgress: weeklyActivities.length,
    activeStreak: todayActivities.length > 0 ? 1 : 0,
    averageResponseTime: 45, // Mock data for now
    mostActiveCategory: homelessHelped > animalsHelped ? 'homeless' as const : 
                      animalsHelped > homelessHelped ? 'animal' as const : null
  }
}

export function calculateCommunityStats(cases: CaseReport[]) {
  const now = new Date()
  const today = new Date().toDateString()
  const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
  const oneMonthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)

  const activeCases = cases.filter(c => c.status === 'open' || c.status === 'in-progress').length
  
  const resolvedToday = cases.filter(c => 
    c.status === 'helped' && 
    c.helpedAt && 
    new Date(c.helpedAt).toDateString() === today
  ).length
  
  const resolvedThisWeek = cases.filter(c => 
    c.status === 'helped' && 
    c.helpedAt && 
    new Date(c.helpedAt) >= oneWeekAgo
  ).length

  const resolvedThisMonth = cases.filter(c => 
    c.status === 'helped' && 
    c.helpedAt && 
    new Date(c.helpedAt) >= oneMonthAgo
  ).length

  return {
    totalVolunteers: 127, // Mock data
    activeCases,
    casesResolvedToday: resolvedToday,
    casesResolvedThisWeek: resolvedThisWeek,
    casesResolvedThisMonth: resolvedThisMonth,
    averageResolutionTime: 180, // Mock data in minutes
    topVolunteers: [
      { id: '1', name: 'You', casesHelped: cases.filter(c => c.status === 'helped').length },
      { id: '2', name: 'Sarah M.', casesHelped: 23 },
      { id: '3', name: 'Mike R.', casesHelped: 19 }
    ]
  }
}

export function formatTimeAgo(timestamp: string): string {
  const now = new Date()
  const time = new Date(timestamp)
  const diffInMinutes = Math.floor((now.getTime() - time.getTime()) / (1000 * 60))

  if (diffInMinutes < 1) return 'Just now'
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`
  
  const diffInHours = Math.floor(diffInMinutes / 60)
  if (diffInHours < 24) return `${diffInHours}h ago`
  
  const diffInDays = Math.floor(diffInHours / 24)
  if (diffInDays < 7) return `${diffInDays}d ago`
  
  return time.toLocaleDateString()
}

export function generateWeeklyData(cases: CaseReport[]) {
  const last7Days = Array.from({ length: 7 }, (_, i) => {
    const date = new Date()
    date.setDate(date.getDate() - (6 - i))
    return date
  })

  return last7Days.map(date => {
    const dayStr = date.toDateString()
    const helpedCases = cases.filter(c => 
      c.status === 'helped' && 
      c.helpedAt && 
      new Date(c.helpedAt).toDateString() === dayStr
    )
    
    const homelessHelped = helpedCases.filter(c => c.type === 'homeless').length
    const animalsHelped = helpedCases.filter(c => c.type === 'animal').length
    
    return {
      day: date.toLocaleDateString('en-US', { weekday: 'short' }),
      date: dayStr,
      homeless: homelessHelped,
      animals: animalsHelped,
      total: helpedCases.length
    }
  })
}