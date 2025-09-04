import './globals.css';
import { Providers } from './providers';
import { Toaster } from 'react-hot-toast';

export const metadata = {
  title: 'Ainflue - AI-Powered Content Protection & Monetization',
  description: 'Advanced content protection, fingerprinting, and monetization platform powered by AI',
  keywords: 'content protection, AI, fingerprinting, monetization, DMCA, copyright',
  authors: [{ name: 'Fahed Mlaiel' }],
  viewport: 'width=device-width, initial-scale=1',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full bg-gray-50 font-sans">
        <Providers>
          {children}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
        </Providers>
      </body>
    </html>
  );
}