/**
 * Localization Context - Extended language and region context
 */

import { createContext, useContext, ReactNode, useState } from 'react';

interface LocalizationContextType {
  locale: string;
  currency: string;
  timezone: string;
  dateFormat: string;
  numberFormat: string;
  setLocale: (locale: string) => void;
  setCurrency: (currency: string) => void;
  setTimezone: (timezone: string) => void;
  formatCurrency: (amount: number) => string;
  formatDate: (date: Date) => string;
  formatNumber: (num: number) => string;
}

const LocalizationContext = createContext<LocalizationContextType | undefined>(undefined);

export function LocalizationProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState('en-US');
  const [currency, setCurrency] = useState('USD');
  const [timezone, setTimezone] = useState('UTC');
  const [dateFormat, setDateFormat] = useState('MM/dd/yyyy');
  const [numberFormat, setNumberFormat] = useState('en-US');

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency,
    }).format(amount);
  };

  const formatDate = (date: Date): string => {
    return new Intl.DateTimeFormat(locale).format(date);
  };

  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat(numberFormat).format(num);
  };

  return (
    <LocalizationContext.Provider value={{
      locale,
      currency,
      timezone,
      dateFormat,
      numberFormat,
      setLocale,
      setCurrency,
      setTimezone,
      formatCurrency,
      formatDate,
      formatNumber,
    }}>
      {children}
    </LocalizationContext.Provider>
  );
}

export const useLocalization = () => {
  const context = useContext(LocalizationContext);
  if (!context) {
    throw new Error('useLocalization must be used within a LocalizationProvider');
  }
  return context;
};
