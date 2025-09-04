/**
 * Embeddable Widget System - Main Entry Point
 * 
 * Provides embeddable widgets for external websites
 * Supports analytics, protection status, and content previews
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React from 'react';
import { AnalyticsWidget } from './components/AnalyticsWidget';
import { ProtectionWidget } from './components/ProtectionWidget';
import { ContentWidget } from './components/ContentWidget';
import { WidgetBuilder } from './builder/WidgetBuilder';
import { WidgetConfig } from './config/WidgetConfig';

export interface EmbeddableWidgetProps {
  type: 'analytics' | 'protection' | 'content' | 'builder' | 'config';
  config?: {
    apiKey?: string;
    userId?: string;
    theme?: 'light' | 'dark' | 'auto';
    size?: 'small' | 'medium' | 'large';
    showTitle?: boolean;
    customColors?: {
      primary?: string;
      secondary?: string;
      background?: string;
      text?: string;
    };
  };
  data?: Record<string, unknown>;
}

export function EmbeddableWidget({ type, config = {}, data }: EmbeddableWidgetProps) {
  const {
    apiKey = '',
    userId = '',
    theme = 'light',
    size = 'medium',
    showTitle = true,
    customColors = {}
  } = config;

  // Apply custom CSS variables for theming
  const customStyle = {
    '--widget-primary': customColors.primary || '#3b82f6',
    '--widget-secondary': customColors.secondary || '#8b5cf6',
    '--widget-background': customColors.background || theme === 'dark' ? '#1f2937' : '#ffffff',
    '--widget-text': customColors.text || theme === 'dark' ? '#ffffff' : '#1f2937',
  } as React.CSSProperties;

  const baseClasses = `
    ainflue-widget 
    ${theme === 'dark' ? 'widget-dark' : 'widget-light'} 
    ${size === 'small' ? 'widget-small' : size === 'large' ? 'widget-large' : 'widget-medium'}
  `;

  const renderWidget = () => {
    switch (type) {
      case 'analytics':
        return (
          <AnalyticsWidget 
            apiKey={apiKey}
            userId={userId}
            showTitle={showTitle}
            data={data}
          />
        );
      
      case 'protection':
        return (
          <ProtectionWidget 
            apiKey={apiKey}
            userId={userId}
            showTitle={showTitle}
            data={data}
          />
        );
      
      case 'content':
        return (
          <ContentWidget 
            apiKey={apiKey}
            userId={userId}
            showTitle={showTitle}
            data={data}
          />
        );
      
      case 'builder':
        return <WidgetBuilder />;
      
      case 'config':
        return <WidgetConfig />;
      
      default:
        return (
          <div className="p-4 text-center text-gray-500">
            Type de widget non reconnu: {type}
          </div>
        );
    }
  };

  return (
    <div 
      className={baseClasses}
      style={customStyle}
    >
      {renderWidget()}
    </div>
  );
}

// Export for standalone usage
export default EmbeddableWidget;

// CSS classes for widget styling
export const widgetStyles = `
  .ainflue-widget {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    border-radius: 8px;
    border: 1px solid var(--widget-border, #e5e7eb);
    background: var(--widget-background, #ffffff);
    color: var(--widget-text, #1f2937);
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;
  }

  .ainflue-widget:hover {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  }

  .widget-small {
    min-height: 100px;
    max-width: 200px;
  }

  .widget-medium {
    min-height: 200px;
    max-width: 400px;
  }

  .widget-large {
    min-height: 300px;
    max-width: 600px;
  }

  .widget-dark {
    --widget-background: #1f2937;
    --widget-text: #ffffff;
    --widget-border: #374151;
  }

  .widget-light {
    --widget-background: #ffffff;
    --widget-text: #1f2937;
    --widget-border: #e5e7eb;
  }
`;