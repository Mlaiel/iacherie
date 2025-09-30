/**
 * 🧪 Integration Test Template - Ainflue Creator Economy
 * 
 * @fileoverview Template enterprise pour tests d'intégration frontend
 * @version 1.0.0
 * @author Fahed Mlaiel <mlaiel@live.de>
 * 
 * ⚠️ PROPRIÉTÉ INTELLECTUELLE PROTÉGÉE
 * © 2025 Fahed Mlaiel - Tous droits réservés
 * Utilisation commerciale interdite sans autorisation écrite
 */

import { describe, it, expect, beforeEach, afterEach, beforeAll, afterAll } from '@jest/globals';
import { render, screen, fireEvent, waitFor, within, cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { setupServer } from 'msw/node';
import { rest } from 'msw';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter as Router } from 'react-router-dom';
import { ThemeProvider } from 'styled-components';
import React from 'react';

// Composants à tester
import { CreatorDashboard } from '../creator/creator_dashboard_template';
import { ContentUpload } from '../creator/content_upload_template';
import { MonetizationDashboard } from '../creator/monetization_dashboard_template';
import { CollaborationInterface } from '../creator/collaboration_interface_template';

// Utilitaires de test
import { mockUser, mockCreatorData, mockRevenueData } from './test_utils_template';
import { createTestTheme } from '../core/theme_provider';

// ============================================================================
// CONFIGURATION SERVEUR MOCK
// ============================================================================

const mockHandlers = [
  // API Utilisateur
  rest.get('/api/user/profile', (req, res, ctx) => {
    return res(ctx.json(mockUser));
  }),

  // API Créateur
  rest.get('/api/creator/:id/dashboard', (req, res, ctx) => {
    return res(ctx.json(mockCreatorData));
  }),

  // API Revenus
  rest.get('/api/creator/:id/revenue', (req, res, ctx) => {
    return res(ctx.json(mockRevenueData));
  }),

  // API Upload
  rest.post('/api/content/upload', (req, res, ctx) => {
    return res(ctx.json({ 
      success: true, 
      contentId: 'test-content-123',
      processingStatus: 'pending'
    }));
  }),

  // API Collaboration
  rest.get('/api/collaborations', (req, res, ctx) => {
    return res(ctx.json([
      {
        id: '1',
        title: 'Brand Partnership',
        status: 'active',
        participants: ['creator1', 'brand1']
      }
    ]));
  }),

  // API Analytics
  rest.get('/api/analytics/:creatorId', (req, res, ctx) => {
    return res(ctx.json({
      views: 50000,
      engagement: 4.2,
      revenue: 2500,
      subscribers: 15000
    }));
  })
];

const server = setupServer(...mockHandlers);

// ============================================================================
// WRAPPER DE TEST
// ============================================================================

interface TestWrapperProps {
  children: React.ReactNode;
  initialRoute?: string;
}

const TestWrapper: React.FC<TestWrapperProps> = ({ 
  children, 
  initialRoute = '/' 
}) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        staleTime: Infinity,
      },
    },
  });

  const theme = createTestTheme();

  // Mock du router avec route initiale
  window.history.pushState({}, 'Test page', initialRoute);

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <ThemeProvider theme={theme}>
          {children}
        </ThemeProvider>
      </Router>
    </QueryClientProvider>
  );
};

// ============================================================================
// HELPERS DE TEST
// ============================================================================

const renderWithProviders = (
  component: React.ReactElement,
  options: { initialRoute?: string } = {}
) => {
  const user = userEvent.setup();
  
  const result = render(
    <TestWrapper initialRoute={options.initialRoute}>
      {component}
    </TestWrapper>
  );

  return {
    ...result,
    user,
  };
};

const waitForLoadingToFinish = async () => {
  await waitFor(() => {
    expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
  });
};

// ============================================================================
// SETUP/TEARDOWN
// ============================================================================

beforeAll(() => {
  server.listen({ onUnhandledRequest: 'error' });
});

afterEach(() => {
  server.resetHandlers();
  cleanup();
});

afterAll(() => {
  server.close();
});

// ============================================================================
// TESTS D'INTÉGRATION
// ============================================================================

