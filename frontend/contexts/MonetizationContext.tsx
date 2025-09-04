/**
 * Monetization Context - Revenue and monetization context
 */

import { createContext, useContext, ReactNode, useState } from 'react';

interface PaymentMethod {
  id: string;
  type: 'bank' | 'paypal' | 'crypto';
  name: string;
  isDefault: boolean;
}

interface Revenue {
  id: string;
  amount: number;
  currency: string;
  source: string;
  date: string;
  status: 'pending' | 'completed' | 'failed';
}

interface MonetizationContextType {
  paymentMethods: PaymentMethod[];
  revenue: Revenue[];
  totalEarnings: number;
  addPaymentMethod: (method: Omit<PaymentMethod, 'id'>) => void;
  removePaymentMethod: (id: string) => void;
  setDefaultPaymentMethod: (id: string) => void;
  withdrawEarnings: (amount: number, methodId: string) => Promise<boolean>;
}

const MonetizationContext = createContext<MonetizationContextType | undefined>(undefined);

export function MonetizationProvider({ children }: { children: ReactNode }) {
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([]);
  const [revenue, setRevenue] = useState<Revenue[]>([]);
  const [totalEarnings, setTotalEarnings] = useState(0);

  const addPaymentMethod = (method: Omit<PaymentMethod, 'id'>) => {
    const newMethod: PaymentMethod = {
      ...method,
      id: `payment_${Date.now()}`,
    };
    setPaymentMethods(prev => [...prev, newMethod]);
  };

  const removePaymentMethod = (id: string) => {
    setPaymentMethods(prev => prev.filter(method => method.id !== id));
  };

  const setDefaultPaymentMethod = (id: string) => {
    setPaymentMethods(prev => prev.map(method => ({
      ...method,
      isDefault: method.id === id,
    })));
  };

  const withdrawEarnings = async (amount: number, methodId: string): Promise<boolean> => {
    try {
      // Mock withdrawal process
      await new Promise(resolve => setTimeout(resolve, 1000));
      setTotalEarnings(prev => prev - amount);
      return true;
    } catch (error) {
      return false;
    }
  };

  return (
    <MonetizationContext.Provider value={{
      paymentMethods,
      revenue,
      totalEarnings,
      addPaymentMethod,
      removePaymentMethod,
      setDefaultPaymentMethod,
      withdrawEarnings,
    }}>
      {children}
    </MonetizationContext.Provider>
  );
}

export const useMonetization = () => {
  const context = useContext(MonetizationContext);
  if (!context) {
    throw new Error('useMonetization must be used within a MonetizationProvider');
  }
  return context;
};
