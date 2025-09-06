/**
 * Content Planning Calendar Component - Professional Dashboard
 * 
 * Provides content planning and scheduling capabilities with calendar interface
 * Supports content scheduling, deadline tracking, and publication planning
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { 
  CalendarIcon,
  PlusIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  TagIcon,
  BellIcon,
  ShareIcon
} from '@heroicons/react/24/outline';

interface ContentEvent {
  id: string;
  title: string;
  description: string;
  type: 'publish' | 'deadline' | 'collaboration' | 'reminder' | 'review';
  content_type: 'audio' | 'video' | 'image' | 'document';
  date: string;
  time: string;
  status: 'scheduled' | 'in_progress' | 'completed' | 'overdue';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  tags: string[];
  collaborators?: string[];
  reminder_settings?: {
    enabled: boolean;
    advance_time: number; // minutes before event
  };
  metadata?: {
    platform?: string[];
    expected_duration?: number;
    budget?: number;
    target_audience?: string;
  };
}

export function ContentPlanningCalendar() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [viewMode, setViewMode] = useState<'month' | 'week' | 'day'>('month');
  const [events, setEvents] = useState<ContentEvent[]>([]);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [showEventModal, setShowEventModal] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<ContentEvent | null>(null);
  const [loading, setLoading] = useState(true);

  // Sample calendar events
  useEffect(() => {
    setTimeout(() => {
      const sampleEvents: ContentEvent[] = [
        {
          id: '1',
          title: 'Release New Track',
          description: 'Publish the new electronic track on all platforms',
          type: 'publish',
          content_type: 'audio',
          date: '2024-01-20',
          time: '10:00',
          status: 'scheduled',
          priority: 'high',
          tags: ['music', 'release', 'electronic'],
          collaborators: ['@producer', '@mixer'],
          reminder_settings: { enabled: true, advance_time: 60 },
          metadata: {
            platform: ['Spotify', 'Apple Music', 'YouTube'],
            expected_duration: 245,
            target_audience: 'Electronic music fans'
          }
        },
        {
          id: '2',
          title: 'Video Editing Deadline',
          description: 'Complete editing for tutorial video series',
          type: 'deadline',
          content_type: 'video',
          date: '2024-01-18',
          time: '17:00',
          status: 'in_progress',
          priority: 'urgent',
          tags: ['video', 'tutorial', 'editing'],
          reminder_settings: { enabled: true, advance_time: 120 },
          metadata: {
            expected_duration: 1800,
            target_audience: 'Content creators'
          }
        },
        {
          id: '3',
          title: 'Photo Shoot Planning',
          description: 'Plan portfolio photo shoot with team',
          type: 'collaboration',
          content_type: 'image',
          date: '2024-01-22',
          time: '14:30',
          status: 'scheduled',
          priority: 'medium',
          tags: ['photography', 'portfolio', 'planning'],
          collaborators: ['@photographer', '@stylist'],
          metadata: {
            budget: 2500,
            target_audience: 'Professional network'
          }
        },
        {
          id: '4',
          title: 'Content Review Meeting',
          description: 'Review Q1 content strategy and performance',
          type: 'review',
          content_type: 'document',
          date: '2024-01-25',
          time: '09:00',
          status: 'scheduled',
          priority: 'medium',
          tags: ['strategy', 'review', 'planning'],
          collaborators: ['@team-lead', '@analyst'],
          metadata: {
            expected_duration: 90,
            target_audience: 'Internal team'
          }
        },
        {
          id: '5',
          title: 'Upload Reminder',
          description: 'Upload final audio master to platform',
          type: 'reminder',
          content_type: 'audio',
          date: '2024-01-16',
          time: '11:00',
          status: 'completed',
          priority: 'low',
          tags: ['upload', 'reminder', 'audio'],
          reminder_settings: { enabled: true, advance_time: 30 }
        }
      ];
      
      setEvents(sampleEvents);
      setLoading(false);
    }, 500);
  }, []);

  const getDaysInMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const getMonthName = (date: Date) => {
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  };

  const getEventsForDate = (date: Date) => {
    const dateString = date.toISOString().split('T')[0];
    return events.filter(event => event.date === dateString);
  };

  const getEventTypeColor = (type: string) => {
    switch (type) {
      case 'publish': return 'bg-green-100 text-green-800 border-green-200';
      case 'deadline': return 'bg-red-100 text-red-800 border-red-200';
      case 'collaboration': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'reminder': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'review': return 'bg-purple-100 text-purple-800 border-purple-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return CheckCircleIcon;
      case 'in_progress': return ClockIcon;
      case 'overdue': return ExclamationTriangleIcon;
      case 'scheduled': return CalendarIcon;
      default: return CalendarIcon;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'text-red-600';
      case 'high': return 'text-orange-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      if (direction === 'prev') {
        newDate.setMonth(prev.getMonth() - 1);
      } else {
        newDate.setMonth(prev.getMonth() + 1);
      }
      return newDate;
    });
  };

  const renderCalendarDays = () => {
    const daysInMonth = getDaysInMonth(currentDate);
    const firstDay = getFirstDayOfMonth(currentDate);
    const days = [];

    // Empty cells for days before the first day of the month
    for (let i = 0; i < firstDay; i++) {
      days.push(
        <div key={`empty-${i}`} className="p-2 border border-gray-200"></div>
      );
    }

    // Days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
      const dayEvents = getEventsForDate(date);
      const isToday = date.toDateString() === new Date().toDateString();
      const isSelected = selectedDate?.toDateString() === date.toDateString();

      days.push(
        <div
          key={day}
          onClick={() => setSelectedDate(date)}
          className={`p-2 border border-gray-200 min-h-[100px] cursor-pointer hover:bg-gray-50 transition-colors ${
            isToday ? 'bg-blue-50 border-blue-300' : ''
          } ${isSelected ? 'bg-purple-50 border-purple-300' : ''}`}
        >
          <div className={`text-sm font-medium mb-1 ${
            isToday ? 'text-blue-600' : 'text-gray-900'
          }`}>
            {day}
          </div>
          <div className="space-y-1">
            {dayEvents.slice(0, 3).map((event) => {
              const StatusIcon = getStatusIcon(event.status);
              return (
                <div
                  key={event.id}
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedEvent(event);
                    setShowEventModal(true);
                  }}
                  className={`text-xs p-1 rounded border cursor-pointer hover:shadow-sm transition-shadow ${getEventTypeColor(event.type)}`}
                >
                  <div className="flex items-center space-x-1">
                    <StatusIcon className="w-3 h-3" />
                    <span className="truncate">{event.title}</span>
                  </div>
                  <div className="text-xs opacity-75">{event.time}</div>
                </div>
              );
            })}
            {dayEvents.length > 3 && (
              <div className="text-xs text-gray-500 text-center">
                +{dayEvents.length - 3} more
              </div>
            )}
          </div>
        </div>
      );
    }

    return days;
  };

  const renderWeekView = () => {
    // Implementation for week view would go here
    return (
      <div className="text-center py-12">
        <CalendarIcon className="w-12 h-12 mx-auto text-gray-400 mb-4" />
        <p className="text-gray-600">Week view coming soon</p>
      </div>
    );
  };

  const renderDayView = () => {
    // Implementation for day view would go here
    return (
      <div className="text-center py-12">
        <CalendarIcon className="w-12 h-12 mx-auto text-gray-400 mb-4" />
        <p className="text-gray-600">Day view coming soon</p>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md border p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-7 gap-2">
            {[...Array(35)].map((_, i) => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md border">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CalendarIcon className="w-5 h-5 text-indigo-500" />
            <h3 className="text-lg font-semibold text-gray-900">Content Planning Calendar</h3>
          </div>
          <div className="flex items-center space-x-2">
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('month')}
                className={`px-3 py-1 text-sm rounded-md transition-colors ${
                  viewMode === 'month' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600'
                }`}
              >
                Month
              </button>
              <button
                onClick={() => setViewMode('week')}
                className={`px-3 py-1 text-sm rounded-md transition-colors ${
                  viewMode === 'week' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600'
                }`}
              >
                Week
              </button>
              <button
                onClick={() => setViewMode('day')}
                className={`px-3 py-1 text-sm rounded-md transition-colors ${
                  viewMode === 'day' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600'
                }`}
              >
                Day
              </button>
            </div>
            <button className="btn-primary">
              <PlusIcon className="w-4 h-4 mr-2" />
              Add Event
            </button>
          </div>
        </div>
      </div>

      {/* Calendar Navigation */}
      {viewMode === 'month' && (
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <button
              onClick={() => navigateMonth('prev')}
              className="p-2 hover:bg-gray-200 rounded-full transition-colors"
            >
              <ChevronLeftIcon className="w-5 h-5 text-gray-600" />
            </button>
            <h4 className="text-xl font-semibold text-gray-900">
              {getMonthName(currentDate)}
            </h4>
            <button
              onClick={() => navigateMonth('next')}
              className="p-2 hover:bg-gray-200 rounded-full transition-colors"
            >
              <ChevronRightIcon className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>
      )}

      {/* Calendar Content */}
      <div className="p-6">
        {viewMode === 'month' && (
          <>
            {/* Day headers */}
            <div className="grid grid-cols-7 gap-2 mb-2">
              {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
                <div key={day} className="p-2 text-center text-sm font-semibold text-gray-700 bg-gray-100 rounded">
                  {day}
                </div>
              ))}
            </div>
            
            {/* Calendar grid */}
            <div className="grid grid-cols-7 gap-2">
              {renderCalendarDays()}
            </div>
          </>
        )}
        
        {viewMode === 'week' && renderWeekView()}
        {viewMode === 'day' && renderDayView()}
      </div>

      {/* Upcoming Events Sidebar */}
      <div className="border-t border-gray-200 p-6 bg-gray-50">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Events</h4>
        <div className="space-y-3 max-h-64 overflow-y-auto">
          {events
            .filter(event => new Date(event.date) >= new Date())
            .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
            .slice(0, 5)
            .map((event) => {
              const StatusIcon = getStatusIcon(event.status);
              return (
                <div
                  key={event.id}
                  onClick={() => {
                    setSelectedEvent(event);
                    setShowEventModal(true);
                  }}
                  className="bg-white rounded-lg p-3 border border-gray-200 hover:shadow-md transition-shadow cursor-pointer"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <StatusIcon className={`w-4 h-4 ${getPriorityColor(event.priority)}`} />
                        <h5 className="text-sm font-semibold text-gray-900">{event.title}</h5>
                      </div>
                      <p className="text-xs text-gray-600 mb-2">{event.description}</p>
                      <div className="flex items-center space-x-2 text-xs text-gray-500">
                        <span>{new Date(event.date).toLocaleDateString()}</span>
                        <span>•</span>
                        <span>{event.time}</span>
                        {event.reminder_settings?.enabled && (
                          <>
                            <span>•</span>
                            <BellIcon className="w-3 h-3" />
                          </>
                        )}
                      </div>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getEventTypeColor(event.type)}`}>
                      {event.type}
                    </span>
                  </div>
                  
                  {/* Tags */}
                  {event.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {event.tags.slice(0, 3).map((tag, index) => (
                        <span key={index} className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded-full text-xs">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
        </div>
      </div>

      {/* Event Modal */}
      {showEventModal && selectedEvent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Event Details</h3>
                <button
                  onClick={() => setShowEventModal(false)}
                  className="text-gray-400 hover:text-gray-600 text-xl font-semibold"
                >
                  ×
                </button>
              </div>
            </div>
            
            <div className="p-6">
              <div className="space-y-4">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900">{selectedEvent.title}</h4>
                  <p className="text-gray-600 mt-1">{selectedEvent.description}</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <label className="block text-gray-600 mb-1">Date</label>
                    <p className="font-medium">{new Date(selectedEvent.date).toLocaleDateString()}</p>
                  </div>
                  <div>
                    <label className="block text-gray-600 mb-1">Time</label>
                    <p className="font-medium">{selectedEvent.time}</p>
                  </div>
                  <div>
                    <label className="block text-gray-600 mb-1">Type</label>
                    <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium border ${getEventTypeColor(selectedEvent.type)}`}>
                      {selectedEvent.type}
                    </span>
                  </div>
                  <div>
                    <label className="block text-gray-600 mb-1">Priority</label>
                    <span className={`font-medium ${getPriorityColor(selectedEvent.priority)}`}>
                      {selectedEvent.priority}
                    </span>
                  </div>
                </div>
                
                {selectedEvent.tags.length > 0 && (
                  <div>
                    <label className="block text-gray-600 mb-2">Tags</label>
                    <div className="flex flex-wrap gap-1">
                      {selectedEvent.tags.map((tag, index) => (
                        <span key={index} className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded-full text-xs">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {selectedEvent.collaborators && selectedEvent.collaborators.length > 0 && (
                  <div>
                    <label className="block text-gray-600 mb-2">Collaborators</label>
                    <div className="space-y-1">
                      {selectedEvent.collaborators.map((collaborator, index) => (
                        <span key={index} className="inline-block px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs mr-1">
                          {collaborator}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {selectedEvent.metadata && (
                  <div>
                    <label className="block text-gray-600 mb-2">Additional Details</label>
                    <div className="bg-gray-50 rounded-lg p-3 text-sm space-y-2">
                      {selectedEvent.metadata.platform && (
                        <div className="flex justify-between">
                          <span>Platforms:</span>
                          <span>{selectedEvent.metadata.platform.join(', ')}</span>
                        </div>
                      )}
                      {selectedEvent.metadata.expected_duration && (
                        <div className="flex justify-between">
                          <span>Duration:</span>
                          <span>{Math.floor(selectedEvent.metadata.expected_duration / 60)}:{(selectedEvent.metadata.expected_duration % 60).toString().padStart(2, '0')}</span>
                        </div>
                      )}
                      {selectedEvent.metadata.budget && (
                        <div className="flex justify-between">
                          <span>Budget:</span>
                          <span>${selectedEvent.metadata.budget.toLocaleString()}</span>
                        </div>
                      )}
                      {selectedEvent.metadata.target_audience && (
                        <div className="flex justify-between">
                          <span>Audience:</span>
                          <span>{selectedEvent.metadata.target_audience}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
              
              <div className="flex space-x-3 mt-6">
                <button className="flex-1 btn-secondary">
                  <PencilIcon className="w-4 h-4 mr-2" />
                  Edit
                </button>
                <button className="flex-1 btn-primary">
                  <EyeIcon className="w-4 h-4 mr-2" />
                  View Content
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Calendar Legend */}
      <div className="border-t border-gray-200 px-6 py-4 bg-gray-50">
        <h5 className="text-sm font-semibold text-gray-700 mb-2">Event Types</h5>
        <div className="flex flex-wrap gap-3 text-xs">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-green-100 border border-green-200 rounded"></div>
            <span>Publish</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-red-100 border border-red-200 rounded"></div>
            <span>Deadline</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-blue-100 border border-blue-200 rounded"></div>
            <span>Collaboration</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-yellow-100 border border-yellow-200 rounded"></div>
            <span>Reminder</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-purple-100 border border-purple-200 rounded"></div>
            <span>Review</span>
          </div>
        </div>
      </div>
    </div>
  );
}