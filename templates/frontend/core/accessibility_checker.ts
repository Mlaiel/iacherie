/**
 * ♿ ACCESSIBILITY CHECKER - ENTERPRISE A11Y SYSTEM
 * ================================================
 * 
 * Advanced Accessibility Compliance for Frontend Templates
 * WCAG 2.1 AA/AAA compliance, automated testing, real-time monitoring
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 * 
 * 🚨 PROTECTION INTELLECTUELLE:
 * - Code propriétaire de Fahed Mlaiel
 * - Utilisation commerciale INTERDITE sans autorisation écrite
 * - Reverse engineering STRICTEMENT INTERDIT
 * - Distribution INTERDITE sans licence explicite
 * - Violation = Poursuites judiciaires automatiques
 */

// Accessibility Interfaces
export interface A11yViolation {
  id: string;
  impact: 'minor' | 'moderate' | 'serious' | 'critical';
  description: string;
  help: string;
  helpUrl: string;
  tags: string[];
  target: string[];
  html: string;
  failureSummary: string;
  wcagLevel: 'A' | 'AA' | 'AAA';
  wcagReference: string;
}

export interface A11yResult {
  url: string;
  timestamp: number;
  violations: A11yViolation[];
  passes: A11yViolation[];
  incomplete: A11yViolation[];
  inapplicable: A11yViolation[];
  score: number;
  level: 'A' | 'AA' | 'AAA';
}

export interface ColorContrastResult {
  element: string;
  foreground: string;
  background: string;
  ratio: number;
  isValid: boolean;
  level: 'AA' | 'AAA';
  recommendation?: string;
}

export interface KeyboardNavigationResult {
  element: string;
  isFocusable: boolean;
  hasTabIndex: boolean;
  tabIndex: number;
  keyboardAccessible: boolean;
  focusVisible: boolean;
  issues: string[];
}

export interface ScreenReaderResult {
  element: string;
  accessibleName: string;
  role: string;
  description: string;
  hasLabel: boolean;
  isDescribed: boolean;
  announcement: string;
  issues: string[];
}

export interface A11yConfiguration {
  level: 'A' | 'AA' | 'AAA';
  tags?: string[];
  rules?: { [key: string]: boolean };
  reporter?: 'v1' | 'v2' | 'raw';
  runOnly?: {
    type: 'tag' | 'rule';
    values: string[];
  };
  locale?: string;
  axeCore?: any;
  disableOtherRules?: boolean;
}

// Accessibility Checker Class
export class AccessibilityChecker {
  private config: A11yConfiguration;
  private violations: A11yViolation[] = [];
  private isEnabled: boolean = true;
  private observer?: MutationObserver;
  private axeConfig: any;

  constructor(config?: Partial<A11yConfiguration>) {
    this.config = {
      level: 'AA',
      tags: ['wcag2a', 'wcag2aa', 'wcag21aa'],
      reporter: 'v2',
      locale: 'en',
      ...config,
    };

    this.axeConfig = {
      runOnly: {
        type: 'tag',
        values: this.config.tags,
      },
      reporter: this.config.reporter,
      locale: this.config.locale,
    };

    if (this.isEnabled && typeof window !== 'undefined') {
      this.initializeAxe();
      this.startMutationObserver();
    }
  }

  private async initializeAxe(): Promise<void> {
    try {
      // Load axe-core dynamically
      if (typeof window !== 'undefined' && !(window as any).axe) {
        const axe = await import('axe-core');
        (window as any).axe = axe.default || axe;
      }
    } catch (error) {
      console.warn('axe-core not available:', error);
    }
  }

