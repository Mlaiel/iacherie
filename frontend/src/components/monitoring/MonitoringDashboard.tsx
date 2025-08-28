import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, Shield, Eye, Clock, MapPin, ExternalLink } from 'lucide-react';

interface ViolationAlert {
  id: string;
  platform: string;
  contentTitle: string;
  violationType: 'copyright' | 'trademark' | 'unauthorized_use';
  confidence: number;
  detectedAt: Date;
  url: string;
  status: 'detected' | 'dmca_sent' | 'resolved' | 'disputed';
  fingerprint: string;
}

interface MonitoringDashboardProps {
  userId?: string;
}

const MonitoringDashboard: React.FC<MonitoringDashboardProps> = ({ userId }) => {
  const [violations, setViolations] = useState<ViolationAlert[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [stats, setStats] = useState({
    totalScans: 0,
    activeMonitoring: 0,
    violationsFound: 0,
    resolvedCases: 0
  });

  // Simulate real-time monitoring
  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate new violation detection
      if (Math.random() < 0.1) { // 10% chance every 5 seconds
        const newViolation: ViolationAlert = {
          id: Math.random().toString(36).substr(2, 9),
          platform: ['YouTube', 'Instagram', 'TikTok', 'Facebook', 'Twitter'][Math.floor(Math.random() * 5)],
          contentTitle: `Content ${Math.floor(Math.random() * 1000)}`,
          violationType: ['copyright', 'trademark', 'unauthorized_use'][Math.floor(Math.random() * 3)] as any,
          confidence: 80 + Math.random() * 20,
          detectedAt: new Date(),
          url: `https://platform.com/content/${Math.random().toString(36).substr(2, 9)}`,
          status: 'detected',
          fingerprint: `fp_${Math.random().toString(36).substr(2, 16)}`
        };
        
        setViolations(prev => [newViolation, ...prev].slice(0, 20)); // Keep only latest 20
        setStats(prev => ({
          ...prev,
          violationsFound: prev.violationsFound + 1,
          totalScans: prev.totalScans + 1
        }));
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getViolationTypeColor = (type: ViolationAlert['violationType']) => {
    switch (type) {
      case 'copyright': return 'bg-red-100 text-red-800';
      case 'trademark': return 'bg-orange-100 text-orange-800';
      case 'unauthorized_use': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: ViolationAlert['status']) => {
    switch (status) {
      case 'detected': return 'bg-red-100 text-red-800';
      case 'dmca_sent': return 'bg-yellow-100 text-yellow-800';
      case 'resolved': return 'bg-green-100 text-green-800';
      case 'disputed': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleTakeAction = (violationId: string, action: 'dmca' | 'dispute' | 'resolve') => {
    setViolations(prev => prev.map(v => {
      if (v.id === violationId) {
        let newStatus: ViolationAlert['status'];
        switch (action) {
          case 'dmca': newStatus = 'dmca_sent'; break;
          case 'dispute': newStatus = 'disputed'; break;
          case 'resolve': newStatus = 'resolved'; break;
          default: newStatus = v.status;
        }
        return { ...v, status: newStatus };
      }
      return v;
    }));

    if (action === 'resolve') {
      setStats(prev => ({ ...prev, resolvedCases: prev.resolvedCases + 1 }));
    }
  };

  const startManualScan = () => {
    setIsScanning(true);
    setStats(prev => ({ ...prev, totalScans: prev.totalScans + 1 }));
    
    setTimeout(() => {
      setIsScanning(false);
      // Simulate finding violations during manual scan
      const numNewViolations = Math.floor(Math.random() * 3) + 1;
      for (let i = 0; i < numNewViolations; i++) {
        const newViolation: ViolationAlert = {
          id: Math.random().toString(36).substr(2, 9),
          platform: ['YouTube', 'Instagram', 'TikTok', 'Facebook', 'Twitter'][Math.floor(Math.random() * 5)],
          contentTitle: `Scanned Content ${Math.floor(Math.random() * 1000)}`,
          violationType: ['copyright', 'trademark', 'unauthorized_use'][Math.floor(Math.random() * 3)] as any,
          confidence: 75 + Math.random() * 25,
          detectedAt: new Date(),
          url: `https://platform.com/scanned/${Math.random().toString(36).substr(2, 9)}`,
          status: 'detected',
          fingerprint: `fp_${Math.random().toString(36).substr(2, 16)}`
        };
        
        setViolations(prev => [newViolation, ...prev]);
        setStats(prev => ({ ...prev, violationsFound: prev.violationsFound + 1 }));
      }
    }, 3000);
  };

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Scans</p>
                <p className="text-2xl font-bold">{stats.totalScans}</p>
              </div>
              <Eye className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active Monitoring</p>
                <p className="text-2xl font-bold">{stats.activeMonitoring}</p>
              </div>
              <Shield className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Violations Found</p>
                <p className="text-2xl font-bold text-red-600">{stats.violationsFound}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Resolved Cases</p>
                <p className="text-2xl font-bold text-green-600">{stats.resolvedCases}</p>
              </div>
              <Shield className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Control Panel */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Eye className="w-5 h-5" />
              Real-time Monitoring
            </CardTitle>
            <Button 
              onClick={startManualScan}
              disabled={isScanning}
              className="ml-4"
            >
              {isScanning ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Scanning...
                </>
              ) : (
                'Start Manual Scan'
              )}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            Monitoring active across 50+ platforms
          </div>
        </CardContent>
      </Card>

      {/* Violations List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            Recent Violations
          </CardTitle>
        </CardHeader>
        <CardContent>
          {violations.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Shield className="w-12 h-12 mx-auto mb-4 text-green-500" />
              <p>No violations detected. Your content is protected!</p>
            </div>
          ) : (
            <div className="space-y-4">
              {violations.map((violation) => (
                <div key={violation.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-semibold">{violation.contentTitle}</h4>
                        <Badge className={getViolationTypeColor(violation.violationType)}>
                          {violation.violationType.replace('_', ' ')}
                        </Badge>
                        <Badge className={getStatusColor(violation.status)}>
                          {violation.status.replace('_', ' ')}
                        </Badge>
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <MapPin className="w-4 h-4" />
                          {violation.platform}
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          {violation.detectedAt.toLocaleString()}
                        </div>
                        <div>
                          Confidence: {violation.confidence.toFixed(1)}%
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2 ml-4">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => window.open(violation.url, '_blank')}
                      >
                        <ExternalLink className="w-4 h-4" />
                      </Button>
                      
                      {violation.status === 'detected' && (
                        <>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleTakeAction(violation.id, 'dmca')}
                          >
                            Send DMCA
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleTakeAction(violation.id, 'dispute')}
                          >
                            Dispute
                          </Button>
                        </>
                      )}
                      
                      {violation.status !== 'resolved' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleTakeAction(violation.id, 'resolve')}
                        >
                          Mark Resolved
                        </Button>
                      )}
                    </div>
                  </div>
                  
                  <div className="text-xs text-muted-foreground font-mono">
                    Fingerprint: {violation.fingerprint}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default MonitoringDashboard;