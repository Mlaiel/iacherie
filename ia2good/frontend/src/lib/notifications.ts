/*
 * Owner: Fahed Mlaiel
 * Contact: mlaiel@live.de
 * Notice: Attribution to Fahed Mlaiel is mandatory in all copies, forks, and derivatives.
 */

import { CaseReport, NotificationPreferences, Location } from './types';
import { calculateDistance } from './geolocation';
import { isQuietHour } from './utils';
import { toast } from 'sonner';

class NotificationService {
  private static instance: NotificationService;
  private permission: NotificationPermission = 'default';

  private constructor() {
    this.requestPermission();
  }

  static getInstance(): NotificationService {
    if (!NotificationService.instance) {
      NotificationService.instance = new NotificationService();
    }
    return NotificationService.instance;
  }

  async requestPermission(): Promise<NotificationPermission> {
    if ('Notification' in window) {
      this.permission = await Notification.requestPermission();
    }
    return this.permission;
  }

  shouldNotify(
    caseReport: CaseReport, 
    preferences: NotificationPreferences, 
    userLocation?: Location
  ): boolean {
    // Check if notifications are enabled
    if (!preferences.enabled) return false;

    // Check if category is enabled
    if (!preferences.categories.includes(caseReport.type)) return false;

    // Check if urgency level is enabled
    if (!preferences.urgencyLevels.includes(caseReport.urgency)) return false;

    // Check quiet hours (only for non-high urgency)
    if (caseReport.urgency !== 'high' && isQuietHour(preferences.quietHours)) {
      return false;
    }

    // Check distance if user location is available
    if (userLocation) {
      const distance = calculateDistance(userLocation, caseReport.location);
      if (distance > preferences.radius) return false;
    }

    return true;
  }

  notify(caseReport: CaseReport, distance?: number): void {
    const title = `Someone needs help nearby`;
    const body = `${caseReport.type === 'homeless' ? 'Person' : 'Animal'} needs assistance${
      distance ? ` (${distance.toFixed(1)}km away)` : ''
    }`;

    // Show browser notification if permission granted
    if (this.permission === 'granted' && 'Notification' in window) {
      const notification = new Notification(title, {
        body,
        icon: '/solidarity-icon.png', // Could add an icon
        badge: '/solidarity-badge.png',
        tag: `case-${caseReport.id}`,
        data: caseReport,
        requireInteraction: caseReport.urgency === 'high'
      });

      notification.onclick = () => {
        window.focus();
        notification.close();
        // Could add navigation to the specific case
      };

      // Auto-close after 10 seconds for non-urgent cases
      if (caseReport.urgency !== 'high') {
        setTimeout(() => notification.close(), 10000);
      }
    }

    // Also show toast notification
    const urgencyColor = caseReport.urgency === 'high' ? 'destructive' : 'default';
    toast(title, {
      description: `${caseReport.description.slice(0, 80)}${caseReport.description.length > 80 ? '...' : ''}`,
      action: {
        label: 'View',
        onClick: () => {
          // Could add navigation to the case
          console.log('Navigate to case:', caseReport.id);
        }
      },
      duration: caseReport.urgency === 'high' ? 0 : 5000 // Keep high urgency notifications until dismissed
    });
  }

  // Simulate receiving a new case notification
  simulateNotification(caseReport: CaseReport, preferences: NotificationPreferences, userLocation?: Location): void {
    if (this.shouldNotify(caseReport, preferences, userLocation)) {
      const distance = userLocation ? calculateDistance(userLocation, caseReport.location) : undefined;
      this.notify(caseReport, distance);
    }
  }
}

export const notificationService = NotificationService.getInstance();