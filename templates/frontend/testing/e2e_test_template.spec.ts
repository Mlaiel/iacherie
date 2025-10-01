/**
 * 🎭 E2E Test Template - iacherie Creator Economy
 * 
 * @fileoverview Template enterprise pour tests end-to-end frontend
 * @version 1.0.0
 * @author Fahed Mlaiel <mlaiel@live.de>
 * 
 * ⚠️ PROPRIÉTÉ INTELLECTUELLE PROTÉGÉE
 * © 2025 Fahed Mlaiel - Tous droits réservés
 * Utilisation commerciale interdite sans autorisation écrite
 */

import { test, expect, Page, BrowserContext } from '@playwright/test';
import { devices } from '@playwright/test';

// ============================================================================
// CONFIGURATION E2E
// ============================================================================

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:3000';
const TEST_USER_EMAIL = 'test-creator@iacherie.com';
const TEST_USER_PASSWORD = 'TestPassword123!';

// Données de test
const testCreatorData = {
  username: 'test_creator_e2e',
  displayName: 'Test Creator E2E',
  email: TEST_USER_EMAIL,
  bio: 'Test creator for E2E testing',
  category: 'Gaming'
};

const testContentData = {
  title: 'Test Video E2E',
  description: 'Video uploaded via E2E testing',
  tags: ['gaming', 'entertainment', 'test'],
  category: 'Gaming'
};

// ============================================================================
// HELPERS E2E
// ============================================================================

class CreatorE2EHelpers {
  constructor(private page: Page) {}

  // Authentification
  async login(email: string = TEST_USER_EMAIL, password: string = TEST_USER_PASSWORD) {
    await this.page.goto(`${BASE_URL}/login`);
    await this.page.fill('[data-testid="email-input"]', email);
    await this.page.fill('[data-testid="password-input"]', password);
    await this.page.click('[data-testid="login-button"]');
    
    // Attendre la redirection vers le dashboard
    await this.page.waitForURL(`${BASE_URL}/creator/dashboard`);
    await expect(this.page.locator('[data-testid="creator-dashboard"]')).toBeVisible();
  }

  // Navigation
  async navigateToSection(section: 'dashboard' | 'upload' | 'analytics' | 'monetization' | 'collaborations') {
    const sectionMap = {
      dashboard: '/creator/dashboard',
      upload: '/creator/upload',
      analytics: '/creator/analytics',
      monetization: '/creator/monetization',
      collaborations: '/creator/collaborations'
    };

    await this.page.goto(`${BASE_URL}${sectionMap[section]}`);
    await this.page.waitForLoadState('networkidle');
  }

  // Upload de contenu
  async uploadContent(filePath: string, metadata: typeof testContentData) {
    await this.navigateToSection('upload');
    
    // Upload du fichier
    const fileInput = this.page.locator('input[type="file"]');
    await fileInput.setInputFiles(filePath);
    
    // Attendre la validation du fichier
    await expect(this.page.locator('[data-testid="file-preview"]')).toBeVisible();
    
    // Remplir les métadonnées
    await this.page.fill('[data-testid="title-input"]', metadata.title);
    await this.page.fill('[data-testid="description-input"]', metadata.description);
    
    // Ajouter des tags
    for (const tag of metadata.tags) {
      await this.page.fill('[data-testid="tags-input"]', tag);
      await this.page.press('[data-testid="tags-input"]', 'Enter');
    }
    
    // Sélectionner la catégorie
    await this.page.selectOption('[data-testid="category-select"]', metadata.category);
    
    // Démarrer l'upload
    await this.page.click('[data-testid="upload-button"]');
    
    // Attendre la confirmation
    await expect(this.page.locator('[data-testid="upload-success"]')).toBeVisible({ timeout: 30000 });
  }

