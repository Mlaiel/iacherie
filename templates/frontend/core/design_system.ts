/**
 * 🎨 DESIGN SYSTEM - ENTERPRISE UI FOUNDATION
 * ===========================================
 * 
 * Complete Design System for IA Chérie Creator Economy
 * Token-based design, component specifications, patterns
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

import { Theme } from './theme_provider';

// Design Tokens
export interface DesignTokens {
  colors: {
    primitive: {
      white: string;
      black: string;
      transparent: string;
      inherit: string;
    };
    semantic: {
      primary: string;
      secondary: string;
      success: string;
      warning: string;
      error: string;
      info: string;
    };
    interactive: {
      default: string;
      hover: string;
      active: string;
      disabled: string;
      focus: string;
    };
    surface: {
      background: string;
      overlay: string;
      elevated: string;
      sunken: string;
    };
  };
  typography: {
    scale: {
      display: {
        large: string;
        medium: string;
        small: string;
      };
      headline: {
        large: string;
        medium: string;
        small: string;
      };
      title: {
        large: string;
        medium: string;
        small: string;
      };
      label: {
        large: string;
        medium: string;
        small: string;
      };
      body: {
        large: string;
        medium: string;
        small: string;
      };
    };
    weight: {
      light: number;
      regular: number;
      medium: number;
      bold: number;
    };
  };
  spacing: {
    density: {
      compact: {
        xxs: string;
        xs: string;
        sm: string;
        md: string;
        lg: string;
        xl: string;
        xxl: string;
      };
      comfortable: {
        xxs: string;
        xs: string;
        sm: string;
        md: string;
        lg: string;
        xl: string;
        xxl: string;
      };
      spacious: {
        xxs: string;
        xs: string;
        sm: string;
        md: string;
        lg: string;
        xl: string;
        xxl: string;
      };
    };
  };
  elevation: {
    level0: string;
    level1: string;
    level2: string;
    level3: string;
    level4: string;
    level5: string;
  };
  motion: {
    duration: {
      instant: string;
      fast: string;
      moderate: string;
      slow: string;
      deliberate: string;
    };
    easing: {
      standard: string;
      emphasized: string;
      decelerated: string;
      accelerated: string;
    };
  };
}

// Component Specifications
export interface ComponentSpec {
  name: string;
  variants: string[];
  sizes: string[];
  states: string[];
  tokens: {
    color?: string[];
    spacing?: string[];
    typography?: string[];
    elevation?: string[];
  };
  accessibility: {
    roles: string[];
    properties: string[];
    states: string[];
  };
}

// Layout Specifications
export interface LayoutSpec {
  name: string;
  structure: {
    areas: string[];
    hierarchy: string[];
    flow: string;
  };
  breakpoints: {
    xs?: Partial<LayoutStructure>;
    sm?: Partial<LayoutStructure>;
    md?: Partial<LayoutStructure>;
    lg?: Partial<LayoutStructure>;
    xl?: Partial<LayoutStructure>;
  };
}

interface LayoutStructure {
  columns: number;
  gaps: string;
  padding: string;
  maxWidth: string;
}

// Interaction Patterns
export interface InteractionPattern {
  name: string;
  type: 'gesture' | 'keyboard' | 'voice' | 'hover' | 'focus';
  trigger: string;
  response: string;
  feedback: {
    visual?: string;
    auditory?: string;
    haptic?: string;
  };
  accessibility: {
    alternatives: string[];
    announcements: string[];
  };
}

// Design System Class
export class DesignSystem {
  private theme: Theme;
  private tokens: DesignTokens;
  private components: Map<string, ComponentSpec>;
  private layouts: Map<string, LayoutSpec>;
  private patterns: Map<string, InteractionPattern>;

  constructor(theme: Theme) {
    this.theme = theme;
    this.tokens = this.generateTokens(theme);
    this.components = new Map();
    this.layouts = new Map();
    this.patterns = new Map();
    this.initializeComponents();
    this.initializeLayouts();
    this.initializePatterns();
  }

  private generateTokens(theme: Theme): DesignTokens {
    return {
      colors: {
        primitive: {
          white: '#ffffff',
          black: '#000000',
          transparent: 'transparent',
          inherit: 'inherit',
        },
        semantic: {
          primary: theme.colors.primary[500],
          secondary: theme.colors.secondary[500],
          success: theme.colors.status.success,
          warning: theme.colors.status.warning,
          error: theme.colors.status.error,
          info: theme.colors.status.info,
        },
        interactive: {
          default: theme.colors.primary[500],
          hover: theme.colors.primary[600],
          active: theme.colors.primary[700],
          disabled: theme.colors.secondary[300],
          focus: theme.colors.primary[400],
        },
        surface: {
          background: theme.colors.semantic.background,
          overlay: theme.colors.semantic.surface,
          elevated: theme.mode === 'light' ? '#ffffff' : '#334155',
          sunken: theme.mode === 'light' ? '#f1f5f9' : '#1e293b',
        },
      },
      typography: {
        scale: {
          display: {
            large: theme.typography.fontSize['6xl'],
            medium: theme.typography.fontSize['5xl'],
            small: theme.typography.fontSize['4xl'],
          },
          headline: {
            large: theme.typography.fontSize['3xl'],
            medium: theme.typography.fontSize['2xl'],
            small: theme.typography.fontSize.xl,
          },
          title: {
            large: theme.typography.fontSize.lg,
            medium: theme.typography.fontSize.base,
            small: theme.typography.fontSize.sm,
          },
          label: {
            large: theme.typography.fontSize.base,
            medium: theme.typography.fontSize.sm,
            small: theme.typography.fontSize.xs,
          },
          body: {
            large: theme.typography.fontSize.lg,
            medium: theme.typography.fontSize.base,
            small: theme.typography.fontSize.sm,
          },
        },
        weight: {
          light: theme.typography.fontWeight.light,
          regular: theme.typography.fontWeight.normal,
          medium: theme.typography.fontWeight.medium,
          bold: theme.typography.fontWeight.bold,
        },
      },
      spacing: {
        density: {
          compact: {
            xxs: theme.spacing[1],
            xs: theme.spacing[2],
            sm: theme.spacing[3],
            md: theme.spacing[4],
            lg: theme.spacing[6],
            xl: theme.spacing[8],
            xxl: theme.spacing[12],
          },
          comfortable: {
            xxs: theme.spacing[2],
            xs: theme.spacing[3],
            sm: theme.spacing[4],
            md: theme.spacing[6],
            lg: theme.spacing[8],
            xl: theme.spacing[12],
            xxl: theme.spacing[16],
          },
          spacious: {
            xxs: theme.spacing[3],
            xs: theme.spacing[4],
            sm: theme.spacing[6],
            md: theme.spacing[8],
            lg: theme.spacing[12],
            xl: theme.spacing[16],
            xxl: theme.spacing[24],
          },
        },
      },
      elevation: {
        level0: theme.shadows.none,
        level1: theme.shadows.sm,
        level2: theme.shadows.md,
        level3: theme.shadows.lg,
        level4: theme.shadows.xl,
        level5: theme.shadows['2xl'],
      },
      motion: {
        duration: {
          instant: theme.animation.duration.faster,
          fast: theme.animation.duration.fast,
          moderate: theme.animation.duration.normal,
          slow: theme.animation.duration.slow,
          deliberate: theme.animation.duration.slower,
        },
        easing: {
          standard: theme.animation.easing.easeInOut,
          emphasized: theme.animation.easing.bounceOut,
          decelerated: theme.animation.easing.easeOut,
          accelerated: theme.animation.easing.easeIn,
        },
      },
    };
  }

  private initializeComponents(): void {
    // Button Component Specification
    this.components.set('button', {
      name: 'Button',
      variants: ['primary', 'secondary', 'tertiary', 'ghost', 'link'],
      sizes: ['small', 'medium', 'large'],
      states: ['default', 'hover', 'active', 'disabled', 'loading'],
      tokens: {
        color: ['interactive.default', 'interactive.hover', 'interactive.active'],
        spacing: ['density.comfortable.sm', 'density.comfortable.md'],
        typography: ['scale.label.medium', 'scale.label.large'],
        elevation: ['level0', 'level1'],
      },
      accessibility: {
        roles: ['button'],
        properties: ['aria-label', 'aria-describedby', 'aria-pressed'],
        states: ['aria-disabled', 'aria-busy'],
      },
    });

    // Input Component Specification
    this.components.set('input', {
      name: 'Input',
      variants: ['outlined', 'filled', 'underlined'],
      sizes: ['small', 'medium', 'large'],
      states: ['default', 'focus', 'error', 'disabled', 'readonly'],
      tokens: {
        color: ['surface.background', 'interactive.default', 'semantic.error'],
        spacing: ['density.comfortable.sm', 'density.comfortable.md'],
        typography: ['scale.body.medium', 'scale.label.small'],
        elevation: ['level0', 'level1'],
      },
      accessibility: {
        roles: ['textbox', 'combobox', 'spinbutton'],
        properties: ['aria-label', 'aria-describedby', 'aria-invalid'],
        states: ['aria-required', 'aria-readonly'],
      },
    });

    // Card Component Specification
    this.components.set('card', {
      name: 'Card',
      variants: ['elevated', 'outlined', 'filled'],
      sizes: ['small', 'medium', 'large', 'full'],
      states: ['default', 'hover', 'selected', 'loading'],
      tokens: {
        color: ['surface.elevated', 'surface.background'],
        spacing: ['density.comfortable.md', 'density.comfortable.lg'],
        elevation: ['level1', 'level2', 'level3'],
      },
      accessibility: {
        roles: ['article', 'region', 'group'],
        properties: ['aria-label', 'aria-describedby'],
        states: ['aria-selected', 'aria-busy'],
      },
    });

    // Modal Component Specification
    this.components.set('modal', {
      name: 'Modal',
      variants: ['dialog', 'alert', 'confirmation'],
      sizes: ['small', 'medium', 'large', 'fullscreen'],
      states: ['closed', 'opening', 'open', 'closing'],
      tokens: {
        color: ['surface.elevated', 'surface.overlay'],
        spacing: ['density.spacious.lg', 'density.spacious.xl'],
        elevation: ['level4', 'level5'],
      },
      accessibility: {
        roles: ['dialog', 'alertdialog'],
        properties: ['aria-modal', 'aria-labelledby', 'aria-describedby'],
        states: ['aria-hidden'],
      },
    });

    // Navigation Component Specification
    this.components.set('navigation', {
      name: 'Navigation',
      variants: ['horizontal', 'vertical', 'breadcrumb', 'pagination'],
      sizes: ['compact', 'comfortable', 'spacious'],
      states: ['default', 'collapsed', 'expanded'],
      tokens: {
        color: ['surface.background', 'interactive.default'],
        spacing: ['density.comfortable.sm', 'density.comfortable.md'],
        typography: ['scale.label.medium'],
      },
      accessibility: {
        roles: ['navigation', 'menubar', 'menu'],
        properties: ['aria-label', 'aria-current'],
        states: ['aria-expanded', 'aria-selected'],
      },
    });
  }

  private initializeLayouts(): void {
    // Dashboard Layout
    this.layouts.set('dashboard', {
      name: 'Dashboard Layout',
      structure: {
        areas: ['header', 'sidebar', 'main', 'footer'],
        hierarchy: ['header', 'content', 'footer'],
        flow: 'grid',
      },
      breakpoints: {
        xs: { columns: 1, gaps: '1rem', padding: '1rem', maxWidth: '100%' },
        sm: { columns: 1, gaps: '1.5rem', padding: '1.5rem', maxWidth: '100%' },
        md: { columns: 12, gaps: '2rem', padding: '2rem', maxWidth: '100%' },
        lg: { columns: 12, gaps: '2rem', padding: '2rem', maxWidth: '1200px' },
        xl: { columns: 12, gaps: '2.5rem', padding: '2.5rem', maxWidth: '1400px' },
      },
    });

    // Landing Page Layout
    this.layouts.set('landing', {
      name: 'Landing Page Layout',
      structure: {
        areas: ['hero', 'features', 'testimonials', 'cta', 'footer'],
        hierarchy: ['hero', 'content', 'footer'],
        flow: 'stack',
      },
      breakpoints: {
        xs: { columns: 1, gaps: '2rem', padding: '1rem', maxWidth: '100%' },
        sm: { columns: 1, gaps: '3rem', padding: '1.5rem', maxWidth: '100%' },
        md: { columns: 1, gaps: '4rem', padding: '2rem', maxWidth: '768px' },
        lg: { columns: 1, gaps: '5rem', padding: '2rem', maxWidth: '1024px' },
        xl: { columns: 1, gaps: '6rem', padding: '2rem', maxWidth: '1200px' },
      },
    });

    // Content Layout
    this.layouts.set('content', {
      name: 'Content Layout',
      structure: {
        areas: ['header', 'content', 'sidebar', 'footer'],
        hierarchy: ['header', 'main', 'footer'],
        flow: 'flex',
      },
      breakpoints: {
        xs: { columns: 1, gaps: '1rem', padding: '1rem', maxWidth: '100%' },
        sm: { columns: 1, gaps: '1.5rem', padding: '1.5rem', maxWidth: '100%' },
        md: { columns: 3, gaps: '2rem', padding: '2rem', maxWidth: '768px' },
        lg: { columns: 4, gaps: '2rem', padding: '2rem', maxWidth: '1024px' },
        xl: { columns: 4, gaps: '2.5rem', padding: '2rem', maxWidth: '1200px' },
      },
    });
  }

  private initializePatterns(): void {
    // Click Interaction
    this.patterns.set('click', {
      name: 'Click Interaction',
      type: 'gesture',
      trigger: 'pointer down + pointer up',
      response: 'execute action',
      feedback: {
        visual: 'scale transform + color change',
        auditory: 'click sound (optional)',
        haptic: 'light tap (mobile)',
      },
      accessibility: {
        alternatives: ['keyboard enter', 'keyboard space'],
        announcements: ['action performed', 'state changed'],
      },
    });

    // Hover Interaction
    this.patterns.set('hover', {
      name: 'Hover Interaction',
      type: 'hover',
      trigger: 'pointer enter',
      response: 'reveal additional information',
      feedback: {
        visual: 'elevation change + color transition',
        auditory: 'none',
        haptic: 'none',
      },
      accessibility: {
        alternatives: ['focus state', 'keyboard navigation'],
        announcements: ['interactive element', 'additional info available'],
      },
    });

    // Focus Interaction
    this.patterns.set('focus', {
      name: 'Focus Interaction',
      type: 'focus',
      trigger: 'keyboard navigation',
      response: 'indicate focused element',
      feedback: {
        visual: 'focus ring + high contrast outline',
        auditory: 'screen reader announcement',
        haptic: 'none',
      },
      accessibility: {
        alternatives: ['mouse hover'],
        announcements: ['element focused', 'element type', 'element state'],
      },
    });

    // Drag and Drop
    this.patterns.set('dragdrop', {
      name: 'Drag and Drop',
      type: 'gesture',
      trigger: 'long press + drag',
      response: 'move element',
      feedback: {
        visual: 'elevation + ghost element + drop zones',
        auditory: 'pickup and drop sounds',
        haptic: 'start + end vibration',
      },
      accessibility: {
        alternatives: ['keyboard cut/paste', 'context menu'],
        announcements: ['picked up', 'dropped', 'position changed'],
      },
    });

    // Swipe Gesture
    this.patterns.set('swipe', {
      name: 'Swipe Gesture',
      type: 'gesture',
      trigger: 'fast horizontal drag',
      response: 'navigate or dismiss',
      feedback: {
        visual: 'slide animation + momentum',
        auditory: 'swipe sound (optional)',
        haptic: 'directional feedback',
      },
      accessibility: {
        alternatives: ['keyboard arrow keys', 'navigation buttons'],
        announcements: ['page changed', 'item dismissed'],
      },
    });
  }

  // Public Methods
  public getToken(path: string): any {
    return path.split('.').reduce((current, key) => current?.[key], this.tokens);
  }

  public getComponent(name: string): ComponentSpec | undefined {
    return this.components.get(name);
  }

  public getLayout(name: string): LayoutSpec | undefined {
    return this.layouts.get(name);
  }

  public getPattern(name: string): InteractionPattern | undefined {
    return this.patterns.get(name);
  }

  public getAllComponents(): ComponentSpec[] {
    return Array.from(this.components.values());
  }

  public getAllLayouts(): LayoutSpec[] {
    return Array.from(this.layouts.values());
  }

  public getAllPatterns(): InteractionPattern[] {
    return Array.from(this.patterns.values());
  }

  public generateCSS(): string {
    let css = ':root {\n';
    
    // Generate color tokens
    Object.entries(this.tokens.colors.primitive).forEach(([key, value]) => {
      css += `  --color-primitive-${key}: ${value};\n`;
    });
    
    Object.entries(this.tokens.colors.semantic).forEach(([key, value]) => {
      css += `  --color-semantic-${key}: ${value};\n`;
    });
    
    Object.entries(this.tokens.colors.interactive).forEach(([key, value]) => {
      css += `  --color-interactive-${key}: ${value};\n`;
    });
    
    Object.entries(this.tokens.colors.surface).forEach(([key, value]) => {
      css += `  --color-surface-${key}: ${value};\n`;
    });
    
    // Generate spacing tokens
    Object.entries(this.tokens.spacing.density.comfortable).forEach(([key, value]) => {
      css += `  --spacing-${key}: ${value};\n`;
    });
    
    // Generate typography tokens
    Object.entries(this.tokens.typography.scale.body).forEach(([key, value]) => {
      css += `  --typography-body-${key}: ${value};\n`;
    });
    
    Object.entries(this.tokens.typography.weight).forEach(([key, value]) => {
      css += `  --typography-weight-${key}: ${value};\n`;
    });
    
    // Generate elevation tokens
    Object.entries(this.tokens.elevation).forEach(([key, value]) => {
      css += `  --elevation-${key}: ${value};\n`;
    });
    
    // Generate motion tokens
    Object.entries(this.tokens.motion.duration).forEach(([key, value]) => {
      css += `  --motion-duration-${key}: ${value};\n`;
    });
    
    Object.entries(this.tokens.motion.easing).forEach(([key, value]) => {
      css += `  --motion-easing-${key}: ${value};\n`;
    });
    
    css += '}\n';
    return css;
  }

  public validateComponent(name: string, props: any): boolean {
    const spec = this.getComponent(name);
    if (!spec) return false;
    
    // Validate variant
    if (props.variant && !spec.variants.includes(props.variant)) {
      console.warn(`Invalid variant "${props.variant}" for component "${name}"`);
      return false;
    }
    
    // Validate size
    if (props.size && !spec.sizes.includes(props.size)) {
      console.warn(`Invalid size "${props.size}" for component "${name}"`);
      return false;
    }
    
    return true;
  }
}

// Design System Hook
export const useDesignSystem = (theme: Theme) => {
  return new DesignSystem(theme);
};

// Export default instance
export default DesignSystem;