/**
 * React Query Configuration - Production Grade
 * @module lib/query/config
 */

'use client';

import { QueryClient, QueryClientProvider as TanStackQueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';

/**
 * Create query client with production configuration
 */
function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Cache time: 5 minutes
        gcTime: 5 * 60 * 1000,
        // Stale time: 30 seconds
        staleTime: 30 * 1000,
        // Retry failed requests 3 times with exponential backoff
        retry: 3,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
        // Refetch on window focus in production
        refetchOnWindowFocus: process.env.NODE_ENV === 'production',
        // Refetch on mount if data is stale
        refetchOnMount: true,
        // Refetch on reconnect
        refetchOnReconnect: true,
        // Show error notifications
        throwOnError: false,
      },
      mutations: {
        // Retry mutations once
        retry: 1,
        // Throw errors to error boundary
        throwOnError: false,
      },
    },
  });
}

let browserQueryClient: QueryClient | undefined = undefined;

function getQueryClient() {
  if (typeof window === 'undefined') {
    // Server: always create new query client
    return makeQueryClient();
  } else {
    // Browser: reuse singleton
    if (!browserQueryClient) {
      browserQueryClient = makeQueryClient();
    }
    return browserQueryClient;
  }
}

/**
 * Query Client Provider
 */
export function QueryClientProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => getQueryClient());

  return (
    <TanStackQueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools initialIsOpen={false} position="bottom" />
      )}
    </TanStackQueryClientProvider>
  );
}