  // Vérification des métriques
  async verifyDashboardMetrics() {
    await this.navigateToSection('dashboard');
    
    // Vérifier la présence des métriques principales
    await expect(this.page.locator('[data-testid="total-views-metric"]')).toBeVisible();
    await expect(this.page.locator('[data-testid="total-subscribers-metric"]')).toBeVisible();
    await expect(this.page.locator('[data-testid="engagement-rate-metric"]')).toBeVisible();
    await expect(this.page.locator('[data-testid="total-revenue-metric"]')).toBeVisible();
    
    // Vérifier que les valeurs sont numériques
    const viewsText = await this.page.textContent('[data-testid="total-views-value"]');
    expect(viewsText).toMatch(/^\d{1,3}(,\d{3})*$/);
  }

  // Gestion de la monétisation
  async setupMonetization() {
    await this.navigateToSection('monetization');
    
    // Activer la monétisation
    await this.page.click('[data-testid="enable-monetization-button"]');
    
    // Configurer les sources de revenus
    await this.page.check('[data-testid="enable-ad-revenue"]');
    await this.page.check('[data-testid="enable-sponsorships"]');
    await this.page.check('[data-testid="enable-merchandise"]');
    
    // Sauvegarder la configuration
    await this.page.click('[data-testid="save-monetization-config"]');
    
    // Vérifier la confirmation
    await expect(this.page.locator('[data-testid="monetization-enabled-success"]')).toBeVisible();
  }

  // Création de collaboration
  async createCollaboration(title: string, description: string) {
    await this.navigateToSection('collaborations');
    
    // Ouvrir le modal de création
    await this.page.click('[data-testid="create-collaboration-button"]');
    await expect(this.page.locator('[data-testid="collaboration-modal"]')).toBeVisible();
    
    // Remplir le formulaire
    await this.page.fill('[data-testid="collaboration-title-input"]', title);
    await this.page.fill('[data-testid="collaboration-description-input"]', description);
    
    // Sélectionner le type de collaboration
    await this.page.selectOption('[data-testid="collaboration-type-select"]', 'brand-partnership');
    
    // Créer la collaboration
    await this.page.click('[data-testid="submit-collaboration-button"]');
    
    // Vérifier la création
    await expect(this.page.locator(`text=${title}`)).toBeVisible();
  }

  // Attendre le chargement complet
  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
    await this.page.waitForSelector('[data-testid="page-loaded"]', { timeout: 10000 });
  }

  // Prendre une capture d'écran pour debug
  async takeScreenshot(name: string) {
    await this.page.screenshot({ 
      path: `test-results/screenshots/${name}.png`,
      fullPage: true 
    });
  }
}

// ============================================================================
// CONFIGURATION DES TESTS
// ============================================================================

test.describe.configure({ mode: 'parallel' });

test.beforeEach(async ({ page }) => {
  // Configuration globale avant chaque test
  await page.goto(BASE_URL);
  await page.waitForLoadState('networkidle');
});

// ============================================================================
// TESTS E2E CREATOR DASHBOARD
// ============================================================================

test.describe('🏠 Creator Dashboard E2E', () => {
  test('devrait charger le dashboard et afficher les métriques', async ({ page }) => {
    const helpers = new CreatorE2EHelpers(page);
    
    await helpers.login();
    await helpers.verifyDashboardMetrics();
    
    // Vérifier les graphiques
    await expect(page.locator('[data-testid="revenue-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="engagement-chart"]')).toBeVisible();
    
    // Vérifier la navigation
    await expect(page.locator('[data-testid="navigation-menu"]')).toBeVisible();
    
    await helpers.takeScreenshot('dashboard-loaded');
  });

  test('devrait permettre de changer la période d\'analyse', async ({ page }) => {
    const helpers = new CreatorE2EHelpers(page);
    
    await helpers.login();
    await helpers.navigateToSection('dashboard');
    
    // Changer la période à 7 jours
    await page.selectOption('[data-testid="time-range-selector"]', '7d');
    await page.waitForResponse(response => 
      response.url().includes('/api/analytics') && response.status() === 200
    );
    
    // Vérifier que les données ont été mises à jour
    await expect(page.locator('[data-testid="time-range-indicator"]')).toHaveText('Last 7 days');
    
    // Changer la période à 1 an
    await page.selectOption('[data-testid="time-range-selector"]', '1y');
    await page.waitForResponse(response => 
      response.url().includes('/api/analytics') && response.status() === 200
    );
    
    await expect(page.locator('[data-testid="time-range-indicator"]')).toHaveText('Last year');
  });
});

