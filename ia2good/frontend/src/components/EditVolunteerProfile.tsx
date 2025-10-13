/*
 * Owner: Fahed Mlaiel
 * Contact: mlaiel@live.de
 * Notice: Attribution to Fahed Mlaiel is mandatory in all copies, forks, and derivatives.
 */

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from '@/components/ui/dialog'
import { Separator } from '@/components/ui/separator'
import {
  User,
  MapPin,
  Clock,
  Bell,
  Plus,
  X,
  Camera,
  FloppyDisk,
  Gear
} from '@phosphor-icons/react'
import { VolunteerProfile } from '@/lib/types'
import { toast } from 'sonner'
import { useTranslation } from '@/hooks/useTranslation'

interface EditVolunteerProfileProps {
  profile: VolunteerProfile
  onSave: (updatedProfile: VolunteerProfile) => void
  trigger?: React.ReactNode
}

export function EditVolunteerProfile({ profile, onSave, trigger }: EditVolunteerProfileProps) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false)
  const [formData, setFormData] = useState({
    name: profile.name,
    bio: profile.bio || '',
    skills: [...profile.skills],
    maxDistance: profile.preferences.maxDistance,
    preferredCategories: [...profile.preferences.preferredCategories],
    notificationsEnabled: profile.preferences.notificationSettings.enabled,
    quietHoursEnabled: profile.preferences.notificationSettings.quietHours.enabled,
    quietHoursStart: profile.preferences.notificationSettings.quietHours.start,
    quietHoursEnd: profile.preferences.notificationSettings.quietHours.end,
    availableDays: [...profile.availableHours.days],
    startTime: profile.availableHours.startTime,
    endTime: profile.availableHours.endTime
  })
  const [newSkill, setNewSkill] = useState('')

  const handleSave = () => {
    const updatedProfile: VolunteerProfile = {
      ...profile,
      name: formData.name,
      bio: formData.bio,
      skills: formData.skills,
      preferences: {
        ...profile.preferences,
        maxDistance: formData.maxDistance,
        preferredCategories: formData.preferredCategories,
        notificationSettings: {
          ...profile.preferences.notificationSettings,
          enabled: formData.notificationsEnabled,
          quietHours: {
            enabled: formData.quietHoursEnabled,
            start: formData.quietHoursStart,
            end: formData.quietHoursEnd
          }
        }
      },
      availableHours: {
        days: formData.availableDays,
        startTime: formData.startTime,
        endTime: formData.endTime
      }
    }

    onSave(updatedProfile)
    setOpen(false)
    toast.success(t('profile.profileUpdatedSuccess'))
  }

  const addSkill = () => {
    if (newSkill.trim() && !formData.skills.includes(newSkill.trim())) {
      setFormData(prev => ({
        ...prev,
        skills: [...prev.skills, newSkill.trim()]
      }))
      setNewSkill('')
    }
  }

  const removeSkill = (skillToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills.filter(skill => skill !== skillToRemove)
    }))
  }

  const toggleCategory = (category: 'homeless' | 'animal') => {
    setFormData(prev => ({
      ...prev,
      preferredCategories: prev.preferredCategories.includes(category)
        ? prev.preferredCategories.filter(c => c !== category)
        : [...prev.preferredCategories, category]
    }))
  }

  const toggleDay = (day: string) => {
    setFormData(prev => ({
      ...prev,
      availableDays: prev.availableDays.includes(day)
        ? prev.availableDays.filter(d => d !== day)
        : [...prev.availableDays, day]
    }))
  }

  const weekDays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="outline">
            <Gear size={16} className="mr-2" />
            {t('profile.editProfile')}
          </Button>
        )}
      </DialogTrigger>
      
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <User className="text-primary" />
            {t('profile.editVolunteerProfile')}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Basic Information */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">{t('profile.basicInformation')}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Avatar */}
              <div className="flex items-center gap-4">
                <Avatar className="w-20 h-20">
                  <AvatarImage src={profile.avatarUrl} alt={profile.name} />
                  <AvatarFallback>
                    {profile.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div className="space-y-2">
                  <Button variant="outline" size="sm">
                    <Camera size={16} className="mr-2" />
                    {t('profile.changePhoto')}
                  </Button>
                  <p className="text-xs text-muted-foreground">
                    {t('profile.photoFormat')}
                  </p>
                </div>
              </div>

              {/* Name */}
              <div className="space-y-2">
                <Label htmlFor="name">{t('profile.displayName')}</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder={t('profile.displayNamePlaceholder')}
                />
              </div>

              {/* Bio */}
              <div className="space-y-2">
                <Label htmlFor="bio">{t('profile.bio')}</Label>
                <Textarea
                  id="bio"
                  value={formData.bio}
                  onChange={(e) => setFormData(prev => ({ ...prev, bio: e.target.value }))}
                  placeholder={t('profile.bioPlaceholder')}
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>

          {/* Skills & Expertise */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">{t('profile.skillsExpertise')}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>{t('profile.skills')}</Label>
                <div className="flex gap-2">
                  <Input
                    value={newSkill}
                    onChange={(e) => setNewSkill(e.target.value)}
                    placeholder={t('profile.addSkillPlaceholder')}
                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                  />
                  <Button onClick={addSkill} size="sm">
                    <Plus size={16} />
                  </Button>
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                {formData.skills.map((skill) => (
                  <Badge key={skill} variant="secondary" className="flex items-center gap-1">
                    {skill}
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-auto p-1 hover:bg-destructive hover:text-destructive-foreground"
                      onClick={() => removeSkill(skill)}
                    >
                      <X size={12} />
                    </Button>
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Volunteer Preferences */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <MapPin className="text-primary" />
                {t('profile.volunteerPreferences')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Max Distance */}
              <div className="space-y-2">
                <Label htmlFor="maxDistance">{t('profile.maxTravelDistance')}</Label>
                <Input
                  id="maxDistance"
                  type="number"
                  min="1"
                  max="100"
                  value={formData.maxDistance}
                  onChange={(e) => setFormData(prev => ({ 
                    ...prev, 
                    maxDistance: parseInt(e.target.value) || 1 
                  }))}
                />
              </div>

              {/* Preferred Categories */}
              <div className="space-y-2">
                <Label>{t('profile.preferredCategories')}</Label>
                <div className="flex gap-2">
                  <Button
                    variant={formData.preferredCategories.includes('homeless') ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => toggleCategory('homeless')}
                  >
                    {t('profile.homelessAssistance')}
                  </Button>
                  <Button
                    variant={formData.preferredCategories.includes('animal') ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => toggleCategory('animal')}
                  >
                    {t('profile.animalCare')}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Availability */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Clock className="text-primary" />
                {t('profile.availability')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Available Days */}
              <div className="space-y-2">
                <Label>{t('profile.availableDays')}</Label>
                <div className="flex flex-wrap gap-2">
                  {weekDays.map((day) => (
                    <Button
                      key={day}
                      variant={formData.availableDays.includes(day) ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => toggleDay(day)}
                      className="capitalize"
                    >
                      {t(`profile.weekdays.${day}` as any).slice(0, 3)}
                    </Button>
                  ))}
                </div>
              </div>

              {/* Time Range */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="startTime">{t('profile.startTime')}</Label>
                  <Input
                    id="startTime"
                    type="time"
                    value={formData.startTime}
                    onChange={(e) => setFormData(prev => ({ ...prev, startTime: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="endTime">{t('profile.endTime')}</Label>
                  <Input
                    id="endTime"
                    type="time"
                    value={formData.endTime}
                    onChange={(e) => setFormData(prev => ({ ...prev, endTime: e.target.value }))}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Notification Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Bell className="text-primary" />
                {t('profile.notificationSettings')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Enable Notifications */}
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label>{t('profile.enableNotifications')}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t('profile.enableNotificationsDesc')}
                  </p>
                </div>
                <Switch
                  checked={formData.notificationsEnabled}
                  onCheckedChange={(checked) => setFormData(prev => ({ 
                    ...prev, 
                    notificationsEnabled: checked 
                  }))}
                />
              </div>

              <Separator />

              {/* Quiet Hours */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <Label>{t('profile.quietHours')}</Label>
                    <p className="text-sm text-muted-foreground">
                      {t('profile.quietHoursDesc')}
                    </p>
                  </div>
                  <Switch
                    checked={formData.quietHoursEnabled}
                    onCheckedChange={(checked) => setFormData(prev => ({ 
                      ...prev, 
                      quietHoursEnabled: checked 
                    }))}
                  />
                </div>

                {formData.quietHoursEnabled && (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="quietStart">{t('profile.startTime')}</Label>
                      <Input
                        id="quietStart"
                        type="time"
                        value={formData.quietHoursStart}
                        onChange={(e) => setFormData(prev => ({ 
                          ...prev, 
                          quietHoursStart: e.target.value 
                        }))}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="quietEnd">{t('profile.endTime')}</Label>
                      <Input
                        id="quietEnd"
                        type="time"
                        value={formData.quietHoursEnd}
                        onChange={(e) => setFormData(prev => ({ 
                          ...prev, 
                          quietHoursEnd: e.target.value 
                        }))}
                      />
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-4">
            <Button variant="outline" onClick={() => setOpen(false)}>
              {t('profile.cancel')}
            </Button>
            <Button onClick={handleSave}>
              <FloppyDisk size={16} className="mr-2" />
              {t('profile.saveChanges')}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}