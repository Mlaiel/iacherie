/**
 * 🧭 Navigation Component Template - Enterprise Navigation System
 * ==============================================================
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS - Propriété Intellectuelle Protégée
 * 
 * Enterprise navigation components with mobile responsiveness,
 * multi-level menus, breadcrumbs, and accessibility features.
 */

import React, { useState, useCallback, useMemo, forwardRef } from 'react';

// ========================================
// 📝 TYPE DEFINITIONS
// ========================================

interface NavigationItem {
  id: string;
  label: string;
  href?: string;
  icon?: React.ReactNode;
  badge?: string | number;
  disabled?: boolean;
  children?: NavigationItem[];
  onClick?: (item: NavigationItem) => void;
  target?: '_blank' | '_self' | '_parent' | '_top';
  exact?: boolean;
}

interface NavigationProps {
  items: NavigationItem[];
  currentPath?: string;
  mode?: 'horizontal' | 'vertical' | 'sidebar';
  theme?: 'light' | 'dark';
  collapsed?: boolean;
  sticky?: boolean;
  logo?: React.ReactNode;
  actions?: React.ReactNode;
  onItemClick?: (item: NavigationItem) => void;
  onToggle?: (collapsed: boolean) => void;
  className?: string;
  testId?: string;
}

interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: React.ReactNode;
  onClick?: () => void;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
  separator?: React.ReactNode;
  maxItems?: number;
  className?: string;
  testId?: string;
}

// ========================================
// 🎨 NAVIGATION STYLES
// ========================================

const getNavigationStyles = (mode: string, theme: string, collapsed: boolean) => ({
  nav: {
    display: 'flex',
    backgroundColor: theme === 'dark' ? '#1f2937' : '#ffffff',
    color: theme === 'dark' ? '#f9fafb' : '#374151',
    borderBottom: theme === 'dark' ? '1px solid #374151' : '1px solid #e5e7eb',
    ...(mode === 'horizontal' && {
      flexDirection: 'row' as const,
      alignItems: 'center',
      height: '64px',
      padding: '0 1rem'
    }),
    ...(mode === 'vertical' && {
      flexDirection: 'column' as const,
      width: '100%'
    }),
    ...(mode === 'sidebar' && {
      flexDirection: 'column' as const,
      width: collapsed ? '80px' : '280px',
      minHeight: '100vh',
      transition: 'width 0.3s ease',
      borderRight: theme === 'dark' ? '1px solid #374151' : '1px solid #e5e7eb',
      borderBottom: 'none'
    })
  },

  brand: {
    display: 'flex',
    alignItems: 'center',
    padding: mode === 'sidebar' ? '1rem' : '0',
    marginBottom: mode === 'sidebar' ? '1rem' : '0',
    marginRight: mode === 'horizontal' ? '2rem' : '0',
    borderBottom: mode === 'sidebar' ? (theme === 'dark' ? '1px solid #374151' : '1px solid #e5e7eb') : 'none'
  },

  menu: {
    display: 'flex',
    listStyle: 'none',
    margin: 0,
    padding: 0,
    ...(mode === 'horizontal' && {
      flexDirection: 'row' as const,
      flex: 1
    }),
    ...(mode === 'vertical' && {
      flexDirection: 'column' as const,
      width: '100%'
    }),
    ...(mode === 'sidebar' && {
      flexDirection: 'column' as const,
      flex: 1,
      padding: '0 0.5rem'
    })
  },

  menuItem: {
    position: 'relative' as const,
    ...(mode === 'horizontal' && {
      marginRight: '0.5rem'
    }),
    ...(mode === 'sidebar' && {
      marginBottom: '0.25rem'
    })
  },

  menuLink: {
    display: 'flex',
    alignItems: 'center',
    padding: mode === 'horizontal' ? '0.5rem 1rem' : '0.75rem 1rem',
    textDecoration: 'none',
    color: 'inherit',
    borderRadius: '0.375rem',
    transition: 'all 0.2s ease',
    cursor: 'pointer',
    ...(mode === 'sidebar' && collapsed && {
      justifyContent: 'center',
      padding: '0.75rem'
    })
  },

  menuLinkActive: {
    backgroundColor: theme === 'dark' ? '#3b82f6' : '#dbeafe',
    color: theme === 'dark' ? '#ffffff' : '#1e40af'
  },

  menuLinkHover: {
    backgroundColor: theme === 'dark' ? '#374151' : '#f3f4f6'
  },

  menuIcon: {
    marginRight: collapsed ? '0' : '0.75rem',
    fontSize: '1.25rem',
    minWidth: '1.25rem'
  },

  menuLabel: {
    ...(collapsed && mode === 'sidebar' && {
      display: 'none'
    })
  },

  badge: {
    marginLeft: 'auto',
    backgroundColor: '#ef4444',
    color: '#ffffff',
    fontSize: '0.75rem',
    padding: '0.125rem 0.375rem',
    borderRadius: '9999px',
    minWidth: '1.25rem',
    textAlign: 'center' as const,
    ...(collapsed && mode === 'sidebar' && {
      display: 'none'
    })
  },

  submenu: {
    listStyle: 'none',
    margin: 0,
    padding: 0,
    backgroundColor: theme === 'dark' ? '#111827' : '#f9fafb',
    borderRadius: '0.375rem',
    overflow: 'hidden',
    ...(mode === 'horizontal' && {
      position: 'absolute' as const,
      top: '100%',
      left: 0,
      minWidth: '200px',
      marginTop: '0.25rem',
      boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
      border: theme === 'dark' ? '1px solid #374151' : '1px solid #e5e7eb'
    }),
    ...(mode === 'sidebar' && {
      marginTop: '0.25rem',
      marginLeft: '1rem'
    })
  },

  actions: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    ...(mode === 'sidebar' && {
      padding: '1rem',
      borderTop: theme === 'dark' ? '1px solid #374151' : '1px solid #e5e7eb',
      marginTop: 'auto'
    })
  },

  toggleButton: {
    background: 'none',
    border: 'none',
    color: 'inherit',
    cursor: 'pointer',
    padding: '0.5rem',
    borderRadius: '0.375rem',
    transition: 'background-color 0.2s ease'
  }
});

