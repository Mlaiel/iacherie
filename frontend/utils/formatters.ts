/**
 * Utilitaires de formatage cohérents pour éviter les erreurs d'hydratation Next.js
 */

// Configuration des paramètres régionaux pour éviter les différences serveur/client
const LOCALE = 'en-US'; // Utilise toujours en-US pour la cohérence

export const formatNumber = (num: number, options?: Intl.NumberFormatOptions): string => {
  return new Intl.NumberFormat(LOCALE, options).format(num);
};

export const formatCurrency = (amount: number, currency: string = 'USD'): string => {
  return new Intl.NumberFormat(LOCALE, {
    style: 'currency',
    currency,
  }).format(amount);
};

export const formatCompactNumber = (num: number): string => {
  return new Intl.NumberFormat(LOCALE, {
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(num);
};

export const formatDate = (date: Date | string): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateObj.toLocaleDateString(LOCALE, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const formatDateTime = (date: Date | string): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateObj.toLocaleDateString(LOCALE, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

// Fonction pour remplacer .toLocaleString() avec paramètres cohérents
export const toConsistentLocaleString = (num: number): string => {
  return num.toLocaleString(LOCALE);
};