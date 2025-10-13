import { createRoot } from 'react-dom/client'
import { ErrorBoundary } from "react-error-boundary";
import { Toaster } from '@/components/ui/sonner'

import App from './App.tsx'
import { ErrorFallback } from './ErrorFallback.tsx'

import "./app.css"

createRoot(document.getElementById('root')!).render(
  <ErrorBoundary FallbackComponent={ErrorFallback}>
    <App />
    <Toaster />
   </ErrorBoundary>
)
