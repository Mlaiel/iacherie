/**
 * ⚡ DevOps Monitoring Dashboard Tests - DevOps Engineer Excellence
 * 
 * @fileoverview Comprehensive testing suite for DevOps monitoring and infrastructure management
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DevOpsMonitoringDashboard } from '../../presentation/devops_monitoring_dashboard';

describe('DevOps Monitoring Dashboard - DevOps Engineer & Backend Senior', () => {
  describe('⚡ DevOps Engineer - Infrastructure Monitoring', () => {
    test('should render comprehensive monitoring dashboard', () => {
      render(<DevOpsMonitoringDashboard />);
      
      expect(screen.getByText('DevOps Infrastructure Monitoring')).toBeInTheDocument();
      expect(screen.getByText('System Health Overview')).toBeInTheDocument();
      expect(screen.getByText('Performance Metrics')).toBeInTheDocument();
      expect(screen.getByText('Service Topology')).toBeInTheDocument();
      expect(screen.getByText('Alert Management')).toBeInTheDocument();
    });

    test('should display real-time system health metrics', async () => {
      render(<DevOpsMonitoringDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('cpu-usage')).toBeInTheDocument();
        expect(screen.getByTestId('memory-usage')).toBeInTheDocument();
        expect(screen.getByTestId('disk-usage')).toBeInTheDocument();
        expect(screen.getByTestId('network-io')).toBeInTheDocument();
      });

      // Check that metrics are displaying valid values
      const cpuUsage = screen.getByTestId('cpu-usage');
      expect(cpuUsage).toHaveTextContent(/\d+%/);
      
      const memoryUsage = screen.getByTestId('memory-usage');
      expect(memoryUsage).toHaveTextContent(/\d+(\.\d+)?\s*(GB|MB)/);
    });

    test('should show service topology visualization', async () => {
      render(<DevOpsMonitoringDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('service-topology')).toBeInTheDocument();
      });

      const topology = screen.getByTestId('service-topology');
      
      // Check for key services
      expect(topology).toHaveTextContent('Frontend');
      expect(topology).toHaveTextContent('API Gateway');
      expect(topology).toHaveTextContent('Database');
      expect(topology).toHaveTextContent('Redis Cache');
      expect(topology).toHaveTextContent('Message Queue');
    });

    test('should handle alert management and escalation', async () => {
      render(<DevOpsMonitoringDashboard />);
      
      // Wait for alerts to load
      await waitFor(() => {
        expect(screen.getByTestId('alerts-panel')).toBeInTheDocument();
      });

      // Check alert severity filtering
      const criticalFilter = screen.getByTestId('filter-critical');
      fireEvent.click(criticalFilter);

      await waitFor(() => {
        const criticalAlerts = screen.getAllByTestId(/alert-.*-critical/);
        expect(criticalAlerts.length).toBeGreaterThan(0);
      });

      // Test alert acknowledgment
      const firstAlert = screen.getByTestId('alert-0');
      const ackButton = firstAlert.querySelector('[data-testid="acknowledge-alert"]');
      
      if (ackButton) {
        fireEvent.click(ackButton);
        
        await waitFor(() => {
          expect(firstAlert).toHaveClass('acknowledged');
        });
      }
    });

    test('should display performance trends and analytics', async () => {
      render(<DevOpsMonitoringDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('performance-charts')).toBeInTheDocument();
      });

      const performanceSection = screen.getByTestId('performance-charts');
      
      // Check for different chart types
      expect(performanceSection).toHaveTextContent('Response Time Trends');
      expect(performanceSection).toHaveTextContent('Throughput Analysis');
      expect(performanceSection).toHaveTextContent('Error Rate Monitoring');
      expect(performanceSection).toHaveTextContent('Resource Utilization');
    });

    test('should support infrastructure scaling operations', async () => {
      render(<DevOpsMonitoringDashboard />);
      
      // Navigate to scaling section
      const scalingTab = screen.getByTestId('scaling-management');
      fireEvent.click(scalingTab);

      await waitFor(() => {
        expect(screen.getByTestId('auto-scaling-config')).toBeInTheDocument();
      });

      // Test auto-scaling configuration
      const autoScalingToggle = screen.getByTestId('enable-auto-scaling');
      fireEvent.click(autoScalingToggle);

      await waitFor(() => {
        expect(screen.getByTestId('scaling-policies')).toBeInTheDocument();
      });

      // Verify scaling policies are configurable
      const cpuThreshold = screen.getByTestId('cpu-scale-threshold');
      fireEvent.change(cpuThreshold, { target: { value: '80' } });
      
      expect(cpuThreshold).toHaveValue('80');
    });
  });

  describe('🏗️ Backend Senior - System Architecture Monitoring', () => {
    test('should monitor microservices health and dependencies', async () => {
      render(<DevOpsMonitoringDashboard />);
      
      const servicesTab = screen.getByTestId('services-health');
      fireEvent.click(servicesTab);

      await waitFor(() => {
        expect(screen.getByTestId('services-grid')).toBeInTheDocument();
      });

      const servicesGrid = screen.getByTestId('services-grid');
      
      // Check for microservices
      expect(servicesGrid).toHaveTextContent('User Service');
      expect(servicesGrid).toHaveTextContent('Content Service');
      expect(servicesGrid).toHaveTextContent('Analytics Service');
      expect(servicesGrid).toHaveTextContent('Notification Service');

      // Verify health status indicators
      const healthIndicators = screen.getAllByTestId(/service-.*-health/);
      expect(healthIndicators.length).toBeGreaterThan(0);
      
      healthIndicators.forEach(indicator => {
        expect(indicator).toHaveClass(/health-(healthy|warning|critical)/);
      });
    });

    test('should track API performance and rate limiting', async () => {
      render(<DevOpsMonitoringDashboard />);
      
      const apiTab = screen.getByTestId('api-monitoring');
      fireEvent.click(apiTab);

      await waitFor(() => {
        expect(screen.getByTestId('api-metrics')).toBeInTheDocument();
      });

      const apiMetrics = screen.getByTestId('api-metrics');
      
      // Check API endpoint monitoring
      expect(apiMetrics).toHaveTextContent('Total Requests');
      expect(apiMetrics).toHaveTextContent('Success Rate');
      expect(apiMetrics).toHaveTextContent('Average Response Time');
      expect(apiMetrics).toHaveTextContent('Rate Limit Status');

      // Verify rate limiting visualization
      const rateLimitChart = screen.getByTestId('rate-limit-chart');
      expect(rateLimitChart).toBeInTheDocument();
    });

    test('should monitor database performance and connections', async () => {
      render(<DevOpsMonitoringDashboard />);
      
      const dbTab = screen.getByTestId('database-monitoring');
      fireEvent.click(dbTab);

      await waitFor(() => {
        expect(screen.getByTestId('db-metrics')).toBeInTheDocument();
      });

      const dbMetrics = screen.getByTestId('db-metrics');
      
      // Check database metrics
      expect(dbMetrics).toHaveTextContent('Active Connections');
      expect(dbMetrics).toHaveTextContent('Query Performance');
      expect(dbMetrics).toHaveTextContent('Slow Queries');
      expect(dbMetrics).toHaveTextContent('Storage Usage');

      // Verify connection pool monitoring
      const connectionPool = screen.getByTestId('connection-pool-status');
      expect(connectionPool).toBeInTheDocument();
    });

    test('should provide deployment pipeline monitoring', async () => {
      render(<DevOpsMonitoringDashboard />);
      
      const deploymentTab = screen.getByTestId('deployment-pipeline');
      fireEvent.click(deploymentTab);

      await waitFor(() => {
        expect(screen.getByTestId('pipeline-status')).toBeInTheDocument();
      });

      const pipelineStatus = screen.getByTestId('pipeline-status');
      
      // Check deployment stages
      expect(pipelineStatus).toHaveTextContent('Build Stage');
      expect(pipelineStatus).toHaveTextContent('Test Stage');
      expect(pipelineStatus).toHaveTextContent('Deploy Stage');
      expect(pipelineStatus).toHaveTextContent('Verification Stage');

      // Verify pipeline history
      const pipelineHistory = screen.getByTestId('pipeline-history');
      expect(pipelineHistory).toBeInTheDocument();
    });
  });

  describe('📊 Performance Analytics & Optimization', () => {
    test('should provide comprehensive performance insights', async () => {
      render(<DevOpsMonitoringDashboard />);
      
      const analyticsTab = screen.getByTestId('performance-analytics');
      fireEvent.click(analyticsTab);

      await waitFor(() => {
        expect(screen.getByTestId('analytics-dashboard')).toBeInTheDocument();
      });

      const analytics = screen.getByTestId('analytics-dashboard');
      
      // Check analytics sections
      expect(analytics).toHaveTextContent('Performance Trends');
      expect(analytics).toHaveTextContent('Bottleneck Analysis');
      expect(analytics).toHaveTextContent('Capacity Planning');
      expect(analytics).toHaveTextContent('Cost Optimization');
    });

    test('should support performance optimization recommendations', async () => {
      render(<DevOpsMonitoringDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('optimization-recommendations')).toBeInTheDocument();
      });

      const recommendations = screen.getByTestId('optimization-recommendations');
      
      // Verify recommendation types
      expect(recommendations).toHaveTextContent('Scale Resources');
      expect(recommendations).toHaveTextContent('Optimize Queries');
      expect(recommendations).toHaveTextContent('Cache Strategy');
      expect(recommendations).toHaveTextContent('Load Balancing');
    });
  });

  describe('🚨 Incident Response & Recovery', () => {
    test('should provide incident management workflow', async () => {
      render(<DevOpsMonitoringDashboard />);
      
      const incidentTab = screen.getByTestId('incident-management');
      fireEvent.click(incidentTab);

      await waitFor(() => {
        expect(screen.getByTestId('incident-board')).toBeInTheDocument();
      });

      // Test incident creation
      const createIncidentBtn = screen.getByTestId('create-incident');
      fireEvent.click(createIncidentBtn);

      await waitFor(() => {
        expect(screen.getByTestId('incident-form')).toBeInTheDocument();
      });

      // Fill incident details
      const titleInput = screen.getByTestId('incident-title');
      const severitySelect = screen.getByTestId('incident-severity');
      
      fireEvent.change(titleInput, { target: { value: 'Database Connection Issues' } });
      fireEvent.change(severitySelect, { target: { value: 'high' } });

      const submitBtn = screen.getByTestId('submit-incident');
      fireEvent.click(submitBtn);

      await waitFor(() => {
        expect(screen.getByText('Database Connection Issues')).toBeInTheDocument();
      });
    });

    test('should support automated recovery procedures', async () => {
      render(<DevOpsMonitoringDashboard />);
      
      const recoveryTab = screen.getByTestId('recovery-procedures');
      fireEvent.click(recoveryTab);

      await waitFor(() => {
        expect(screen.getByTestId('recovery-automation')).toBeInTheDocument();
      });

      const automation = screen.getByTestId('recovery-automation');
      
      // Check automated procedures
      expect(automation).toHaveTextContent('Auto Restart Services');
      expect(automation).toHaveTextContent('Failover Database');
      expect(automation).toHaveTextContent('Scale Resources');
      expect(automation).toHaveTextContent('Clear Cache');
    });
  });

  describe('🔧 Configuration & Customization', () => {
    test('should allow dashboard customization', async () => {
      render(<DevOpsMonitoringDashboard />);
      
      const settingsBtn = screen.getByTestId('dashboard-settings');
      fireEvent.click(settingsBtn);

      await waitFor(() => {
        expect(screen.getByTestId('customization-panel')).toBeInTheDocument();
      });

      const customization = screen.getByTestId('customization-panel');
      
      // Test widget management
      const addWidgetBtn = customization.querySelector('[data-testid="add-widget"]');
      if (addWidgetBtn) {
        fireEvent.click(addWidgetBtn);
        
        await waitFor(() => {
          expect(screen.getByTestId('widget-gallery')).toBeInTheDocument();
        });
      }
    });

    test('should support multi-environment monitoring', async () => {
      render(<DevOpsMonitoringDashboard />);
      
      const envSelector = screen.getByTestId('environment-selector');
      fireEvent.click(envSelector);

      await waitFor(() => {
        expect(screen.getByTestId('environment-dropdown')).toBeInTheDocument();
      });

      const environments = ['development', 'staging', 'production'];
      environments.forEach(env => {
        expect(screen.getByText(env)).toBeInTheDocument();
      });

      // Switch to staging environment
      const stagingOption = screen.getByText('staging');
      fireEvent.click(stagingOption);

      await waitFor(() => {
        expect(screen.getByTestId('environment-badge')).toHaveTextContent('staging');
      });
    });
  });
});