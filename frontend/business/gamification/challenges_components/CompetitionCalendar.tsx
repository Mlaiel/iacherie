/**
 * Competition Calendar - Ultra-Advanced Enterprise System
 * 
 * This component provides comprehensive competition calendar with
 * event scheduling and participation tracking.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️  CRITICAL LEGAL NOTICE:
 * This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
 * Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
 * Contact: mlaiel@live.de for licensing inquiries.
 * 
 * 🏆 Expert Development Team Specialties:
 * - Lead AI Developer: Advanced machine learning and AI systems
 * - Backend Senior Engineer: Enterprise Python/FastAPI architecture
 * - ML Engineer: TensorFlow/PyTorch and neural networks
 * - Database Administrator: PostgreSQL and vector databases
 * - Security Specialist: Enterprise security protocols
 * - Microservices Architect: Scalable distributed systems
 * - Audio Engineer: Professional audio processing
 * - DevOps Engineer: CI/CD and cloud infrastructure
 * - AI Prompt Engineer: Advanced prompt engineering
 */

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Competition, ApiResponse } from '../gamification/types';
import { gamificationStyles } from '../gamification/gamification.styles';
import { CalendarIcon, ClockIcon, UsersIcon, TrophyIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface CompetitionCalendarProps {
  userId: string;
  className?: string;
  onCompetitionClick?: (competition: Competition) => void;
}

interface CalendarEvent {
  id: string;
  title: string;
  startDate: Date;
  endDate: Date;
  type: 'competition' | 'challenge' | 'event';
  status: 'upcoming' | 'active' | 'completed';
  participants: number;
  isParticipating: boolean;
}

const CompetitionCalendar: React.FC<CompetitionCalendarProps> = ({
  userId,
  className,
  onCompetitionClick
}) => {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedView, setSelectedView] = useState<'month' | 'week' | 'list'>('month');

  const fetchEvents = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/gamification/calendar?userId=${userId}&month=${currentDate.getMonth() + 1}&year=${currentDate.getFullYear()}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
      });
      const result: ApiResponse<CalendarEvent[]> = await response.json();
      if (result.success) setEvents(result.data!);
    } catch (err) {
      console.error('Failed to fetch calendar events:', err);
    } finally {
      setLoading(false);
    }
  }, [userId, currentDate]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add all days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }
    
    return days;
  };

  const getEventsForDay = (date: Date) => {
    return events.filter(event => {
      const eventStart = new Date(event.startDate);
      const eventEnd = new Date(event.endDate);
      return date >= eventStart && date <= eventEnd;
    });
  };

  const getEventTypeColor = (type: CalendarEvent['type']) => {
    switch (type) {
      case 'competition':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'challenge':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'event':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  if (loading) {
    return (
      <div className={clsx(gamificationStyles.container.main, className)}>
        <div className="max-w-6xl mx-auto p-6">
          <div className={gamificationStyles.loading.skeleton + " h-8 w-64 mb-6"} />
          <div className={gamificationStyles.loading.skeleton + " h-96 w-full"} />
        </div>
      </div>
    );
  }

  return (
    <div className={clsx(gamificationStyles.container.main, className)}>
      <div className="max-w-6xl mx-auto p-6">
        <div className="mb-8">
          <div className={gamificationStyles.utils.flexBetween}>
            <div>
              <h1 className={clsx(gamificationStyles.typography.heading.primary, "flex items-center")}>
                <CalendarIcon className="w-8 h-8 mr-3 text-blue-500" />
                Competition Calendar
              </h1>
              <p className={gamificationStyles.typography.body.regular}>
                View upcoming competitions and events
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setSelectedView('month')}
                className={clsx(
                  gamificationStyles.buttons.ghost,
                  selectedView === 'month' && "bg-blue-100 text-blue-700"
                )}
              >
                Month
              </button>
              <button
                onClick={() => setSelectedView('list')}
                className={clsx(
                  gamificationStyles.buttons.ghost,
                  selectedView === 'list' && "bg-blue-100 text-blue-700"
                )}
              >
                List
              </button>
            </div>
          </div>
        </div>

        <div className={gamificationStyles.container.section}>
          {/* Calendar Header */}
          <div className={gamificationStyles.utils.flexBetween + " mb-6"}>
            <button
              onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1))}
              className={gamificationStyles.buttons.ghost}
            >
              ← Previous
            </button>
            <h2 className={gamificationStyles.typography.heading.secondary}>
              {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
            </h2>
            <button
              onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1))}
              className={gamificationStyles.buttons.ghost}
            >
              Next →
            </button>
          </div>

          {selectedView === 'month' ? (
            <>
              {/* Calendar Grid */}
              <div className="grid grid-cols-7 gap-1 mb-2">
                {dayNames.map(day => (
                  <div key={day} className={clsx(
                    gamificationStyles.typography.body.small,
                    "p-2 text-center font-medium text-slate-600"
                  )}>
                    {day}
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-7 gap-1">
                {getDaysInMonth(currentDate).map((date, index) => {
                  if (!date) {
                    return <div key={index} className="h-24" />;
                  }

                  const dayEvents = getEventsForDay(date);
                  const isToday = date.toDateString() === new Date().toDateString();

                  return (
                    <div
                      key={date.toISOString()}
                      className={clsx(
                        "h-24 p-1 border border-slate-200 dark:border-slate-700",
                        isToday && "bg-blue-50 dark:bg-blue-900/20"
                      )}
                    >
                      <div className={clsx(
                        gamificationStyles.typography.body.small,
                        "font-medium mb-1",
                        isToday && "text-blue-600"
                      )}>
                        {date.getDate()}
                      </div>
                      <div className="space-y-1">
                        {dayEvents.slice(0, 2).map(event => (
                          <div
                            key={event.id}
                            className={clsx(
                              "text-xs p-1 rounded border cursor-pointer",
                              getEventTypeColor(event.type)
                            )}
                            onClick={() => onCompetitionClick?.(event as any)}
                            title={event.title}
                          >
                            {event.title.substring(0, 12)}...
                          </div>
                        ))}
                        {dayEvents.length > 2 && (
                          <div className={gamificationStyles.typography.body.small}>
                            +{dayEvents.length - 2} more
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          ) : (
            // List View
            <div className="space-y-4">
              {events.map(event => (
                <div
                  key={event.id}
                  className={clsx(
                    gamificationStyles.container.compactCard,
                    "cursor-pointer hover:shadow-md transition-all duration-200"
                  )}
                  onClick={() => onCompetitionClick?.(event as any)}
                >
                  <div className={gamificationStyles.utils.flexBetween}>
                    <div className="flex items-center">
                      <div className={clsx(
                        "w-3 h-3 rounded-full mr-3",
                        event.type === 'competition' && "bg-purple-500",
                        event.type === 'challenge' && "bg-blue-500",
                        event.type === 'event' && "bg-green-500"
                      )} />
                      <div>
                        <h3 className={clsx(gamificationStyles.typography.body.regular, "font-medium")}>
                          {event.title}
                        </h3>
                        <div className={clsx(gamificationStyles.typography.body.small, "flex items-center gap-4")}>
                          <span className="flex items-center">
                            <ClockIcon className="w-4 h-4 mr-1" />
                            {new Date(event.startDate).toLocaleDateString()} - {new Date(event.endDate).toLocaleDateString()}
                          </span>
                          <span className="flex items-center">
                            <UsersIcon className="w-4 h-4 mr-1" />
                            {event.participants} participants
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={clsx(
                        "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium",
                        event.status === 'upcoming' && "bg-blue-100 text-blue-800",
                        event.status === 'active' && "bg-green-100 text-green-800",
                        event.status === 'completed' && "bg-slate-100 text-slate-800"
                      )}>
                        {event.status}
                      </div>
                      {event.isParticipating && (
                        <div className={clsx(gamificationStyles.badges.featured, "mt-1")}>
                          Participating
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {events.length === 0 && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📅</div>
              <h3 className={gamificationStyles.typography.heading.secondary}>
                No Events This Month
              </h3>
              <p className={gamificationStyles.typography.body.regular}>
                Check back later for upcoming competitions and challenges.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CompetitionCalendar;