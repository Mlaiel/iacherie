/**
 * Theme Management Library
 */

interface ThemeColors {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  text: string;
  textSecondary: string;
  border: string;
  error: string;
  warning: string;
  success: string;
  info: string;
}

interface ThemeSpacing {
  xs: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
  '2xl': string;
}

interface ThemeTypography {
  fontFamily: string;
  fontSize: {
    xs: string;
    sm: string;
    base: string;
    lg: string;
    xl: string;
    '2xl': string;
    '3xl': string;
  };
  fontWeight: {
    light: number;
    normal: number;
    medium: number;
    semibold: number;
    bold: number;
  };
}

interface Theme {
  name: string;
  colors: ThemeColors;
  spacing: ThemeSpacing;
  typography: ThemeTypography;
  borderRadius: string;
  shadows: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
}

class ThemeManager {
  private themes: Map<string, Theme> = new Map();
  private currentTheme: string = 'default';
  private listeners: Set<(theme: Theme) => void> = new Set();

  addTheme(theme: Theme): void {
    this.themes.set(theme.name, theme);
  }

  removeTheme(name: string): boolean {
    return this.themes.delete(name);
  }

  setTheme(name: string): boolean {
    if (!this.themes.has(name)) return false;
    
    this.currentTheme = name;
    const theme = this.themes.get(name)!;
    this.applyTheme(theme);
    this.notifyListeners(theme);
    return true;
  }

  getCurrentTheme(): Theme | undefined {
    return this.themes.get(this.currentTheme);
  }

  getTheme(name: string): Theme | undefined {
    return this.themes.get(name);
  }

  getAllThemes(): Theme[] {
    return Array.from(this.themes.values());
  }

  getThemeNames(): string[] {
    return Array.from(this.themes.keys());
  }

  subscribe(listener: (theme: Theme) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private applyTheme(theme: Theme): void {
    const root = document.documentElement;
    
    // Apply colors as CSS custom properties
    Object.entries(theme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });
    
    // Apply spacing
    Object.entries(theme.spacing).forEach(([key, value]) => {
      root.style.setProperty(`--spacing-${key}`, value);
    });
    
    // Apply typography
    root.style.setProperty('--font-family', theme.typography.fontFamily);
    Object.entries(theme.typography.fontSize).forEach(([key, value]) => {
      root.style.setProperty(`--font-size-${key}`, value);
    });
    
    // Apply other properties
    root.style.setProperty('--border-radius', theme.borderRadius);
    Object.entries(theme.shadows).forEach(([key, value]) => {
      root.style.setProperty(`--shadow-${key}`, value);
    });
  }

  private notifyListeners(theme: Theme): void {
    this.listeners.forEach(listener => listener(theme));
  }

  createTheme(name: string, overrides: Partial<Theme>): Theme {
    const defaultTheme = this.getDefaultTheme();
    return {
      ...defaultTheme,
      ...overrides,
      name,
      colors: { ...defaultTheme.colors, ...overrides.colors },
      spacing: { ...defaultTheme.spacing, ...overrides.spacing },
      typography: {
        ...defaultTheme.typography,
        ...overrides.typography,
        fontSize: { ...defaultTheme.typography.fontSize, ...overrides.typography?.fontSize },
        fontWeight: { ...defaultTheme.typography.fontWeight, ...overrides.typography?.fontWeight },
      },
      shadows: { ...defaultTheme.shadows, ...overrides.shadows },
    };
  }

  private getDefaultTheme(): Theme {
    return {
      name: 'default',
      colors: {
        primary: '#3b82f6',
        secondary: '#64748b',
        accent: '#8b5cf6',
        background: '#ffffff',
        surface: '#f8fafc',
        text: '#1e293b',
        textSecondary: '#64748b',
        border: '#e2e8f0',
        error: '#ef4444',
        warning: '#f59e0b',
        success: '#22c55e',
        info: '#06b6d4',
      },
      spacing: {
        xs: '0.25rem',
        sm: '0.5rem',
        md: '1rem',
        lg: '1.5rem',
        xl: '2rem',
        '2xl': '3rem',
      },
      typography: {
        fontFamily: 'Inter, sans-serif',
        fontSize: {
          xs: '0.75rem',
          sm: '0.875rem',
          base: '1rem',
          lg: '1.125rem',
          xl: '1.25rem',
          '2xl': '1.5rem',
          '3xl': '1.875rem',
        },
        fontWeight: {
          light: 300,
          normal: 400,
          medium: 500,
          semibold: 600,
          bold: 700,
        },
      },
      borderRadius: '0.375rem',
      shadows: {
        sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
        lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
        xl: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
      },
    };
  }
}

export { ThemeManager, type Theme, type ThemeColors };
export default ThemeManager;
