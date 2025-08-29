/**
 * Protection Alert Notification Templates
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { NotificationTemplate, TemplateVariables, NotificationPayload } from '../types/notification_types';

export class ProtectionAlertTemplates {
  /**
   * Get copyright violation alert template
   */
  public static getCopyrightViolationTemplate(): NotificationTemplate {
    return {
      id: 'protection_copyright_violation',
      name: 'Copyright Violation Alert',
      type: 'protection_alert',
      title: '🛡️ Copyright Violation Detected',
      body: 'Your {contentType} "{contentName}" may have been uploaded without permission on {platform}',
      variables: ['contentType', 'contentName', 'platform', 'severity', 'violationId'],
      platforms: {
        android: {
          channelId: 'protection_alerts',
          priority: 'high',
          category: 'alert',
          ledColor: '#FF4444',
          vibrationPattern: [0, 300, 100, 300],
          largeIcon: 'ic_shield_alert'
        },
        ios: {
          sound: {
            name: 'protection_alert.wav',
            critical: true,
            volume: 1.0
          },
          category: 'PROTECTION_ALERT',
          interruptionLevel: 'timeSensitive',
          relevanceScore: 1.0
        },
        web: {
          icon: '/icons/shield-alert.png',
          badge: '/icons/badge-alert.png',
          requireInteraction: true,
          vibrate: [200, 100, 200]
        }
      },
      actions: [
        {
          id: 'view_violation',
          title: 'View Details',
          type: 'button',
          deepLink: 'ainflue://protection/violations/{violationId}'
        },
        {
          id: 'take_action',
          title: 'Take Action',
          type: 'button',
          deepLink: 'ainflue://protection/violations/{violationId}/actions'
        },
        {
          id: 'dismiss',
          title: 'Dismiss',
          type: 'button'
        }
      ],
      defaultSettings: {
        priority: 'high',
        ttl: 86400, // 24 hours
        badge: 1,
        sound: 'protection_alert.wav',
        color: '#FF4444'
      }
    };
  }

  /**
   * Get content fingerprinting complete template
   */
  public static getFingerprintingCompleteTemplate(): NotificationTemplate {
    return {
      id: 'protection_fingerprinting_complete',
      name: 'Content Fingerprinting Complete',
      type: 'protection_alert',
      title: '✅ Content Protection Activated',
      body: 'Your {contentType} "{contentName}" is now protected and being monitored',
      variables: ['contentType', 'contentName', 'protectionId'],
      platforms: {
        android: {
          channelId: 'protection_status',
          priority: 'default',
          category: 'status',
          ledColor: '#4CAF50',
          largeIcon: 'ic_shield_check'
        },
        ios: {
          sound: 'protection_success.wav',
          category: 'PROTECTION_STATUS',
          interruptionLevel: 'active',
          relevanceScore: 0.8
        },
        web: {
          icon: '/icons/shield-check.png',
          badge: '/icons/badge-success.png'
        }
      },
      actions: [
        {
          id: 'view_protection',
          title: 'View Protection',
          type: 'button',
          deepLink: 'ainflue://protection/content/{protectionId}'
        }
      ],
      defaultSettings: {
        priority: 'normal',
        ttl: 43200, // 12 hours
        sound: 'protection_success.wav',
        color: '#4CAF50'
      }
    };
  }

  /**
   * Get DMCA takedown sent template
   */
  public static getDMCATakedownTemplate(): NotificationTemplate {
    return {
      id: 'protection_dmca_sent',
      name: 'DMCA Takedown Notice Sent',
      type: 'protection_alert',
      title: '📨 DMCA Takedown Notice Sent',
      body: 'Takedown notice sent to {platform} for "{contentName}" - tracking reference: {dmcaId}',
      variables: ['platform', 'contentName', 'dmcaId', 'estimatedResponse'],
      platforms: {
        android: {
          channelId: 'protection_actions',
          priority: 'default',
          category: 'progress',
          ledColor: '#2196F3',
          largeIcon: 'ic_legal_action'
        },
        ios: {
          sound: 'notification.wav',
          category: 'PROTECTION_ACTION',
          interruptionLevel: 'active',
          relevanceScore: 0.9
        },
        web: {
          icon: '/icons/legal-action.png',
          badge: '/icons/badge-action.png'
        }
      },
      actions: [
        {
          id: 'track_dmca',
          title: 'Track Progress',
          type: 'button',
          deepLink: 'ainflue://protection/dmca/{dmcaId}'
        },
        {
          id: 'view_notice',
          title: 'View Notice',
          type: 'button',
          deepLink: 'ainflue://protection/dmca/{dmcaId}/notice'
        }
      ],
      defaultSettings: {
        priority: 'normal',
        ttl: 86400, // 24 hours
        sound: 'notification.wav',
        color: '#2196F3'
      }
    };
  }

  /**
   * Get violation resolved template
   */
  public static getViolationResolvedTemplate(): NotificationTemplate {
    return {
      id: 'protection_violation_resolved',
      name: 'Copyright Violation Resolved',
      type: 'protection_alert',
      title: '🎉 Violation Resolved!',
      body: 'Copyright violation for "{contentName}" on {platform} has been successfully resolved',
      variables: ['contentName', 'platform', 'resolutionMethod', 'violationId'],
      platforms: {
        android: {
          channelId: 'protection_success',
          priority: 'default',
          category: 'status',
          ledColor: '#4CAF50',
          largeIcon: 'ic_shield_success'
        },
        ios: {
          sound: 'success.wav',
          category: 'PROTECTION_SUCCESS',
          interruptionLevel: 'active',
          relevanceScore: 0.9
        },
        web: {
          icon: '/icons/shield-success.png',
          badge: '/icons/badge-success.png'
        }
      },
      actions: [
        {
          id: 'view_details',
          title: 'View Details',
          type: 'button',
          deepLink: 'ainflue://protection/violations/{violationId}/resolution'
        }
      ],
      defaultSettings: {
        priority: 'normal',
        ttl: 43200, // 12 hours
        sound: 'success.wav',
        color: '#4CAF50'
      }
    };
  }

  /**
   * Generate protection alert notification
   */
  public static generateProtectionAlert(
    templateId: string,
    variables: TemplateVariables,
    userId: string
  ): NotificationPayload | null {
    const templates = {
      'copyright_violation': this.getCopyrightViolationTemplate(),
      'fingerprinting_complete': this.getFingerprintingCompleteTemplate(),
      'dmca_takedown': this.getDMCATakedownTemplate(),
      'violation_resolved': this.getViolationResolvedTemplate()
    };

    const template = templates[templateId as keyof typeof templates];
    if (!template) {
      return null;
    }

    // Replace variables in title and body
    let title = template.title;
    let body = template.body;

    template.variables.forEach(variable => {
      const value = variables[variable]?.toString() || `{${variable}}`;
      title = title.replace(new RegExp(`{${variable}}`, 'g'), value);
      body = body.replace(new RegExp(`{${variable}}`, 'g'), value);
    });

    // Replace variables in deep links
    const actions = template.actions?.map(action => ({
      ...action,
      deepLink: action.deepLink ? this.replaceVariables(action.deepLink, variables) : undefined
    }));

    return {
      userId,
      title,
      body,
      type: template.type,
      data: {
        templateId: template.id,
        variables,
        timestamp: new Date().toISOString()
      },
      priority: template.defaultSettings?.priority,
      ttl: template.defaultSettings?.ttl,
      badge: template.defaultSettings?.badge,
      sound: template.defaultSettings?.sound,
      color: template.defaultSettings?.color,
      actions,
      deepLink: actions?.[0]?.deepLink,
      analytics: true
    };
  }

  /**
   * Replace variables in a string
   */
  private static replaceVariables(text: string, variables: TemplateVariables): string {
    let result = text;
    
    Object.entries(variables).forEach(([key, value]) => {
      result = result.replace(new RegExp(`{${key}}`, 'g'), value?.toString() || `{${key}}`);
    });
    
    return result;
  }

  /**
   * Get all protection alert templates
   */
  public static getAllTemplates(): NotificationTemplate[] {
    return [
      this.getCopyrightViolationTemplate(),
      this.getFingerprintingCompleteTemplate(),
      this.getDMCATakedownTemplate(),
      this.getViolationResolvedTemplate()
    ];
  }
}