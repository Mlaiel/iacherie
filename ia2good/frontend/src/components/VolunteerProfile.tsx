/*
 * Owner: Fahed Mlaiel
 * Contact: mlaiel@live.de
 * Notice: Attribution to Fahed Mlaiel is mandatory in all copies, forks, and derivatives.
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { useTranslation } from '@/hooks/useTranslation'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import {
  Heart,
  MapPin,
  Clock,
  Star,
  Question as Award,
  TrendUp,
  Calendar,
  Users,
  Shield,
  Phone,
  Question as Mail,
  Question as Edit,
  Question as Settings,
  ChartBar,
  Activity,
  Target
} from '@phosphor-icons/react'
import type { VolunteerProfile as VolunteerProfileType, VolunteerActivity, CaseReport, Badge as BadgeType } from '@/lib/types'
import { ActivityTimeline } from '@/components/ActivityTimeline'

interface VolunteerProfileProps {
  profile: VolunteerProfileType
  activities: VolunteerActivity[]
  cases: CaseReport[]
  isOwnProfile: boolean
  onEditProfile?: () => void
}

export function VolunteerProfile({ 
  profile, 
  activities, 
  cases, 
  isOwnProfile,
  onEditProfile 
}: VolunteerProfileProps) {
  const { t } = useTranslation()
  const [selectedTimeframe, setSelectedTimeframe] = useState<'week' | 'month' | 'year' | 'all'>('month')

  // Calculate recent activity stats
  const getTimeframeDate = (timeframe: string) => {
    const now = new Date()
    switch (timeframe) {
      case 'week':
        return new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
      case 'month':
        return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
      case 'year':
        return new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000)
      default:
        return new Date(0)
    }
  }

  const filteredActivities = activities.filter(activity => 
    new Date(activity.timestamp) >= getTimeframeDate(selectedTimeframe)
  )

  // Calculate contribution metrics
  const helpedCases = filteredActivities.filter(a => a.action === 'helped').length
  const reportedCases = filteredActivities.filter(a => a.action === 'reported').length
  const totalContributions = filteredActivities.length

  // Calculate average response time for helped cases
  const responseTimes = filteredActivities
    .filter(a => a.action === 'helped')
    .map(activity => {
      const caseReport = cases.find(c => c.id === activity.caseId)
      if (caseReport) {
        const reportTime = new Date(caseReport.reportedAt).getTime()
        const helpTime = new Date(activity.timestamp).getTime()
        return (helpTime - reportTime) / (1000 * 60) // minutes
      }
      return 0
    })
    .filter(time => time > 0)

  const avgResponseTime = responseTimes.length > 0 
    ? Math.round(responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length)
    : 0

  // Format member since date
  const memberSince = new Date(profile.joinedAt).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })

  const formatDuration = (minutes: number) => {
    if (minutes < 60) return `${minutes}m`
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
  }

  return (
    <div className="space-y-6">
      {/* Profile Header */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-6">
            {/* Avatar and Basic Info */}
            <div className="flex flex-col items-center md:items-start space-y-4">
              <Avatar className="w-24 h-24">
                <AvatarImage src={profile.avatarUrl} alt={profile.name} />
                <AvatarFallback className="text-2xl">
                  {profile.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                </AvatarFallback>
              </Avatar>
              
              <div className="text-center md:text-left space-y-2">
                <h1 className="text-2xl font-bold flex items-center gap-2">
                  {profile.name}
                  {profile.verification.isVerified && (
                    <Shield className="text-primary" size={20} />
                  )}
                </h1>
                
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Calendar size={16} />
                  <span>Member since {memberSince}</span>
                </div>

                {profile.bio && (
                  <p className="text-sm text-muted-foreground max-w-md">
                    {profile.bio}
                  </p>
                )}
              </div>
            </div>

            {/* Stats Overview */}
            <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-muted rounded-lg">
                <div className="text-2xl font-bold text-primary">{profile.stats.totalCasesHelped}</div>
                <div className="text-xs text-muted-foreground">Cases Helped</div>
              </div>
              
              <div className="text-center p-3 bg-muted rounded-lg">
                <div className="text-2xl font-bold text-accent">{profile.stats.totalHoursVolunteered}</div>
                <div className="text-xs text-muted-foreground">Hours Volunteered</div>
              </div>
              
              <div className="text-center p-3 bg-muted rounded-lg">
                <div className="text-2xl font-bold text-success">{profile.stats.activeStreakDays}</div>
                <div className="text-xs text-muted-foreground">Day Streak</div>
              </div>
              
              <div className="text-center p-3 bg-muted rounded-lg">
                <div className="flex items-center justify-center gap-1">
                  <span className="text-2xl font-bold">{profile.stats.rating.toFixed(1)}</span>
                  <Star weight="fill" className="text-yellow-500" size={16} />
                </div>
                <div className="text-xs text-muted-foreground">
                  {profile.stats.reviewCount} reviews
                </div>
              </div>
            </div>

            {/* Actions */}
            {isOwnProfile && (
              <div className="flex flex-col gap-2">
                <Button onClick={onEditProfile} variant="outline" size="sm">
                  <Edit size={16} className="mr-2" />
                  Edit Profile
                </Button>
                <Button variant="outline" size="sm">
                  <Settings size={16} className="mr-2" />
                  Settings
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Detailed Analytics */}
      <Tabs defaultValue="activity" className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <TabsList>
            <TabsTrigger value="activity">
              <Activity size={16} className="mr-2" />
              Activity
            </TabsTrigger>
            <TabsTrigger value="impact">
              <ChartBar size={16} className="mr-2" />
              Impact
            </TabsTrigger>
            <TabsTrigger value="badges">
              <Award size={16} className="mr-2" />
              Badges
            </TabsTrigger>
            <TabsTrigger value="skills">
              <Target size={16} className="mr-2" />
              Skills
            </TabsTrigger>
          </TabsList>

          {/* Timeframe Selector */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Period:</span>
            <div className="flex gap-1">
              {['week', 'month', 'year', 'all'].map((timeframe) => (
                <Button
                  key={timeframe}
                  variant={selectedTimeframe === timeframe ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setSelectedTimeframe(timeframe as any)}
                  className="capitalize"
                >
                  {timeframe}
                </Button>
              ))}
            </div>
          </div>
        </div>

        {/* Activity Tab */}
        <TabsContent value="activity" className="space-y-6">
          {/* Recent Activity Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Heart className="text-primary" size={16} />
                  Cases Helped
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{helpedCases}</div>
                <p className="text-xs text-muted-foreground">
                  in the last {selectedTimeframe === 'all' ? 'year' : selectedTimeframe}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center gap-2">
                  <MapPin className="text-accent" size={16} />
                  Cases Reported
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{reportedCases}</div>
                <p className="text-xs text-muted-foreground">
                  new cases identified
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Clock className="text-success" size={16} />
                  Response Time
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatDuration(avgResponseTime)}</div>
                <p className="text-xs text-muted-foreground">
                  average response
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Activity Timeline */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <ActivityTimeline 
                activities={filteredActivities.slice(0, 10)} 
                cases={cases}
              />
              {filteredActivities.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  No activity in this time period
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Impact Tab */}
        <TabsContent value="impact" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* People vs Animals Helped */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Impact Breakdown</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>{t('profile.peopleHelped')}</span>
                    <span className="font-medium">{profile.stats.peopleHelped}</span>
                  </div>
                  <Progress 
                    value={(profile.stats.peopleHelped / Math.max(profile.stats.totalCasesHelped, 1)) * 100} 
                    className="h-2"
                  />
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>{t('profile.animalsHelped')}</span>
                    <span className="font-medium">{profile.stats.animalsHelped}</span>
                  </div>
                  <Progress 
                    value={(profile.stats.animalsHelped / Math.max(profile.stats.totalCasesHelped, 1)) * 100} 
                    className="h-2"
                  />
                </div>

                <Separator />

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Most Active Category</span>
                    <Badge variant="secondary" className="capitalize">
                      {profile.stats.mostActiveCategory || 'Equal'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Community Rating */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Community Feedback</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="text-3xl font-bold">{profile.stats.rating.toFixed(1)}</div>
                  <div className="flex items-center">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Star
                        key={star}
                        weight={star <= profile.stats.rating ? 'fill' : 'regular'}
                        className={star <= profile.stats.rating ? 'text-yellow-500' : 'text-muted-foreground'}
                        size={20}
                      />
                    ))}
                  </div>
                </div>
                
                <p className="text-sm text-muted-foreground">
                  Based on {profile.stats.reviewCount} community reviews
                </p>

                <div className="pt-2">
                  <div className="text-sm font-medium mb-2">Recognition</div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <TrendUp className="text-primary" size={16} />
                    Consistently helpful volunteer
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Badges Tab */}
        <TabsContent value="badges" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Achievement Badges</CardTitle>
            </CardHeader>
            <CardContent>
              {profile.stats.badges.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {profile.stats.badges.map((badge) => (
                    <div
                      key={badge.id}
                      className="flex items-center gap-3 p-4 border rounded-lg"
                    >
                      <div className="text-2xl">{badge.icon}</div>
                      <div className="flex-1">
                        <div className="font-medium">{badge.name}</div>
                        <div className="text-sm text-muted-foreground">{badge.description}</div>
                        <div className="text-xs text-muted-foreground mt-1">
                          Earned {new Date(badge.earnedAt).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Award size={48} className="mx-auto mb-4 opacity-50" />
                  <p>Keep volunteering to earn achievement badges!</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Skills Tab */}
        <TabsContent value="skills" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Skills & Expertise</CardTitle>
            </CardHeader>
            <CardContent>
              {profile.skills.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {profile.skills.map((skill) => (
                    <Badge key={skill} variant="outline" className="px-3 py-1">
                      {skill}
                    </Badge>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Target size={48} className="mx-auto mb-4 opacity-50" />
                  <p>Add skills to help others know your expertise!</p>
                </div>
              )}

              {profile.preferences && (
                <div className="mt-6 space-y-4">
                  <Separator />
                  <div>
                    <h4 className="font-medium mb-2">{t('settings.volunteerPreferencesTitle')}</h4>
                    <div className="space-y-2 text-sm text-muted-foreground">
                      <div className="flex justify-between">
                        <span>Max Distance</span>
                        <span>{profile.preferences.maxDistance} km</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Preferred Categories</span>
                        <div className="flex gap-1">
                          {profile.preferences.preferredCategories.map(cat => (
                            <Badge key={cat} variant="secondary" className="text-xs capitalize">
                              {cat}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}