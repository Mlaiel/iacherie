/**
 * 🎯 HOOKS INDEX - EXPORT CONSOLIDÉ POUR 57 MODULES
 * @author Fahed Mlaiel - Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + DevOps
 */

// Re-export from presentation layer
export * from '../presentation/hooks';

// Export hooks existants
export * from './useAPI';
export * from './useContent';
export * from './useLiveAnalytics';
export * from './useNotifications';

// Export nouveaux hooks pour les 57 modules enterprise
export * from './useModules';
// Note: useDataServices, useFinancialServices et useInfrastructureServices 
// sont déjà exportés via useModules pour éviter les conflits