describe('🏠 Creator Dashboard Integration', () => {
  it('devrait charger et afficher le dashboard complet', async () => {
    const { user } = renderWithProviders(
      <CreatorDashboard creatorId="test-creator-123" />
    );

    // Vérifier le chargement initial
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    
    // Attendre la fin du chargement
    await waitForLoadingToFinish();

    // Vérifier les éléments du dashboard
    expect(screen.getByText(/creator dashboard/i)).toBeInTheDocument();
    expect(screen.getByText(/total views/i)).toBeInTheDocument();
    expect(screen.getByText(/revenue/i)).toBeInTheDocument();
    expect(screen.getByText(/subscribers/i)).toBeInTheDocument();

    // Vérifier les métriques
    expect(screen.getByText('50,000')).toBeInTheDocument(); // Views
    expect(screen.getByText('$2,500')).toBeInTheDocument(); // Revenue
  });

  it('devrait naviguer entre les différentes sections', async () => {
    const { user } = renderWithProviders(
      <CreatorDashboard creatorId="test-creator-123" />
    );

    await waitForLoadingToFinish();

    // Cliquer sur l'onglet Analytics
    const analyticsTab = screen.getByRole('button', { name: /analytics/i });
    await user.click(analyticsTab);

    // Vérifier que la section Analytics est affichée
    expect(screen.getByText(/engagement rate/i)).toBeInTheDocument();

    // Cliquer sur l'onglet Revenue
    const revenueTab = screen.getByRole('button', { name: /revenue/i });
    await user.click(revenueTab);

    // Vérifier que la section Revenue est affichée
    expect(screen.getByText(/monetization/i)).toBeInTheDocument();
  });
});

describe('📤 Content Upload Integration', () => {
  it('devrait gérer le processus d\'upload complet', async () => {
    const { user } = renderWithProviders(
      <ContentUpload onUploadComplete={jest.fn()} />
    );

    // Créer un fichier mock
    const file = new File(['video content'], 'test-video.mp4', {
      type: 'video/mp4'
    });

    // Simuler le drag & drop
    const dropzone = screen.getByTestId('upload-dropzone');
    
    // Mock de l'événement drop
    const dropEvent = new Event('drop', { bubbles: true });
    Object.defineProperty(dropEvent, 'dataTransfer', {
      value: {
        files: [file]
      }
    });

    fireEvent(dropzone, dropEvent);

    // Vérifier que le fichier est ajouté
    await waitFor(() => {
      expect(screen.getByText('test-video.mp4')).toBeInTheDocument();
    });

    // Remplir les métadonnées
    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, 'Mon Super Contenu');

    const descriptionInput = screen.getByLabelText(/description/i);
    await user.type(descriptionInput, 'Description de mon contenu');

    // Sélectionner les tags
    const tagInput = screen.getByLabelText(/tags/i);
    await user.type(tagInput, 'gaming, entertainment{enter}');

    // Démarrer l'upload
    const uploadButton = screen.getByRole('button', { name: /upload/i });
    await user.click(uploadButton);

    // Vérifier la progression
    expect(screen.getByText(/uploading/i)).toBeInTheDocument();
    
    // Attendre la fin de l'upload
    await waitFor(() => {
      expect(screen.getByText(/upload successful/i)).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  it('devrait gérer les erreurs d\'upload', async () => {
    // Mock d'une erreur d'upload
    server.use(
      rest.post('/api/content/upload', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ 
          error: 'Upload failed' 
        }));
      })
    );

    const { user } = renderWithProviders(
      <ContentUpload onUploadComplete={jest.fn()} />
    );

    const file = new File(['video content'], 'test-video.mp4', {
      type: 'video/mp4'
    });

    const fileInput = screen.getByLabelText(/choose file/i);
    await user.upload(fileInput, file);

    const uploadButton = screen.getByRole('button', { name: /upload/i });
    await user.click(uploadButton);

    // Vérifier le message d'erreur
    await waitFor(() => {
      expect(screen.getByText(/upload failed/i)).toBeInTheDocument();
    });
  });
});

