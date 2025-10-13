/*
 * Owner: Fahed Mlaiel
 * Contact: mlaiel@live.de
 * Notice: Attribution to Fahed Mlaiel is mandatory in all copies, forks, and derivatives.
 */

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { MapPin, Heart, Dog, Clock, User, CheckCircle, Warning } from '@phosphor-icons/react';
import { toast } from 'sonner';
import { CaseReport, Location } from '@/lib/types';
import { useTranslation } from '@/hooks/useTranslation';
import { formatTimeAgo, formatDistance, calculateDistance, useGeolocation } from '@/lib/geolocation';
import { useKV } from '@/hooks/useKV';
import { CaseDetailModal } from './CaseDetailModal';

interface CaseListProps {
  cases: CaseReport[];
  onCaseUpdate: (updatedCase: CaseReport) => void;
}

export function CaseList({ cases, onCaseUpdate }: CaseListProps) {
  const { t } = useTranslation();
  const [filter, setFilter] = useState<'all' | 'homeless' | 'animal'>('all');
  const [statusFilter, setStatusFilter] = useState<'all' | 'open' | 'in-progress' | 'helped'>('all');
  const [selectedCase, setSelectedCase] = useState<CaseReport | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [storedCases, setStoredCases] = useKV<CaseReport[]>('solidarity-cases', []);
  
  const { location } = useGeolocation();

  const openDetailModal = (caseItem: CaseReport) => {
    setSelectedCase(caseItem);
    setIsDetailModalOpen(true);
  };

  const closeDetailModal = () => {
    setIsDetailModalOpen(false);
    setSelectedCase(null);
  };

  const handleTakeAction = (caseId: string) => {
    const caseToUpdate = cases.find(c => c.id === caseId);
    if (caseToUpdate) {
      onCaseUpdate({
        ...caseToUpdate,
        status: 'in-progress',
        volunteerId: 'current-user-id',
      });
      toast.success('Action prise pour le cas');
      closeDetailModal();
    }
  };

  // Filter cases based on selected filters
  const filteredCases = cases.filter(case_ => {
    const typeMatch = filter === 'all' || case_.type === filter;
    const statusMatch = statusFilter === 'all' || case_.status === statusFilter;
    return typeMatch && statusMatch;
  });

  // Sort cases by urgency and time
  const sortedCases = [...filteredCases].sort((a, b) => {
    // First by urgency (high -> medium -> low)
    const urgencyOrder = { high: 3, medium: 2, low: 1 };
    const urgencyDiff = urgencyOrder[b.urgency] - urgencyOrder[a.urgency];
    if (urgencyDiff !== 0) return urgencyDiff;
    
    // Then by time (newest first)
    return new Date(b.reportedAt).getTime() - new Date(a.reportedAt).getTime();
  });

  const handleStatusUpdate = async (caseReport: CaseReport, newStatus: 'in-progress' | 'helped') => {
    const updatedCase: CaseReport = {
      ...caseReport,
      status: newStatus,
      resolvedAt: newStatus === 'helped' ? new Date().toISOString() : caseReport.resolvedAt,
      volunteerId: newStatus === 'helped' ? 'anonymous-volunteer' : caseReport.volunteerId
    };

    // Update in persistent storage
    setStoredCases((currentCases) => 
      (currentCases || []).map(c => c.id === caseReport.id ? updatedCase : c)
    );
    
    onCaseUpdate(updatedCase);
    setIsDialogOpen(false);
    
    toast.success(
      newStatus === 'helped' 
        ? t('cases.markedAsHelped')
        : t('cases.markedAsInProgress')
    );
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'high': return 'destructive';
      case 'medium': return 'default';
      case 'low': return 'secondary';
      default: return 'secondary';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'destructive';
      case 'in-progress': return 'default';
      case 'helped': return 'outline';
      default: return 'secondary';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'open': return Warning;
      case 'in-progress': return Clock;
      case 'helped': return CheckCircle;
      default: return Warning;
    }
  };

  const CaseCard = ({ case_: caseReport }: { case_: CaseReport }) => {
    const distance = location ? calculateDistance(location, caseReport.location) : null;
    const StatusIcon = getStatusIcon(caseReport.status);

    return (
      <Dialog open={isDialogOpen && selectedCase?.id === caseReport.id} onOpenChange={setIsDialogOpen}>
        <DialogTrigger asChild>
          <Card 
            className="cursor-pointer hover:shadow-md transition-all duration-200 border-l-4 active:scale-[0.98]"
            style={{
              borderLeftColor: caseReport.urgency === 'high' ? 'hsl(var(--destructive))' : 
                               caseReport.urgency === 'medium' ? 'hsl(var(--primary))' : 
                               'hsl(var(--muted-foreground))'
            }}
            onClick={() => {
              setSelectedCase(caseReport);
              setIsDetailModalOpen(true);
            }}
          >
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2 flex-1">
                  <div className="text-2xl">
                    {caseReport.type === 'homeless' ? '👤' : '�'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-sm leading-tight">
                      {caseReport.type === 'homeless' ? t('cases.personNeedsHelp') : t('cases.animalNeedsHelp')}
                    </h3>
                    <p className="text-xs text-muted-foreground line-clamp-2 mt-1">
                      {caseReport.description}
                    </p>
                  </div>
                </div>
                
                <div className="flex flex-col items-end gap-1 ml-2">
                  <Badge 
                    variant={getUrgencyColor(caseReport.urgency) as any} 
                    className="text-xs px-2 py-0.5 whitespace-nowrap"
                  >
                    {caseReport.urgency}
                  </Badge>
                  <Badge 
                    variant={getStatusColor(caseReport.status) as any} 
                    className="flex items-center gap-1 text-xs px-2 py-0.5"
                  >
                    <StatusIcon size={10} />
                    {caseReport.status === 'in-progress' ? 'helping' : caseReport.status}
                  </Badge>
                </div>
              </div>
              
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <div className="flex items-center gap-1">
                  <MapPin size={12} />
                  <span>{distance ? formatDistance(distance) : t('cases.unknown')}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock size={12} />
                  <span>{formatTimeAgo(caseReport.reportedAt)}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </DialogTrigger>

        {/* Mobile-Optimized Case Detail Dialog */}
        <DialogContent className="max-w-[95vw] w-full sm:max-w-md max-h-[90vh] overflow-y-auto">
          <DialogHeader className="text-left">
            <DialogTitle className="flex items-center gap-3 text-lg">
              <div className="text-2xl">
                {caseReport.type === 'homeless' ? '👤' : '�'}
              </div>
              <div>
                <div>{caseReport.type === 'homeless' ? t('cases.personNeedsHelp') : t('cases.animalNeedsHelp')}</div>
                <div className="text-sm font-normal text-muted-foreground">
                  {t('cases.reported')} {formatTimeAgo(caseReport.reportedAt)}
                </div>
              </div>
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            {/* Status and Urgency */}
            <div className="flex gap-2 flex-wrap">
              <Badge variant={getUrgencyColor(caseReport.urgency) as any} className="flex items-center gap-1">
                {caseReport.urgency === 'high' && '🔴'}
                {caseReport.urgency === 'medium' && '🟡'}
                {caseReport.urgency === 'low' && '🟢'}
                {caseReport.urgency} urgency
              </Badge>
              <Badge variant={getStatusColor(caseReport.status) as any} className="flex items-center gap-1">
                <StatusIcon size={12} />
                {caseReport.status.replace('-', ' ')}
              </Badge>
            </div>

            {/* Description */}
            <div className="bg-muted/50 p-4 rounded-lg">
              <h4 className="font-medium mb-2 text-sm">{t('cases.whatHappening')}</h4>
              <p className="text-sm leading-relaxed">
                {caseReport.description}
              </p>
            </div>

            {/* Location and Time Info */}
            <div className="grid grid-cols-1 gap-3 text-sm">
              <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                <div className="flex items-center gap-2">
                  <MapPin size={16} className="text-muted-foreground" />
                  <span className="font-medium">{t('cases.distance')}</span>
                </div>
                <span className="text-muted-foreground">
                  {distance ? formatDistance(distance) : t('cases.unknown')}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                <div className="flex items-center gap-2">
                  <Clock size={16} className="text-muted-foreground" />
                  <span className="font-medium">{t('cases.reported')}</span>
                </div>
                <span className="text-muted-foreground">
                  {formatTimeAgo(caseReport.reportedAt)}
                </span>
              </div>
            </div>

            {/* Action Buttons */}
            {caseReport.status === 'open' && (
              <div className="space-y-3 pt-2">
                <Button 
                  onClick={() => handleStatusUpdate(caseReport, 'in-progress')}
                  className="w-full h-12 text-base"
                  size="lg"
                >
                  <User className="mr-2" size={18} />
                  I'm going to help
                </Button>
                <Button 
                  onClick={() => handleStatusUpdate(caseReport, 'helped')}
                  className="w-full h-12 text-base"
                  variant="outline"
                  size="lg"
                >
                  <CheckCircle className="mr-2" size={18} />
                  Mark as already helped
                </Button>
              </div>
            )}

            {caseReport.status === 'in-progress' && (
              <div className="pt-2">
                <Button 
                  onClick={() => handleStatusUpdate(caseReport, 'helped')}
                  className="w-full h-12 text-base"
                  size="lg"
                >
                  <CheckCircle className="mr-2" size={18} />
                  Mark as helped
                </Button>
              </div>
            )}

            {caseReport.status === 'helped' && caseReport.resolvedAt && (
              <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                <div className="flex items-center gap-2 text-green-800 mb-1">
                  <CheckCircle className="text-green-600" size={18} />
                  <span className="font-medium">Help has been provided</span>
                </div>
                <p className="text-sm text-green-700">
                  Assistance completed {formatTimeAgo(caseReport.resolvedAt)}
                </p>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    );
  };

  return (
    <div className="space-y-4">
      {/* Mobile-Optimized Filters */}
      <div className="grid grid-cols-2 gap-3 sm:flex sm:gap-4">
        <div className="space-y-1">
          <label className="text-sm font-medium">Type</label>
          <Select value={filter} onValueChange={(value: 'all' | 'homeless' | 'animal') => setFilter(value)}>
            <SelectTrigger className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{t('cases.allCases')}</SelectItem>
              <SelectItem value="homeless">👤 {t('cases.people')}</SelectItem>
              <SelectItem value="animal">🐾 {t('cases.animals')}</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="space-y-1">
          <label className="text-sm font-medium">{t('cases.statusLabel')}</label>
          <Select value={statusFilter} onValueChange={(value: 'all' | 'open' | 'in-progress' | 'helped') => setStatusFilter(value)}>
            <SelectTrigger className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{t('cases.allStatus')}</SelectItem>
              <SelectItem value="open">🔴 {t('cases.status.open')}</SelectItem>
              <SelectItem value="in-progress">🟡 {t('cases.inProgress')}</SelectItem>
              <SelectItem value="helped">🟢 {t('cases.status.helped')}</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Summary Bar */}
      {sortedCases.length > 0 && (
        <div className="bg-muted/50 rounded-lg p-3 text-sm text-muted-foreground">
          {t('cases.showing')} {sortedCases.length} {sortedCases.length !== 1 ? t('cases.cases') : t('cases.case')} 
          {filter !== 'all' && ` • ${filter === 'homeless' ? t('cases.people') : t('cases.animals')} ${t('cases.only')}`}
          {statusFilter !== 'all' && ` • ${statusFilter.replace('-', ' ')} status`}
        </div>
      )}

      {/* Cases List - Mobile Optimized */}
      {sortedCases.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-8 px-4">
            <div className="text-4xl mb-3">
              {filter === 'homeless' ? '👤' : filter === 'animal' ? '🐾' : '💝'}
            </div>
            <h3 className="font-medium text-base mb-2 text-center">{t('cases.noCasesFound')}</h3>
            <p className="text-muted-foreground text-center text-sm max-w-sm">
              {filter === 'all' 
                ? t('cases.noResultsDesc')
                : `${t('cases.noResults')} ${filter === 'homeless' ? t('cases.people') : t('cases.animals')}`
              }
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {sortedCases.map((caseReport) => (
            <CaseCard key={caseReport.id} case_={caseReport} />
          ))}
        </div>
      )}

      {/* Modal de détails avec chat */}
      <CaseDetailModal
        case={selectedCase}
        isOpen={isDetailModalOpen}
        onClose={closeDetailModal}
        currentUserId="current-user-id"
        currentUserName="Utilisateur"
        onTakeAction={handleTakeAction}
      />
    </div>
  );
}