// ========================================
// 🧭 NAVIGATION COMPONENT
// ========================================

export const Navigation = forwardRef<HTMLElement, NavigationProps>(({
  items = [],
  currentPath = '',
  mode = 'horizontal',
  theme = 'light',
  collapsed = false,
  sticky = false,
  logo,
  actions,
  onItemClick,
  onToggle,
  className = '',
  testId = 'navigation'
}, ref) => {
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const [hoveredItems, setHoveredItems] = useState<Set<string>>(new Set());

  const styles = getNavigationStyles(mode, theme, collapsed);

  const isItemActive = useCallback((item: NavigationItem): boolean => {
    if (!currentPath) return false;
    if (item.exact) {
      return currentPath === item.href;
    }
    return item.href ? currentPath.startsWith(item.href) : false;
  }, [currentPath]);

  const hasActiveChild = useCallback((item: NavigationItem): boolean => {
    if (!item.children) return false;
    return item.children.some(child => 
      isItemActive(child) || hasActiveChild(child)
    );
  }, [isItemActive]);

  const handleItemClick = useCallback((item: NavigationItem, event: React.MouseEvent) => {
    if (item.disabled) {
      event.preventDefault();
      return;
    }

    if (item.children && item.children.length > 0) {
      event.preventDefault();
      setExpandedItems(prev => {
        const newExpanded = new Set(prev);
        if (newExpanded.has(item.id)) {
          newExpanded.delete(item.id);
        } else {
          newExpanded.add(item.id);
        }
        return newExpanded;
      });
    }

    item.onClick?.(item);
    onItemClick?.(item);
  }, [onItemClick]);

  const handleMouseEnter = useCallback((itemId: string) => {
    if (mode === 'horizontal') {
      setHoveredItems(prev => new Set(prev.add(itemId)));
    }
  }, [mode]);

  const handleMouseLeave = useCallback((itemId: string) => {
    if (mode === 'horizontal') {
      setHoveredItems(prev => {
        const newHovered = new Set(prev);
        newHovered.delete(itemId);
        return newHovered;
      });
    }
  }, [mode]);

  const renderMenuItem = useCallback((item: NavigationItem, level: number = 0) => {
    const isActive = isItemActive(item);
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedItems.has(item.id);
    const isHovered = hoveredItems.has(item.id);
    const showSubmenu = hasChildren && (isExpanded || (mode === 'horizontal' && isHovered));
    const hasActiveDescendant = hasActiveChild(item);

    const linkStyle = {
      ...styles.menuLink,
      ...(isActive && styles.menuLinkActive),
      ...(item.disabled && {
        opacity: 0.5,
        cursor: 'not-allowed'
      }),
      paddingLeft: mode === 'sidebar' ? `${1 + level * 0.75}rem` : styles.menuLink.padding
    };

    return (
      <li
        key={item.id}
        style={styles.menuItem}
        onMouseEnter={() => handleMouseEnter(item.id)}
        onMouseLeave={() => handleMouseLeave(item.id)}
      >
        {item.href && !hasChildren ? (
          <a
            href={item.href}
            target={item.target}
            style={linkStyle}
            onClick={(e) => handleItemClick(item, e)}
            aria-current={isActive ? 'page' : undefined}
            aria-disabled={item.disabled}
          >
            {item.icon && (
              <span style={styles.menuIcon} aria-hidden="true">
                {item.icon}
              </span>
            )}
            <span style={styles.menuLabel}>{item.label}</span>
            {item.badge && (
              <span style={styles.badge}>{item.badge}</span>
            )}
          </a>
        ) : (
          <button
            type="button"
            style={linkStyle}
            onClick={(e) => handleItemClick(item, e)}
            aria-expanded={hasChildren ? isExpanded : undefined}
            aria-disabled={item.disabled}
          >
            {item.icon && (
              <span style={styles.menuIcon} aria-hidden="true">
                {item.icon}
              </span>
            )}
            <span style={styles.menuLabel}>{item.label}</span>
            {item.badge && (
              <span style={styles.badge}>{item.badge}</span>
            )}
            {hasChildren && !collapsed && (
              <span style={{ marginLeft: 'auto', transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }}>
                ▼
              </span>
            )}
          </button>
        )}

        {showSubmenu && (
          <ul style={styles.submenu} role="menu">
            {item.children!.map(child => renderMenuItem(child, level + 1))}
          </ul>
        )}
      </li>
    );
  }, [
    isItemActive,
    hasActiveChild,
    expandedItems,
    hoveredItems,
    mode,
    collapsed,
    styles,
    handleItemClick,
    handleMouseEnter,
    handleMouseLeave
  ]);

  const navStyle = {
    ...styles.nav,
    ...(sticky && {
      position: 'sticky' as const,
      top: 0,
      zIndex: 1000
    })
  };

  return (
    <nav
      ref={ref}
      className={className}
      style={navStyle}
      data-testid={testId}
      role="navigation"
      aria-label="Main navigation"
    >
      {(logo || (mode === 'sidebar' && onToggle)) && (
        <div style={styles.brand}>
          {mode === 'sidebar' && onToggle && (
            <button
              type="button"
              style={styles.toggleButton}
              onClick={() => onToggle(!collapsed)}
              aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              ☰
            </button>
          )}
          {logo && <div>{logo}</div>}
        </div>
      )}

      <ul style={styles.menu} role="menubar">
        {items.map(item => renderMenuItem(item))}
      </ul>

      {actions && (
        <div style={styles.actions}>
          {actions}
        </div>
      )}
    </nav>
  );
});