describe('💰 Monetization Dashboard Integration', () => {
  it('devrait afficher les métriques de revenus', async () => {
    const { user } = renderWithProviders(
      <MonetizationDashboard 
        creatorId="test-creator-123"
        timeRange="30d"
        currency="USD"
        onTimeRangeChange={jest.fn()}
        onExportData={jest.fn()}
      />
    );

    await waitForLoadingToFinish();

    // Vérifier les métriques principales
    expect(screen.getByText(/total revenue/i)).toBeInTheDocument();
    expect(screen.getByText(/active streams/i)).toBeInTheDocument();
    expect(screen.getByText(/conversion rate/i)).toBeInTheDocument();

    // Vérifier les graphiques
    expect(screen.getByText(/revenue trend/i)).toBeInTheDocument();
    expect(screen.getByText(/revenue breakdown/i)).toBeInTheDocument();
  });

  it('devrait permettre de changer la période', async () => {
    const onTimeRangeChange = jest.fn();
    
    const { user } = renderWithProviders(
      <MonetizationDashboard 
        creatorId="test-creator-123"
        timeRange="30d"
        currency="USD"
        onTimeRangeChange={onTimeRangeChange}
        onExportData={jest.fn()}
      />
    );

    await waitForLoadingToFinish();

    // Changer la période
    const timeRangeSelect = screen.getByRole('combobox');
    await user.selectOptions(timeRangeSelect, '7d');

    expect(onTimeRangeChange).toHaveBeenCalledWith('7d');
  });

  it('devrait permettre d\'exporter les données', async () => {
    const onExportData = jest.fn();
    
    const { user } = renderWithProviders(
      <MonetizationDashboard 
        creatorId="test-creator-123"
        timeRange="30d"
        currency="USD"
        onTimeRangeChange={jest.fn()}
        onExportData={onExportData}
      />
    );

    await waitForLoadingToFinish();

    // Cliquer sur Export
    const exportButton = screen.getByRole('button', { name: /export/i });
    await user.click(exportButton);

    expect(onExportData).toHaveBeenCalled();
  });
});

describe('🤝 Collaboration Interface Integration', () => {
  it('devrait charger et afficher les collaborations', async () => {
    const { user } = renderWithProviders(
      <CollaborationInterface creatorId="test-creator-123" />
    );

    await waitForLoadingToFinish();

    // Vérifier l'affichage des collaborations
    expect(screen.getByText(/brand partnership/i)).toBeInTheDocument();
    expect(screen.getByText(/active/i)).toBeInTheDocument();
  });

  it('devrait permettre de créer une nouvelle collaboration', async () => {
    const { user } = renderWithProviders(
      <CollaborationInterface creatorId="test-creator-123" />
    );

    await waitForLoadingToFinish();

    // Cliquer sur "Nouvelle Collaboration"
    const newCollabButton = screen.getByRole('button', { 
      name: /new collaboration/i 
    });
    await user.click(newCollabButton);

    // Vérifier l'ouverture du modal
    expect(screen.getByText(/create collaboration/i)).toBeInTheDocument();

    // Remplir le formulaire
    const titleInput = screen.getByLabelText(/collaboration title/i);
    await user.type(titleInput, 'New Brand Partnership');

    const descriptionInput = screen.getByLabelText(/description/i);
    await user.type(descriptionInput, 'Partnership description');

    // Soumettre
    const submitButton = screen.getByRole('button', { name: /create/i });
    await user.click(submitButton);

    // Vérifier la création
    await waitFor(() => {
      expect(screen.getByText(/collaboration created/i)).toBeInTheDocument();
    });
  });
});

describe('🔄 Flux d\'intégration complet', () => {
  it('devrait gérer le flux créateur complet', async () => {
    const { user } = renderWithProviders(
      <CreatorDashboard creatorId="test-creator-123" />,
      { initialRoute: '/creator/dashboard' }
    );

    // 1. Vérifier le chargement du dashboard
    await waitForLoadingToFinish();
    expect(screen.getByText(/creator dashboard/i)).toBeInTheDocument();

    // 2. Naviguer vers l'upload
    const uploadLink = screen.getByRole('link', { name: /upload content/i });
    await user.click(uploadLink);

    // 3. Uploader du contenu
    expect(screen.getByText(/upload content/i)).toBeInTheDocument();
    
    // 4. Naviguer vers la monétisation
    const monetizationLink = screen.getByRole('link', { 
      name: /monetization/i 
    });
    await user.click(monetizationLink);

    // 5. Vérifier les revenus
    expect(screen.getByText(/total revenue/i)).toBeInTheDocument();

    // 6. Naviguer vers les collaborations
    const collaborationLink = screen.getByRole('link', { 
      name: /collaborations/i 
    });
    await user.click(collaborationLink);

    // 7. Vérifier les collaborations
    expect(screen.getByText(/brand partnership/i)).toBeInTheDocument();
  });
});

