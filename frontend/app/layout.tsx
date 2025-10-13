import './globals.css';
import { Inter } from 'next/font/google';
import { Providers } from './providers';
import { Toaster } from 'react-hot-toast';
import { QueryClientProvider } from '@/lib/query/config';
import { AuthProvider } from '@/lib/auth/provider';
import { WebSocketProvider } from '@/lib/websocket';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'IA Chérie - Enterprise AI Platform',
  description: 'Professional AI-powered content creation and management platform',
  keywords: 'AI, content creation, enterprise, professional, platform',
  authors: [{ name: 'IA Chérie Team' }],
};

export const viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <QueryClientProvider>
          <AuthProvider>
            <WebSocketProvider autoConnect={true} showConnectionStatus={true}>
              <Providers>
                <div className="min-h-screen bg-gray-50">
                  <main>
                    {children}
                  </main>
                  <Toaster position="top-right" />
                </div>
              </Providers>
            </WebSocketProvider>
          </AuthProvider>
        </QueryClientProvider>
      </body>
    </html>
  );
}