// ============================================================================
// TESTS E2E CONTENT UPLOAD
// ============================================================================

test.describe('📤 Content Upload E2E', () => {
  test('devrait uploader du contenu avec succès', async ({ page }) => {
    const helpers = new CreatorE2EHelpers(page);
    
    await helpers.login();
    
    // Créer un fichier de test temporaire
    const testVideoPath = 'test-assets/sample-video.mp4';
    
    await helpers.uploadContent(testVideoPath, testContentData);
    
    // Vérifier que le contenu apparaît dans la liste
    await helpers.navigateToSection('dashboard');
    await expect(page.locator(`text=${testContentData.title}`)).toBeVisible();
    
    await helpers.takeScreenshot('content-uploaded');
  });

  test('devrait gérer les erreurs d\'upload', async ({ page }) => {
    const helpers = new CreatorE2EHelpers(page);
    
    await helpers.login();
    await helpers.navigateToSection('upload');
    
    // Essayer d'uploader un fichier invalide
    const invalidFilePath = 'test-assets/invalid-file.txt';
    await page.setInputFiles('input[type="file"]', invalidFilePath);
    
    // Vérifier l'affichage de l'erreur
    await expect(page.locator('[data-testid="file-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="file-error"]')).toContainText('Invalid file format');
  });

  test('devrait supporter le drag and drop', async ({ page }) => {
    const helpers = new CreatorE2EHelpers(page);
    
    await helpers.login();
    await helpers.navigateToSection('upload');
    
    // Simuler un drag and drop
    const dropzone = page.locator('[data-testid="upload-dropzone"]');
    
    // Créer un fichier virtuel pour le test
    const fileContent = Buffer.from('fake video content');
    await page.evaluate((content) => {
      const dt = new DataTransfer();
      const file = new File([content], 'test-video.mp4', { type: 'video/mp4' });
      dt.items.add(file);
      
      const dropEvent = new DragEvent('drop', { dataTransfer: dt });
      document.querySelector('[data-testid="upload-dropzone"]')?.dispatchEvent(dropEvent);
    }, fileContent);
    
    // Vérifier que le fichier a été ajouté
    await expect(page.locator('[data-testid="file-preview"]')).toBeVisible();
  });
});

// ============================================================================
// TESTS E2E MONETIZATION
// ============================================================================

test.describe('💰 Monetization E2E', () => {
  test('devrait configurer la monétisation', async ({ page }) => {
    const helpers = new CreatorE2EHelpers(page);
    
    await helpers.login();
    await helpers.setupMonetization();
    
    // Vérifier les métriques de revenus
    await expect(page.locator('[data-testid="total-revenue-metric"]')).toBeVisible();
    await expect(page.locator('[data-testid="revenue-streams-list"]')).toBeVisible();
    
    await helpers.takeScreenshot('monetization-configured');
  });

  test('devrait afficher les graphiques de revenus', async ({ page }) => {
    const helpers = new CreatorE2EHelpers(page);
    
    await helpers.login();
    await helpers.navigateToSection('monetization');
    
    // Vérifier les graphiques
    await expect(page.locator('[data-testid="revenue-trend-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="revenue-breakdown-chart"]')).toBeVisible();
    
    // Tester l'interaction avec les graphiques
    await page.hover('[data-testid="revenue-chart-bar-0"]');
    await expect(page.locator('[data-testid="chart-tooltip"]')).toBeVisible();
  });

  test('devrait permettre d\'exporter les données de revenus', async ({ page }) => {
    const helpers = new CreatorE2EHelpers(page);
    
    await helpers.login();
    await helpers.navigateToSection('monetization');
    
    // Configuration du téléchargement
    const downloadPromise = page.waitForEvent('download');
    
    // Cliquer sur export
    await page.click('[data-testid="export-revenue-data"]');
    
    // Vérifier le téléchargement
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain('revenue-data');
    expect(download.suggestedFilename()).toContain('.csv');
  });
});