describe('🧪 Tests de performance et accessibilité', () => {
  it('devrait respecter les standards d\'accessibilité', async () => {
    const { container } = renderWithProviders(
      <CreatorDashboard creatorId="test-creator-123" />
    );

    await waitForLoadingToFinish();

    // Vérifier les attributs d'accessibilité
    const headings = screen.getAllByRole('heading');
    expect(headings.length).toBeGreaterThan(0);

    // Vérifier la navigation au clavier
    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      expect(button).not.toHaveAttribute('tabindex', '-1');
    });

    // Vérifier les alt texts pour les images
    const images = container.querySelectorAll('img');
    images.forEach(img => {
      expect(img).toHaveAttribute('alt');
    });
  });

  it('devrait gérer les états de chargement', async () => {
    const { user } = renderWithProviders(
      <CreatorDashboard creatorId="test-creator-123" />
    );

    // Vérifier l'état de chargement initial
    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    // Attendre le chargement
    await waitForLoadingToFinish();

    // Vérifier que le contenu est affiché
    expect(screen.getByText(/creator dashboard/i)).toBeInTheDocument();
  });

  it('devrait gérer les erreurs réseau', async () => {
    // Mock d'erreur réseau
    server.use(
      rest.get('/api/creator/:id/dashboard', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    const { user } = renderWithProviders(
      <CreatorDashboard creatorId="test-creator-123" />
    );

    // Attendre l'affichage de l'erreur
    await waitFor(() => {
      expect(screen.getByText(/error loading/i)).toBeInTheDocument();
    });

    // Vérifier le bouton de retry
    const retryButton = screen.getByRole('button', { name: /retry/i });
    expect(retryButton).toBeInTheDocument();
  });
});

describe('📱 Tests responsive', () => {
  beforeEach(() => {
    // Mock des media queries
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: jest.fn().mockImplementation(query => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      })),
    });
  });

  it('devrait s\'adapter aux écrans mobiles', async () => {
    // Simuler un écran mobile
    global.innerWidth = 375;
    global.innerHeight = 667;
    global.dispatchEvent(new Event('resize'));

    const { user } = renderWithProviders(
      <CreatorDashboard creatorId="test-creator-123" />
    );

    await waitForLoadingToFinish();

    // Vérifier l'adaptation mobile
    const dashboard = screen.getByTestId('creator-dashboard');
    expect(dashboard).toHaveClass('mobile-layout');
  });

  it('devrait s\'adapter aux écrans desktop', async () => {
    // Simuler un écran desktop
    global.innerWidth = 1920;
    global.innerHeight = 1080;
    global.dispatchEvent(new Event('resize'));

    const { user } = renderWithProviders(
      <CreatorDashboard creatorId="test-creator-123" />
    );

    await waitForLoadingToFinish();

    // Vérifier l'adaptation desktop
    const dashboard = screen.getByTestId('creator-dashboard');
    expect(dashboard).toHaveClass('desktop-layout');
  });
});

// ============================================================================
// TESTS DE PERFORMANCE
// ============================================================================

describe('⚡ Tests de performance', () => {
  it('devrait charger rapidement', async () => {
    const startTime = performance.now();
    
    renderWithProviders(
      <CreatorDashboard creatorId="test-creator-123" />
    );

    await waitForLoadingToFinish();
    
    const endTime = performance.now();
    const loadTime = endTime - startTime;

    // Le chargement ne devrait pas dépasser 3 secondes
    expect(loadTime).toBeLessThan(3000);
  });

  it('devrait optimiser les re-renders', async () => {
    let renderCount = 0;
    
    const TestComponent = () => {
      renderCount++;
      return <CreatorDashboard creatorId="test-creator-123" />;
    };

    const { rerender } = renderWithProviders(<TestComponent />);
    
    await waitForLoadingToFinish();
    
    const initialRenderCount = renderCount;
    
    // Re-render avec les mêmes props
    rerender(<TestComponent />);
    
    // Ne devrait pas causer de re-render inutile
    expect(renderCount).toBe(initialRenderCount);
  });
});

// ============================================================================
// EXPORT
// ============================================================================

export {};

/**
 * 🧪 TESTS D'INTÉGRATION COMPLETS
 * 
 * ✅ Fonctionnalités testées:
 * - Dashboard créateur complet
 * - Upload de contenu avec métadonnées
 * - Dashboard de monétisation
 * - Interface de collaboration
 * - Navigation entre sections
 * - Gestion des erreurs
 * - États de chargement
 * - Responsive design
 * - Accessibilité WCAG
 * - Performance optimization
 * 
 * 🔧 Technologies utilisées:
 * - Jest + React Testing Library
 * - MSW pour mock API
 * - User events simulation
 * - Performance monitoring
 * - A11y testing
 * 
 * 📊 Métriques couvertes:
 * - Flux utilisateur complets
 * - Intégrations API
 * - États d'interface
 * - Validation formulaires
 * - Navigation routing
 * - Error handling
 */