Navigation.displayName = 'Navigation';

// ========================================
// 🍞 BREADCRUMB COMPONENT
// ========================================

export const Breadcrumb: React.FC<BreadcrumbProps> = ({
  items = [],
  separator = '/',
  maxItems = 0,
  className = '',
  testId = 'breadcrumb'
}) => {
  const displayItems = useMemo(() => {
    if (maxItems > 0 && items.length > maxItems) {
      const startItems = items.slice(0, 1);
      const endItems = items.slice(-(maxItems - 1));
      return [...startItems, { label: '...', href: undefined }, ...endItems];
    }
    return items;
  }, [items, maxItems]);

  return (
    <nav
      className={className}
      data-testid={testId}
      aria-label="Breadcrumb"
      style={{
        padding: '0.75rem 0',
        fontSize: '0.875rem'
      }}
    >
      <ol
        style={{
          display: 'flex',
          alignItems: 'center',
          listStyle: 'none',
          margin: 0,
          padding: 0,
          gap: '0.5rem'
        }}
      >
        {displayItems.map((item, index) => (
          <li
            key={index}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            {index > 0 && (
              <span
                style={{ color: '#6b7280' }}
                aria-hidden="true"
              >
                {separator}
              </span>
            )}
            
            {item.href && index < displayItems.length - 1 ? (
              <a
                href={item.href}
                onClick={item.onClick}
                style={{
                  color: '#3b82f6',
                  textDecoration: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.25rem',
                  transition: 'color 0.2s ease'
                }}
              >
                {item.icon && <span>{item.icon}</span>}
                {item.label}
              </a>
            ) : (
              <span
                style={{
                  color: index === displayItems.length - 1 ? '#374151' : '#6b7280',
                  fontWeight: index === displayItems.length - 1 ? '500' : 'normal',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.25rem'
                }}
                aria-current={index === displayItems.length - 1 ? 'page' : undefined}
              >
                {item.icon && <span>{item.icon}</span>}
                {item.label}
              </span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
};

// ========================================
// 📱 MOBILE NAVIGATION
// ========================================

export const MobileNavigation: React.FC<NavigationProps & {
  isOpen?: boolean;
  onClose?: () => void;
}> = ({
  items = [],
  currentPath = '',
  theme = 'light',
  isOpen = false,
  onClose,
  logo,
  actions,
  onItemClick,
  className = '',
  testId = 'mobile-navigation'
}) => {
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

  const handleItemClick = useCallback((item: NavigationItem, event: React.MouseEvent) => {
    if (item.disabled) {
      event.preventDefault();
      return;
    }

    if (item.children && item.children.length > 0) {
      event.preventDefault();
      setExpandedItems(prev => {
        const newExpanded = new Set(prev);
        if (newExpanded.has(item.id)) {
          newExpanded.delete(item.id);
        } else {
          newExpanded.add(item.id);
        }
        return newExpanded;
      });
    } else {
      onClose?.();
    }

    item.onClick?.(item);
    onItemClick?.(item);
  }, [onItemClick, onClose]);

  const isItemActive = useCallback((item: NavigationItem): boolean => {
    if (!currentPath) return false;
    return item.href ? currentPath.startsWith(item.href) : false;
  }, [currentPath]);

  if (!isOpen) return null;

  return (
    <>
      {/* Overlay */}
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          zIndex: 1000
        }}
        onClick={onClose}
      />

      {/* Mobile Menu */}
      <div
        className={className}
        data-testid={testId}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          bottom: 0,
          width: '280px',
          backgroundColor: theme === 'dark' ? '#1f2937' : '#ffffff',
          color: theme === 'dark' ? '#f9fafb' : '#374151',
          zIndex: 1001,
          transform: 'translateX(0)',
          transition: 'transform 0.3s ease',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
        }}
      >
        {/* Header */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '1rem',
            borderBottom: theme === 'dark' ? '1px solid #374151' : '1px solid #e5e7eb'
          }}
        >
          {logo}
          <button
            type="button"
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: 'inherit',
              fontSize: '1.5rem',
              cursor: 'pointer',
              padding: '0.5rem'
            }}
            aria-label="Close menu"
          >
            ✕
          </button>
        </div>

        {/* Menu Items */}
        <div style={{ flex: 1, overflow: 'auto', padding: '1rem' }}>
          <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
            {items.map(item => {
              const isActive = isItemActive(item);
              const hasChildren = item.children && item.children.length > 0;
              const isExpanded = expandedItems.has(item.id);

              return (
                <li key={item.id} style={{ marginBottom: '0.25rem' }}>
                  {item.href && !hasChildren ? (
                    <a
                      href={item.href}
                      target={item.target}
                      onClick={(e) => handleItemClick(item, e)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        padding: '0.75rem',
                        textDecoration: 'none',
                        color: 'inherit',
                        borderRadius: '0.375rem',
                        backgroundColor: isActive ? (theme === 'dark' ? '#3b82f6' : '#dbeafe') : 'transparent',
                        transition: 'background-color 0.2s ease'
                      }}
                    >
                      {item.icon && (
                        <span style={{ marginRight: '0.75rem', fontSize: '1.25rem' }}>
                          {item.icon}
                        </span>
                      )}
                      <span>{item.label}</span>
                      {item.badge && (
                        <span
                          style={{
                            marginLeft: 'auto',
                            backgroundColor: '#ef4444',
                            color: '#ffffff',
                            fontSize: '0.75rem',
                            padding: '0.125rem 0.375rem',
                            borderRadius: '9999px'
                          }}
                        >
                          {item.badge}
                        </span>
                      )}
                    </a>
                  ) : (
                    <button
                      type="button"
                      onClick={(e) => handleItemClick(item, e)}
                      style={{
                        width: '100%',
                        display: 'flex',
                        alignItems: 'center',
                        padding: '0.75rem',
                        background: 'none',
                        border: 'none',
                        color: 'inherit',
                        textAlign: 'left',
                        borderRadius: '0.375rem',
                        cursor: 'pointer',
                        transition: 'background-color 0.2s ease'
                      }}
                    >
                      {item.icon && (
                        <span style={{ marginRight: '0.75rem', fontSize: '1.25rem' }}>
                          {item.icon}
                        </span>
                      )}
                      <span>{item.label}</span>
                      {item.badge && (
                        <span
                          style={{
                            marginLeft: 'auto',
                            backgroundColor: '#ef4444',
                            color: '#ffffff',
                            fontSize: '0.75rem',
                            padding: '0.125rem 0.375rem',
                            borderRadius: '9999px',
                            marginRight: '0.5rem'
                          }}
                        >
                          {item.badge}
                        </span>
                      )}
                      {hasChildren && (
                        <span
                          style={{
                            marginLeft: 'auto',
                            transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                            transition: 'transform 0.2s ease'
                          }}
                        >
                          ▼
                        </span>
                      )}
                    </button>
                  )}

                  {hasChildren && isExpanded && (
                    <ul
                      style={{
                        listStyle: 'none',
                        margin: '0.25rem 0 0 0',
                        padding: 0,
                        marginLeft: '1rem'
                      }}
                    >
                      {item.children!.map(child => {
                        const childIsActive = isItemActive(child);
                        return (
                          <li key={child.id} style={{ marginBottom: '0.25rem' }}>
                            <a
                              href={child.href}
                              target={child.target}
                              onClick={(e) => handleItemClick(child, e)}
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                padding: '0.5rem 0.75rem',
                                textDecoration: 'none',
                                color: 'inherit',
                                borderRadius: '0.375rem',
                                backgroundColor: childIsActive ? (theme === 'dark' ? '#3b82f6' : '#dbeafe') : 'transparent',
                                fontSize: '0.875rem'
                              }}
                            >
                              {child.icon && (
                                <span style={{ marginRight: '0.5rem' }}>
                                  {child.icon}
                                </span>
                              )}
                              <span>{child.label}</span>
                            </a>
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </li>
              );
            })}
          </ul>
        </div>

        {/* Actions */}
        {actions && (
          <div
            style={{
              padding: '1rem',
              borderTop: theme === 'dark' ? '1px solid #374151' : '1px solid #e5e7eb'
            }}
          >
            {actions}
          </div>
        )}
      </div>
    </>
  );
};

// ========================================
// 📦 EXPORTS
// ========================================

export { Navigation as default, Breadcrumb, MobileNavigation };

export type {
  NavigationProps,
  NavigationItem,
  BreadcrumbProps,
  BreadcrumbItem
};

// ========================================
// 🎯 USAGE EXAMPLES
// ========================================

/*
// Horizontal Navigation
<Navigation
  mode="horizontal"
  currentPath="/dashboard"
  items={[
    { id: 'home', label: 'Home', href: '/', icon: '🏠' },
    { id: 'dashboard', label: 'Dashboard', href: '/dashboard', icon: '📊' },
    {
      id: 'products',
      label: 'Products',
      icon: '📦',
      children: [
        { id: 'all-products', label: 'All Products', href: '/products' },
        { id: 'categories', label: 'Categories', href: '/products/categories' }
      ]
    },
    { id: 'settings', label: 'Settings', href: '/settings', icon: '⚙️' }
  ]}
  logo={<img src="/logo.png" alt="Logo" />}
  actions={
    <div>
      <button>Login</button>
      <button>Sign Up</button>
    </div>
  }
/>

// Sidebar Navigation
<Navigation
  mode="sidebar"
  collapsed={sidebarCollapsed}
  currentPath="/dashboard"
  theme="dark"
  items={navigationItems}
  onToggle={setSidebarCollapsed}
  logo={<h2>MyApp</h2>}
/>

// Breadcrumb
<Breadcrumb
  items={[
    { label: 'Home', href: '/', icon: '🏠' },
    { label: 'Products', href: '/products' },
    { label: 'Electronics', href: '/products/electronics' },
    { label: 'Laptops' }
  ]}
  separator=">"
  maxItems={4}
/>

// Mobile Navigation
<MobileNavigation
  isOpen={mobileMenuOpen}
  onClose={() => setMobileMenuOpen(false)}
  items={navigationItems}
  currentPath="/dashboard"
  logo={<h2>MyApp</h2>}
  actions={<button>Logout</button>}
/>
*/