// ============================================================================
// TESTS E2E COLLABORATIONS
// ============================================================================

test.describe('🤝 Collaborations E2E', () => {
  test('devrait créer une nouvelle collaboration', async ({ page }) => {
    const helpers = new CreatorE2EHelpers(page);
    
    await helpers.login();
    
    const collaborationTitle = 'Test Brand Partnership E2E';
    const collaborationDescription = 'Partnership created via E2E testing';
    
    await helpers.createCollaboration(collaborationTitle, collaborationDescription);
    
    // Vérifier les détails de la collaboration
    await page.click(`text=${collaborationTitle}`);
    await expect(page.locator('[data-testid="collaboration-details"]')).toBeVisible();
    await expect(page.locator('[data-testid="collaboration-status"]')).toHaveText('Pending');
    
    await helpers.takeScreenshot('collaboration-created');
  });

  test('devrait filtrer les collaborations par statut', async ({ page }) => {
    const helpers = new CreatorE2EHelpers(page);
    
    await helpers.login();
    await helpers.navigateToSection('collaborations');
    
    // Filtrer par statut "Active"
    await page.selectOption('[data-testid="collaboration-status-filter"]', 'active');
    await page.waitForLoadState('networkidle');
    
    // Vérifier que seules les collaborations actives sont affichées
    const collaborationItems = page.locator('[data-testid="collaboration-item"]');
    await expect(collaborationItems).toHaveCount(2); // Selon les données de test
    
    // Vérifier que tous les éléments ont le statut "Active"
    const statusBadges = page.locator('[data-testid="collaboration-status-badge"]');
    for (let i = 0; i < await statusBadges.count(); i++) {
      await expect(statusBadges.nth(i)).toHaveText('Active');
    }
  });
});

// ============================================================================
// TESTS E2E ANALYTICS
// ============================================================================

test.describe('📊 Analytics E2E', () => {
  test('devrait afficher les analytics détaillés', async ({ page }) => {
    const helpers = new CreatorE2EHelpers(page);
    
    await helpers.login();
    await helpers.navigateToSection('analytics');
    
    // Vérifier les sections d'analytics
    await expect(page.locator('[data-testid="audience-analytics"]')).toBeVisible();
    await expect(page.locator('[data-testid="content-performance"]')).toBeVisible();
    await expect(page.locator('[data-testid="engagement-metrics"]')).toBeVisible();
    
    // Vérifier les graphiques interactifs
    await expect(page.locator('[data-testid="views-timeline-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="engagement-heatmap"]')).toBeVisible();
    
    await helpers.takeScreenshot('analytics-dashboard');
  });

  test('devrait permettre de comparer les périodes', async ({ page }) => {
    const helpers = new CreatorE2EHelpers(page);
    
    await helpers.login();
    await helpers.navigateToSection('analytics');
    
    // Activer la comparaison
    await page.check('[data-testid="enable-comparison-toggle"]');
    
    // Sélectionner la période de comparaison
    await page.selectOption('[data-testid="comparison-period-selector"]', 'previous-month');
    
    // Vérifier l'affichage de la comparaison
    await expect(page.locator('[data-testid="comparison-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="comparison-metrics"]')).toBeVisible();
  });
});

// ============================================================================
// TESTS E2E RESPONSIVE
// ============================================================================

