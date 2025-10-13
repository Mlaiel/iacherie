/*
 * Owner: Fahed Mlaiel
 * Contact: mlaiel@live.de
 * Notice: Attribution to Fahed Mlaiel is mandatory in all copies, forks, and derivatives.
 */

import { useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Heart, 
  MapPin, 
  Clock, 
  User,
  PawPrint,
  CheckCircle,
  PlayCircle,
  Plus
} from '@phosphor-icons/react'
import { VolunteerActivity, CaseReport } from '@/lib/types'
import { formatTimeAgo } from '@/lib/statistics'

interface ActivityTimelineProps {
  activities: VolunteerActivity[]
  cases: CaseReport[]
}

export function ActivityTimeline({ activities, cases }: ActivityTimelineProps) {
  // Generate some mock recent activities based on cases for demo
  const timelineData = useMemo(() => {
    const recentActivities: Array<{
      id: string
      action: string
      description: string
      timestamp: string
      icon: JSX.Element
      color: string
      case?: CaseReport
    }> = []

    // Add real activities
    activities.forEach(activity => {
      const relatedCase = cases.find(c => c.id === activity.caseId)
      if (relatedCase) {
        const actionMap = {
          'helped': { 
            text: 'Completed assistance for', 
            icon: <CheckCircle size={16} />, 
            color: 'text-success'
          },
          'started-helping': { 
            text: 'Started helping with', 
            icon: <PlayCircle size={16} />, 
            color: 'text-primary'
          },
          'reported': { 
            text: 'Reported new case:', 
            icon: <Plus size={16} />, 
            color: 'text-accent'
          },
          'updated': { 
            text: 'Updated information for', 
            icon: <Clock size={16} />, 
            color: 'text-muted-foreground'
          }
        }

        const actionInfo = actionMap[activity.action] || actionMap['updated']
        
        recentActivities.push({
          id: activity.id,
          action: activity.action,
          description: `${actionInfo.text} ${relatedCase.type} case`,
          timestamp: activity.timestamp,
          icon: actionInfo.icon,
          color: actionInfo.color,
          case: relatedCase
        })
      }
    })

    // Add some demo activities if no real activities exist
    if (recentActivities.length === 0) {
      const now = new Date()
      const demoActivities = [
        {
          id: 'demo-1',
          action: 'helped',
          description: 'Completed assistance for homeless case',
          timestamp: new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString(),
          icon: <CheckCircle size={16} />,
          color: 'text-success'
        },
        {
          id: 'demo-2',
          action: 'started-helping',
          description: 'Started helping with animal care case',
          timestamp: new Date(now.getTime() - 4 * 60 * 60 * 1000).toISOString(),
          icon: <PlayCircle size={16} />,
          color: 'text-primary'
        },
        {
          id: 'demo-3',
          action: 'reported',
          description: 'Reported new homeless assistance case',
          timestamp: new Date(now.getTime() - 1 * 24 * 60 * 60 * 1000).toISOString(),
          icon: <Plus size={16} />,
          color: 'text-accent'
        }
      ]
      recentActivities.push(...demoActivities)
    }

    // Sort by timestamp (most recent first)
    return recentActivities.sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    )
  }, [activities, cases])

  // Remove the local formatTimeAgo function since we're importing it

  const getActivityBadge = (action: string) => {
    switch (action) {
      case 'helped':
        return <Badge variant="secondary" className="text-success">Completed</Badge>
      case 'started-helping':
        return <Badge variant="secondary" className="text-primary">In Progress</Badge>
      case 'reported':
        return <Badge variant="secondary" className="text-accent">Reported</Badge>
      default:
        return <Badge variant="outline">Updated</Badge>
    }
  }

  return (
    <div className="space-y-6">
      {/* Activity Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Today's Activities</p>
                <p className="text-2xl font-bold text-primary">
                  {timelineData.filter(a => 
                    new Date(a.timestamp).toDateString() === new Date().toDateString()
                  ).length}
                </p>
              </div>
              <Clock className="text-primary" size={24} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">This Week</p>
                <p className="text-2xl font-bold text-accent">
                  {timelineData.filter(a => {
                    const activityDate = new Date(a.timestamp)
                    const oneWeekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
                    return activityDate >= oneWeekAgo
                  }).length}
                </p>
              </div>
              <Heart className="text-accent" size={24} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Average Response</p>
                <p className="text-2xl font-bold text-success">45m</p>
              </div>
              <Clock className="text-success" size={24} />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Activity Timeline */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          {timelineData.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Heart size={48} className="mx-auto mb-4 opacity-50" />
              <p>No recent activities</p>
              <p className="text-sm">Start helping cases to see your impact timeline</p>
            </div>
          ) : (
            <div className="space-y-4">
              {timelineData.map((item, index) => (
                <div key={item.id} className="relative flex gap-4 group">
                  {/* Timeline line */}
                  {index < timelineData.length - 1 && (
                    <div className="absolute left-4 top-8 w-px h-6 bg-border" />
                  )}
                  
                  {/* Activity icon */}
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full bg-muted flex items-center justify-center ${item.color} group-hover:bg-primary group-hover:text-primary-foreground transition-colors`}>
                    {item.icon}
                  </div>
                  
                  {/* Activity content */}
                  <div className="flex-1 min-w-0 space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-foreground">
                          {item.description}
                        </p>
                        {item.case && (
                          <div className="flex items-center gap-2 mt-1">
                            <div className="flex items-center gap-1 text-xs text-muted-foreground">
                              {item.case.type === 'homeless' ? (
                                <User size={12} />
                              ) : (
                                <PawPrint size={12} />
                              )}
                              <span className="capitalize">{item.case.type}</span>
                            </div>
                            <div className="flex items-center gap-1 text-xs text-muted-foreground">
                              <MapPin size={12} />
                              <span>{item.case.address || 'Location marked'}</span>
                            </div>
                          </div>
                        )}
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {getActivityBadge(item.action)}
                        <span className="text-xs text-muted-foreground">
                          {formatTimeAgo(item.timestamp)}
                        </span>
                      </div>
                    </div>
                    
                    {item.case && (
                      <div className="text-xs text-muted-foreground bg-muted/50 p-2 rounded">
                        "{item.case.description}"
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Weekly Summary */}
      <Card>
        <CardHeader>
          <CardTitle>This Week's Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Activity Breakdown</h4>
              <div className="space-y-2">
                {[
                  { action: 'helped', label: 'Cases Completed', count: timelineData.filter(a => a.action === 'helped').length },
                  { action: 'started-helping', label: 'Cases Started', count: timelineData.filter(a => a.action === 'started-helping').length },
                  { action: 'reported', label: 'Cases Reported', count: timelineData.filter(a => a.action === 'reported').length }
                ].map(item => (
                  <div key={item.action} className="flex justify-between text-sm">
                    <span className="text-muted-foreground">{item.label}</span>
                    <span className="font-mono font-medium">{item.count}</span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Impact by Type</h4>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Homeless Assistance</span>
                  <span className="font-mono font-medium">
                    {timelineData.filter(a => a.case?.type === 'homeless').length}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Animal Care</span>
                  <span className="font-mono font-medium">
                    {timelineData.filter(a => a.case?.type === 'animal').length}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}