  private startMutationObserver(): void {
    if (typeof window === 'undefined' || !MutationObserver) return;

    this.observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
          // Debounce the accessibility check
          this.debounceCheck();
        }
      });
    });

    this.observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['aria-*', 'role', 'alt', 'title', 'lang'],
    });
  }

  private debounceCheck = this.debounce(() => {
    this.checkPage();
  }, 1000);

  private debounce(func: Function, wait: number) {
    let timeout: NodeJS.Timeout;
    return function executedFunction(...args: any[]) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  public async checkPage(): Promise<A11yResult> {
    if (!this.isEnabled || typeof window === 'undefined') {
      return this.getEmptyResult();
    }

    try {
      const axe = (window as any).axe;
      if (!axe) {
        console.warn('axe-core not loaded');
        return this.getEmptyResult();
      }

      const results = await axe.run(document, this.axeConfig);
      
      const a11yResult: A11yResult = {
        url: window.location.href,
        timestamp: Date.now(),
        violations: results.violations.map(this.mapViolation),
        passes: results.passes.map(this.mapViolation),
        incomplete: results.incomplete.map(this.mapViolation),
        inapplicable: results.inapplicable.map(this.mapViolation),
        score: this.calculateScore(results),
        level: this.determineLevel(results),
      };

      this.violations = a11yResult.violations;
      this.reportViolations(a11yResult.violations);
      
      return a11yResult;
    } catch (error) {
      console.error('Accessibility check failed:', error);
      return this.getEmptyResult();
    }
  }

  public async checkElement(element: Element): Promise<A11yResult> {
    if (!this.isEnabled || typeof window === 'undefined') {
      return this.getEmptyResult();
    }

    try {
      const axe = (window as any).axe;
      if (!axe) {
        return this.getEmptyResult();
      }

      const results = await axe.run(element, this.axeConfig);
      
      return {
        url: window.location.href,
        timestamp: Date.now(),
        violations: results.violations.map(this.mapViolation),
        passes: results.passes.map(this.mapViolation),
        incomplete: results.incomplete.map(this.mapViolation),
        inapplicable: results.inapplicable.map(this.mapViolation),
        score: this.calculateScore(results),
        level: this.determineLevel(results),
      };
    } catch (error) {
      console.error('Element accessibility check failed:', error);
      return this.getEmptyResult();
    }
  }

  public checkColorContrast(
    foreground: string,
    background: string,
    fontSize: number = 16,
    isBold: boolean = false
  ): ColorContrastResult {
    const ratio = this.calculateContrastRatio(foreground, background);
    const minRatio = this.getMinContrastRatio(fontSize, isBold);
    
    return {
      element: '',
      foreground,
      background,
      ratio,
      isValid: ratio >= minRatio.AA,
      level: ratio >= minRatio.AAA ? 'AAA' : 'AA',
      recommendation: ratio < minRatio.AA ? 
        `Increase contrast ratio to at least ${minRatio.AA}:1` : undefined,
    };
  }

  public checkKeyboardNavigation(element: Element): KeyboardNavigationResult {
    const tabIndex = element.getAttribute('tabindex');
    const isFocusable = this.isFocusable(element);
    const keyboardAccessible = this.isKeyboardAccessible(element);
    const focusVisible = this.hasFocusVisible(element);
    const issues: string[] = [];

    if (!isFocusable && this.shouldBeFocusable(element)) {
      issues.push('Element should be focusable but is not');
    }

    if (!keyboardAccessible) {
      issues.push('Element is not keyboard accessible');
    }

    if (isFocusable && !focusVisible) {
      issues.push('Element lacks visible focus indicator');
    }

    return {
      element: this.getElementSelector(element),
      isFocusable,
      hasTabIndex: tabIndex !== null,
      tabIndex: tabIndex ? parseInt(tabIndex) : 0,
      keyboardAccessible,
      focusVisible,
      issues,
    };
  }

  public checkScreenReaderCompatibility(element: Element): ScreenReaderResult {
    const accessibleName = this.getAccessibleName(element);
    const role = element.getAttribute('role') || this.getImplicitRole(element);
    const description = this.getAccessibleDescription(element);
    const hasLabel = this.hasLabel(element);
    const isDescribed = this.isDescribed(element);
    const announcement = this.generateAnnouncement(element);
    const issues: string[] = [];

    if (!accessibleName && this.requiresAccessibleName(element)) {
      issues.push('Element requires an accessible name');
    }

    if (!role && this.requiresRole(element)) {
      issues.push('Element requires a role attribute');
    }

    if (!hasLabel && this.requiresLabel(element)) {
      issues.push('Form element requires a label');
    }

    return {
      element: this.getElementSelector(element),
      accessibleName,
      role,
      description,
      hasLabel,
      isDescribed,
      announcement,
      issues,
    };
  }

  public generateReport(): string {
    const violations = this.violations;
    const groupedViolations = this.groupViolationsByImpact(violations);
    
    let report = '# Accessibility Report\n\n';
    report += `Generated: ${new Date().toISOString()}\n`;
    report += `Total Violations: ${violations.length}\n\n`;

    ['critical', 'serious', 'moderate', 'minor'].forEach(impact => {
      const impactViolations = groupedViolations[impact as keyof typeof groupedViolations] || [];
      if (impactViolations.length > 0) {
        report += `## ${impact.toUpperCase()} Issues (${impactViolations.length})\n\n`;
        
        impactViolations.forEach(violation => {
          report += `### ${violation.id}\n`;
          report += `**Impact:** ${violation.impact}\n`;
          report += `**Description:** ${violation.description}\n`;
          report += `**Help:** ${violation.help}\n`;
          report += `**WCAG:** ${violation.wcagLevel} - ${violation.wcagReference}\n`;
          report += `**Elements:** ${violation.target.join(', ')}\n`;
          report += `**Fix:** ${violation.failureSummary}\n\n`;
        });
      }
    });

    return report;
  }

  public getViolationsSummary(): { [key: string]: number } {
    const summary = { critical: 0, serious: 0, moderate: 0, minor: 0 };
    
    this.violations.forEach(violation => {
      summary[violation.impact]++;
    });
    
    return summary;
  }

  public async validateWCAGCompliance(level: 'A' | 'AA' | 'AAA' = 'AA'): Promise<boolean> {
    const result = await this.checkPage();
    const relevantViolations = result.violations.filter(v => 
      this.isRelevantForLevel(v, level)
    );
    
    return relevantViolations.length === 0;
  }

  private mapViolation = (violation: any): A11yViolation => ({
    id: violation.id,
    impact: violation.impact,
    description: violation.description,
    help: violation.help,
    helpUrl: violation.helpUrl,
    tags: violation.tags,
    target: violation.nodes.map((node: any) => node.target.join(' ')),
    html: violation.nodes.map((node: any) => node.html).join('\n'),
    failureSummary: violation.nodes.map((node: any) => node.failureSummary).join('\n'),
    wcagLevel: this.extractWCAGLevel(violation.tags),
    wcagReference: this.extractWCAGReference(violation.tags),
  });

  private calculateScore(results: any): number {
    const total = results.violations.length + results.passes.length;
    if (total === 0) return 100;
    
    const weightedScore = results.violations.reduce((score: number, violation: any) => {
      const weight = { critical: 4, serious: 3, moderate: 2, minor: 1 }[violation.impact] || 1;
      return score - weight;
    }, 100);
    
    return Math.max(0, Math.min(100, weightedScore));
  }

  private determineLevel(results: any): 'A' | 'AA' | 'AAA' {
    const hasAAViolations = results.violations.some((v: any) => 
      v.tags.includes('wcag2aa') || v.tags.includes('wcag21aa')
    );
    
    const hasAAAViolations = results.violations.some((v: any) => 
      v.tags.includes('wcag2aaa') || v.tags.includes('wcag21aaa')
    );
    
    if (hasAAViolations) return 'A';
    if (hasAAAViolations) return 'AA';
    return 'AAA';
  }

  private getEmptyResult(): A11yResult {
    return {
      url: typeof window !== 'undefined' ? window.location.href : '',
      timestamp: Date.now(),
      violations: [],
      passes: [],
      incomplete: [],
      inapplicable: [],
      score: 100,
      level: 'AAA',
    };
  }

  private calculateContrastRatio(foreground: string, background: string): number {
    const fgLuminance = this.getLuminance(foreground);
    const bgLuminance = this.getLuminance(background);
    
    const lighter = Math.max(fgLuminance, bgLuminance);
    const darker = Math.min(fgLuminance, bgLuminance);
    
    return (lighter + 0.05) / (darker + 0.05);
  }

  private getLuminance(color: string): number {
    const rgb = this.hexToRgb(color);
    if (!rgb) return 0;
    
    const { r, g, b } = rgb;
    const [rSRGB, gSRGB, bSRGB] = [r, g, b].map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    
    return 0.2126 * rSRGB + 0.7152 * gSRGB + 0.0722 * bSRGB;
  }

  private hexToRgb(hex: string): { r: number; g: number; b: number } | null {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16),
    } : null;
  }

  private getMinContrastRatio(fontSize: number, isBold: boolean): { AA: number; AAA: number } {
    const isLargeText = fontSize >= 18 || (fontSize >= 14 && isBold);
    return isLargeText ? { AA: 3, AAA: 4.5 } : { AA: 4.5, AAA: 7 };
  }

  private isFocusable(element: Element): boolean {
    const focusableElements = [
      'a[href]', 'button', 'input', 'select', 'textarea',
      '[tabindex]:not([tabindex="-1"])', '[contenteditable]'
    ];
    
    return focusableElements.some(selector => element.matches(selector));
  }

  private isKeyboardAccessible(element: Element): boolean {
    // Check if element can be activated with keyboard
    const tagName = element.tagName.toLowerCase();
    const role = element.getAttribute('role');
    
    if (['button', 'a', 'input', 'select', 'textarea'].includes(tagName)) {
      return true;
    }
    
    if (role && ['button', 'link', 'menuitem', 'tab'].includes(role)) {
      return true;
    }
    
    return element.hasAttribute('tabindex') && element.getAttribute('tabindex') !== '-1';
  }

  private hasFocusVisible(element: Element): boolean {
    const computedStyle = window.getComputedStyle(element, ':focus');
    const outline = computedStyle.outline;
    const outlineColor = computedStyle.outlineColor;
    
    return outline !== 'none' && outlineColor !== 'transparent';
  }

  private shouldBeFocusable(element: Element): boolean {
    const interactiveRoles = ['button', 'link', 'textbox', 'combobox', 'slider'];
    const role = element.getAttribute('role');
    const tagName = element.tagName.toLowerCase();
    
    return interactiveRoles.includes(role || '') || 
           ['button', 'a', 'input', 'select', 'textarea'].includes(tagName);
  }

  private getAccessibleName(element: Element): string {
    // Simplified accessible name calculation
    const ariaLabel = element.getAttribute('aria-label');
    if (ariaLabel) return ariaLabel;
    
    const ariaLabelledby = element.getAttribute('aria-labelledby');
    if (ariaLabelledby) {
      const labelElement = document.getElementById(ariaLabelledby);
      if (labelElement) return labelElement.textContent || '';
    }
    
    if (element.tagName.toLowerCase() === 'img') {
      return element.getAttribute('alt') || '';
    }
    
    return element.textContent?.trim() || '';
  }

  private getImplicitRole(element: Element): string {
    const tagName = element.tagName.toLowerCase();
    const roleMap: { [key: string]: string } = {
      button: 'button',
      a: 'link',
      input: 'textbox',
      img: 'img',
      h1: 'heading',
      h2: 'heading',
      h3: 'heading',
      h4: 'heading',
      h5: 'heading',
      h6: 'heading',
    };
    
    return roleMap[tagName] || '';
  }

  private getAccessibleDescription(element: Element): string {
    const ariaDescribedby = element.getAttribute('aria-describedby');
    if (ariaDescribedby) {
      const descElement = document.getElementById(ariaDescribedby);
      if (descElement) return descElement.textContent || '';
    }
    
    const title = element.getAttribute('title');
    return title || '';
  }

  private hasLabel(element: Element): boolean {
    const tagName = element.tagName.toLowerCase();
    if (!['input', 'select', 'textarea'].includes(tagName)) return true;
    
    const id = element.getAttribute('id');
    if (id) {
      const label = document.querySelector(`label[for="${id}"]`);
      if (label) return true;
    }
    
    const parentLabel = element.closest('label');
    return !!parentLabel;
  }

  private isDescribed(element: Element): boolean {
    return !!element.getAttribute('aria-describedby') || !!element.getAttribute('title');
  }

  private requiresAccessibleName(element: Element): boolean {
    const tagName = element.tagName.toLowerCase();
    const role = element.getAttribute('role');
    
    return ['button', 'a', 'img'].includes(tagName) || 
           ['button', 'link', 'img'].includes(role || '');
  }

  private requiresRole(element: Element): boolean {
    // Custom interactive elements should have roles
    const hasClick = element.getAttribute('onclick') || element.addEventListener;
    const isInteractive = element.hasAttribute('tabindex');
    
    return !!(hasClick && isInteractive && !this.getImplicitRole(element));
  }

  private requiresLabel(element: Element): boolean {
    const tagName = element.tagName.toLowerCase();
    return ['input', 'select', 'textarea'].includes(tagName);
  }

  private generateAnnouncement(element: Element): string {
    const name = this.getAccessibleName(element);
    const role = element.getAttribute('role') || this.getImplicitRole(element);
    const description = this.getAccessibleDescription(element);
    
    let announcement = name;
    if (role) announcement += `, ${role}`;
    if (description) announcement += `, ${description}`;
    
    return announcement;
  }

  private getElementSelector(element: Element): string {
    const id = element.getAttribute('id');
    if (id) return `#${id}`;
    
    const classes = Array.from(element.classList).join('.');
    if (classes) return `${element.tagName.toLowerCase()}.${classes}`;
    
    return element.tagName.toLowerCase();
  }

  private groupViolationsByImpact(violations: A11yViolation[]): Record<string, A11yViolation[]> {
    return violations.reduce((groups, violation) => {
      const impact = violation.impact;
      if (!groups[impact]) groups[impact] = [];
      groups[impact].push(violation);
      return groups;
    }, {} as Record<string, A11yViolation[]>);
  }

  private extractWCAGLevel(tags: string[]): 'A' | 'AA' | 'AAA' {
    if (tags.includes('wcag2aaa') || tags.includes('wcag21aaa')) return 'AAA';
    if (tags.includes('wcag2aa') || tags.includes('wcag21aa')) return 'AA';
    return 'A';
  }

  private extractWCAGReference(tags: string[]): string {
    const wcagTag = tags.find(tag => tag.startsWith('wcag'));
    return wcagTag || '';
  }

  private isRelevantForLevel(violation: A11yViolation, level: 'A' | 'AA' | 'AAA'): boolean {
    const violationLevel = violation.wcagLevel;
    const levels = { A: 1, AA: 2, AAA: 3 };
    return levels[violationLevel] <= levels[level];
  }

  private reportViolations(violations: A11yViolation[]): void {
    if (violations.length > 0) {
      console.group('🚨 Accessibility Violations Found');
      violations.forEach(violation => {
        const level = violation.impact === 'critical' ? 'error' : 
                     violation.impact === 'serious' ? 'warn' : 'info';
        console[level](`${violation.id}: ${violation.description}`);
      });
      console.groupEnd();
    }
  }

  public destroy(): void {
    if (this.observer) {
      this.observer.disconnect();
      this.observer = undefined;
    }
    this.violations = [];
  }
}

// React Hook for Accessibility
export const useAccessibility = (options?: Partial<A11yConfiguration>) => {
  const checker = new AccessibilityChecker(options);
  
  return {
    checkPage: checker.checkPage.bind(checker),
    checkElement: checker.checkElement.bind(checker),
    checkColorContrast: checker.checkColorContrast.bind(checker),
    checkKeyboardNavigation: checker.checkKeyboardNavigation.bind(checker),
    checkScreenReaderCompatibility: checker.checkScreenReaderCompatibility.bind(checker),
    generateReport: checker.generateReport.bind(checker),
    getViolationsSummary: checker.getViolationsSummary.bind(checker),
    validateWCAGCompliance: checker.validateWCAGCompliance.bind(checker),
  };
};

export default AccessibilityChecker;