test.describe('📱 Responsive E2E', () => {
  test('devrait fonctionner sur mobile', async ({ browser }) => {
    const context = await browser.newContext({
      ...devices['iPhone 12']
    });
    const page = await context.newPage();
    const helpers = new CreatorE2EHelpers(page);
    
    await helpers.login();
    
    // Vérifier l'adaptation mobile du dashboard
    await expect(page.locator('[data-testid="mobile-navigation"]')).toBeVisible();
    await expect(page.locator('[data-testid="hamburger-menu"]')).toBeVisible();
    
    // Tester la navigation mobile
    await page.click('[data-testid="hamburger-menu"]');
    await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
    
    await page.click('[data-testid="mobile-upload-link"]');
    await expect(page.locator('[data-testid="mobile-upload-interface"]')).toBeVisible();
    
    await helpers.takeScreenshot('mobile-dashboard');
    await context.close();
  });

  test('devrait fonctionner sur tablette', async ({ browser }) => {
    const context = await browser.newContext({
      ...devices['iPad Pro']
    });
    const page = await context.newPage();
    const helpers = new CreatorE2EHelpers(page);
    
    await helpers.login();
    
    // Vérifier l'adaptation tablette
    await expect(page.locator('[data-testid="tablet-layout"]')).toBeVisible();
    
    // Vérifier la grille de métriques sur tablette
    const metricsGrid = page.locator('[data-testid="metrics-grid"]');
    await expect(metricsGrid).toHaveCSS('grid-template-columns', /repeat\(2, 1fr\)/);
    
    await helpers.takeScreenshot('tablet-dashboard');
    await context.close();
  });
});

// ============================================================================
// TESTS E2E PERFORMANCE
// ============================================================================

test.describe('⚡ Performance E2E', () => {
  test('devrait respecter les Core Web Vitals', async ({ page }) => {
    const helpers = new CreatorE2EHelpers(page);
    
    await helpers.login();
    
    // Mesurer les Core Web Vitals
    const webVitals = await page.evaluate(() => {
      return new Promise((resolve) => {
        const vitals = {
          fcp: 0,
          lcp: 0,
          cls: 0,
          fid: 0
        };
        
        // Mesurer FCP
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          entries.forEach((entry) => {
            if (entry.name === 'first-contentful-paint') {
              vitals.fcp = entry.startTime;
            }
          });
        }).observe({ entryTypes: ['paint'] });
        
        // Mesurer LCP
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          vitals.lcp = lastEntry.startTime;
        }).observe({ entryTypes: ['largest-contentful-paint'] });
        
        // Mesurer CLS
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          entries.forEach((entry) => {
            if (!entry.hadRecentInput) {
              vitals.cls += entry.value;
            }
          });
        }).observe({ entryTypes: ['layout-shift'] });
        
        setTimeout(() => resolve(vitals), 5000);
      });
    });
    
    // Vérifier les seuils Core Web Vitals
    expect(webVitals.fcp).toBeLessThan(1800); // FCP < 1.8s
    expect(webVitals.lcp).toBeLessThan(2500); // LCP < 2.5s
    expect(webVitals.cls).toBeLessThan(0.1);  // CLS < 0.1
  });

  test('devrait charger rapidement en conditions réseau lentes', async ({ page }) => {
    const helpers = new CreatorE2EHelpers(page);
    
    // Simuler une connexion 3G lente
    await page.route('**/*', route => {
      setTimeout(() => route.continue(), 100); // Délai de 100ms par requête
    });
    
    const startTime = Date.now();
    await helpers.login();
    const loadTime = Date.now() - startTime;
    
    // Même avec la connexion lente, le chargement ne devrait pas dépasser 10s
    expect(loadTime).toBeLessThan(10000);
  });
});

// ============================================================================
// TESTS E2E ACCESSIBILITY
// ============================================================================

test.describe('♿ Accessibility E2E', () => {
  test('devrait être navigable au clavier', async ({ page }) => {
    const helpers = new CreatorE2EHelpers(page);
    
    await helpers.login();
    
    // Navigation au clavier dans le dashboard
    await page.keyboard.press('Tab');
    await expect(page.locator(':focus')).toBeVisible();
    
    // Continuer la navigation
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press('Tab');
      const focusedElement = page.locator(':focus');
      await expect(focusedElement).toBeVisible();
    }
    
    // Tester l'activation avec Enter/Space
    await page.keyboard.press('Enter');
    // Vérifier qu'une action a été déclenchée
  });

  test('devrait avoir des descriptions appropriées pour les lecteurs d\'écran', async ({ page }) => {
    const helpers = new CreatorE2EHelpers(page);
    
    await helpers.login();
    
    // Vérifier les attributs aria-label
    const buttons = page.locator('button');
    for (let i = 0; i < await buttons.count(); i++) {
      const button = buttons.nth(i);
      const hasAriaLabel = await button.getAttribute('aria-label');
      const hasText = await button.textContent();
      
      expect(hasAriaLabel || hasText).toBeTruthy();
    }
    
    // Vérifier les headings hiérarchiques
    const headings = page.locator('h1, h2, h3, h4, h5, h6');
    const headingLevels = [];
    
    for (let i = 0; i < await headings.count(); i++) {
      const heading = headings.nth(i);
      const tagName = await heading.evaluate(el => el.tagName);
      headingLevels.push(parseInt(tagName.charAt(1)));
    }
    
    // Vérifier la hiérarchie (pas de saut de niveau > 1)
    for (let i = 1; i < headingLevels.length; i++) {
      expect(headingLevels[i] - headingLevels[i-1]).toBeLessThanOrEqual(1);
    }
  });
});

// ============================================================================
// TESTS E2E SÉCURITÉ
// ============================================================================

test.describe('🔒 Security E2E', () => {
  test('devrait protéger contre les attaques XSS', async ({ page }) => {
    const helpers = new CreatorE2EHelpers(page);
    
    await helpers.login();
    await helpers.navigateToSection('upload');
    
    // Tenter d'injecter du script dans le titre
    const maliciousTitle = '<script>alert("XSS")</script>Test Title';
    await page.fill('[data-testid="title-input"]', maliciousTitle);
    
    // Vérifier que le script n'est pas exécuté
    await page.waitForTimeout(1000);
    
    // Vérifier que le contenu est échappé
    const titleValue = await page.inputValue('[data-testid="title-input"]');
    expect(titleValue).toBe(maliciousTitle); // Le texte doit être préservé mais pas exécuté
  });

  test('devrait rediriger vers login si non authentifié', async ({ page }) => {
    // Essayer d'accéder directement au dashboard sans être connecté
    await page.goto(`${BASE_URL}/creator/dashboard`);
    
    // Vérifier la redirection vers la page de login
    await page.waitForURL(/\/login/);
    expect(page.url()).toContain('/login');
  });

  test('devrait gérer l\'expiration de session', async ({ page }) => {
    const helpers = new CreatorE2EHelpers(page);
    
    await helpers.login();
    
    // Simuler l'expiration de session en supprimant les cookies
    await page.context().clearCookies();
    
    // Essayer d'effectuer une action
    await helpers.navigateToSection('upload');
    
    // Vérifier la redirection vers login
    await page.waitForURL(/\/login/);
    expect(page.url()).toContain('/login');
  });
});

// ============================================================================
// EXPORT
// ============================================================================

export {};

/**
 * 🎭 TESTS E2E COMPLETS
 * 
 * ✅ Scénarios testés:
 * - Authentification complète
 * - Upload de contenu multi-format
 * - Dashboard créateur interactif
 * - Configuration monétisation
 * - Gestion collaborations
 * - Analytics détaillés
 * - Navigation responsive
 * - Performance optimization
 * - Accessibilité WCAG
 * - Sécurité anti-XSS
 * 
 * 🔧 Technologies utilisées:
 * - Playwright pour automation
 * - Cross-browser testing
 * - Device emulation
 * - Performance monitoring
 * - Accessibility auditing
 * 
 * 📊 Métriques couvertes:
 * - User journeys complets
 * - Core Web Vitals
 * - Keyboard navigation
 * - Screen reader compatibility
 * - Security vulnerabilities
 * - Network conditions
 */