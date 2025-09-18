/**
 * 🧭 Navigation Component Template - UI Component Templates
 * ========================================================
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

import React, { useState, useRef, useEffect, useCallback } from 'react';
import styled, { css, keyframes } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

// ================================
// TYPES & INTERFACES
// ================================

export interface NavigationItem {
  id: string;
  label: string;
  href?: string;
  icon?: React.ReactNode;
  badge?: string | number;
  disabled?: boolean;
  active?: boolean;
  children?: NavigationItem[];
  onClick?: (item: NavigationItem, event: React.MouseEvent) => void;
  target?: '_blank' | '_self' | '_parent' | '_top';
  className?: string;
}

export interface NavigationProps {
  items: NavigationItem[];
  variant?: 'horizontal' | 'vertical' | 'sidebar' | 'breadcrumb' | 'tabs' | 'pills';
  size?: 'small' | 'medium' | 'large';
  layout?: 'start' | 'center' | 'end' | 'space-between' | 'space-around';
  orientation?: 'horizontal' | 'vertical';
  mode?: 'light' | 'dark' | 'auto';
  collapsible?: boolean;
  collapsed?: boolean;
  defaultCollapsed?: boolean;
  sticky?: boolean;
  bordered?: boolean;
  elevated?: boolean;
  fluid?: boolean;
  animated?: boolean;
  activeKey?: string;
  defaultActiveKey?: string;
  multiple?: boolean;
  trigger?: 'hover' | 'click';
  expandIcon?: React.ReactNode;
  collapseIcon?: React.ReactNode;
  logo?: React.ReactNode;
  actions?: React.ReactNode;
  footer?: React.ReactNode;
  breakpoint?: 'sm' | 'md' | 'lg' | 'xl';
  onItemClick?: (item: NavigationItem, event: React.MouseEvent) => void;
  onActiveChange?: (activeKey: string, item: NavigationItem) => void;
  onCollapse?: (collapsed: boolean) => void;
  onOpenChange?: (openKeys: string[]) => void;
  className?: string;
  style?: React.CSSProperties;
  'data-testid'?: string;
}

export interface SubNavProps {
  items: NavigationItem[];
  parentKey: string;
  level: number;
  onItemClick?: (item: NavigationItem, event: React.MouseEvent) => void;
}

// ================================
// ANIMATIONS
// ================================

const slideIn = keyframes`
  from { transform: translateX(-100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
`;

const slideDown = keyframes`
  from { transform: translateY(-10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
`;

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`;

const pulse = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
`;

// ================================
// STYLED COMPONENTS
// ================================

const NavigationContainer = styled.nav<{
  variant: string;
  size: string;
  mode: string;
  orientation: string;
  sticky?: boolean;
  bordered?: boolean;
  elevated?: boolean;
  fluid?: boolean;
  collapsed?: boolean;
}>`
  position: relative;
  display: flex;
  font-family: inherit;
  
  ${({ variant, orientation }) => {
    if (variant === 'horizontal' || variant === 'tabs' || variant === 'pills') {
      return css`
        flex-direction: row;
        align-items: center;
        width: 100%;
      `;
    }
    
    if (variant === 'vertical' || variant === 'sidebar') {
      return css`
        flex-direction: column;
        min-height: 100vh;
        width: ${orientation === 'vertical' ? '280px' : '100%'};
        transition: width 0.3s ease;
      `;
    }
    
    if (variant === 'breadcrumb') {
      return css`
        flex-direction: row;
        align-items: center;
        flex-wrap: wrap;
      `;
    }
    
    return css`
      flex-direction: row;
      align-items: center;
    `;
  }}
  
  ${({ collapsed, variant }) => collapsed && variant === 'sidebar' && css`
    width: 80px;
  `}
  
  ${({ mode }) => {
    switch (mode) {
      case 'dark':
        return css`
          background: #1f2937;
          color: #f9fafb;
          border-color: #374151;
        `;
      case 'light':
        return css`
          background: #ffffff;
          color: #111827;
          border-color: #e5e7eb;
        `;
      default:
        return css`
          background: #ffffff;
          color: #111827;
          border-color: #e5e7eb;
          
          @media (prefers-color-scheme: dark) {
            background: #1f2937;
            color: #f9fafb;
            border-color: #374151;
          }
        `;
    }
  }}
  
  ${({ sticky }) => sticky && css`
    position: sticky;
    top: 0;
    z-index: 1000;
  `}
  
  ${({ bordered }) => bordered && css`
    border: 1px solid currentColor;
    border-opacity: 0.1;
  `}
  
  ${({ elevated }) => elevated && css`
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 
                0 2px 4px -1px rgba(0, 0, 0, 0.06);
  `}
  
  ${({ fluid }) => !fluid && css`
    max-width: 1200px;
    margin: 0 auto;
  `}
  
  ${({ size }) => {
    switch (size) {
      case 'small':
        return css`
          font-size: 0.875rem;
          --nav-padding: 8px 12px;
          --nav-gap: 4px;
        `;
      case 'large':
        return css`
          font-size: 1.125rem;
          --nav-padding: 16px 24px;
          --nav-gap: 12px;
        `;
      default:
        return css`
          font-size: 1rem;
          --nav-padding: 12px 16px;
          --nav-gap: 8px;
        `;
    }
  }}
`;

const NavigationHeader = styled.div<{ collapsed?: boolean }>`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--nav-padding);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
  
  .nav-logo {
    display: flex;
    align-items: center;
    gap: var(--nav-gap);
    font-weight: 600;
    text-decoration: none;
    color: inherit;
    transition: opacity 0.3s ease;
    
    ${({ collapsed }) => collapsed && css`
      .logo-text {
        opacity: 0;
        width: 0;
        overflow: hidden;
      }
    `}
  }
  
  .nav-toggle {
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
    padding: 8px;
    border-radius: 4px;
    transition: background 0.2s ease;
    
    &:hover {
      background: rgba(0, 0, 0, 0.05);
    }
  }
`;

const NavigationList = styled.ul<{
  variant: string;
  layout: string;
  orientation: string;
  level?: number;
}>`
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  
  ${({ variant, orientation, layout }) => {
    if (variant === 'horizontal' || variant === 'tabs' || variant === 'pills') {
      return css`
        flex-direction: row;
        align-items: center;
        gap: var(--nav-gap);
        flex: 1;
        
        ${layout === 'center' && css`justify-content: center;`}
        ${layout === 'end' && css`justify-content: flex-end;`}
        ${layout === 'space-between' && css`justify-content: space-between;`}
        ${layout === 'space-around' && css`justify-content: space-around;`}
      `;
    }
    
    if (variant === 'vertical' || variant === 'sidebar') {
      return css`
        flex-direction: column;
        flex: 1;
        padding: var(--nav-gap) 0;
      `;
    }
    
    if (variant === 'breadcrumb') {
      return css`
        flex-direction: row;
        align-items: center;
        gap: var(--nav-gap);
      `;
    }
    
    return css`
      flex-direction: row;
      align-items: center;
      gap: var(--nav-gap);
    `;
  }}
  
  ${({ level = 0 }) => level > 0 && css`
    padding-left: ${level * 20}px;
  `}
`;

const NavigationItem = styled.li<{
  variant: string;
  active?: boolean;
  disabled?: boolean;
  hasChildren?: boolean;
  level?: number;
}>`
  position: relative;
  display: flex;
  
  ${({ variant }) => {
    if (variant === 'breadcrumb') {
      return css`
        &:not(:last-child)::after {
          content: '/';
          margin: 0 8px;
          opacity: 0.5;
        }
      `;
    }
  }}
  
  ${({ disabled }) => disabled && css`
    opacity: 0.5;
    pointer-events: none;
  `}
`;

const NavigationLink = styled.a<{
  variant: string;
  active?: boolean;
  hasChildren?: boolean;
  collapsed?: boolean;
}>`
  display: flex;
  align-items: center;
  gap: var(--nav-gap);
  padding: var(--nav-padding);
  color: inherit;
  text-decoration: none;
  border-radius: 6px;
  transition: all 0.2s ease;
  position: relative;
  width: 100%;
  cursor: pointer;
  
  .nav-icon {
    flex-shrink: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .nav-label {
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: opacity 0.3s ease;
    
    ${({ collapsed }) => collapsed && css`
      opacity: 0;
      width: 0;
    `}
  }
  
  .nav-badge {
    background: #ef4444;
    color: white;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 10px;
    min-width: 18px;
    text-align: center;
    line-height: 1.2;
  }
  
  .nav-arrow {
    transition: transform 0.2s ease;
    width: 16px;
    height: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &.expanded {
      transform: rotate(90deg);
    }
  }
  
  ${({ variant, active }) => {
    if (variant === 'tabs') {
      return css`
        border-bottom: 3px solid transparent;
        padding-bottom: calc(var(--nav-padding) - 3px);
        border-radius: 0;
        
        ${active && css`
          border-bottom-color: #3b82f6;
          color: #3b82f6;
        `}
        
        &:hover:not(.active) {
          border-bottom-color: rgba(59, 130, 246, 0.3);
        }
      `;
    }
    
    if (variant === 'pills') {
      return css`
        ${active && css`
          background: #3b82f6;
          color: white;
        `}
        
        &:hover:not(.active) {
          background: rgba(59, 130, 246, 0.1);
        }
      `;
    }
    
    if (variant === 'breadcrumb') {
      return css`
        padding: 4px 8px;
        
        ${active && css`
          font-weight: 600;
          color: #3b82f6;
        `}
        
        &:hover:not(.active) {
          color: #3b82f6;
          text-decoration: underline;
        }
      `;
    }
    
    return css`
      ${active && css`
        background: rgba(59, 130, 246, 0.1);
        color: #3b82f6;
        border-left: 3px solid #3b82f6;
        padding-left: calc(var(--nav-padding) - 3px);
      `}
      
      &:hover:not(.active) {
        background: rgba(0, 0, 0, 0.05);
      }
      
      &:focus {
        outline: 2px solid #3b82f6;
        outline-offset: 2px;
      }
    `;
  }}
`;

const SubNavigation = styled(motion.div)<{ variant: string }>`
  overflow: hidden;
  
  ${({ variant }) => {
    if (variant === 'horizontal') {
      return css`
        position: absolute;
        top: 100%;
        left: 0;
        background: inherit;
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 6px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        min-width: 200px;
        z-index: 1000;
      `;
    }
    
    return css`
      width: 100%;
    `;
  }}
`;

const NavigationFooter = styled.div`
  padding: var(--nav-padding);
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  margin-top: auto;
`;

const MobileOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  display: none;
  
  @media (max-width: 768px) {
    display: block;
  }
`;

const MobileDrawer = styled(motion.div)<{ mode: string }>`
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 280px;
  z-index: 1000;
  display: none;
  
  ${({ mode }) => {
    switch (mode) {
      case 'dark':
        return css`
          background: #1f2937;
          color: #f9fafb;
        `;
      default:
        return css`
          background: #ffffff;
          color: #111827;
        `;
    }
  }}
  
  @media (max-width: 768px) {
    display: flex;
    flex-direction: column;
  }
`;

// ================================
// CUSTOM HOOKS
// ================================

const useNavigation = (
  items: NavigationItem[],
  defaultActiveKey?: string,
  multiple?: boolean
) => {
  const [activeKey, setActiveKey] = useState(defaultActiveKey || '');
  const [openKeys, setOpenKeys] = useState<string[]>([]);
  
  const handleItemClick = useCallback((item: NavigationItem, event: React.MouseEvent) => {
    if (item.disabled) return;
    
    if (item.children && item.children.length > 0) {
      // Toggle submenu
      setOpenKeys(prev => {
        const isOpen = prev.includes(item.id);
        if (multiple) {
          return isOpen
            ? prev.filter(key => key !== item.id)
            : [...prev, item.id];
        } else {
          return isOpen ? [] : [item.id];
        }
      });
    } else {
      // Set active item
      setActiveKey(item.id);
    }
    
    item.onClick?.(item, event);
  }, [multiple]);
  
  return {
    activeKey,
    openKeys,
    setActiveKey,
    setOpenKeys,
    handleItemClick,
  };
};

const useResponsive = (breakpoint: string = 'md') => {
  const [isMobile, setIsMobile] = useState(false);
  
  useEffect(() => {
    const breakpoints = {
      sm: 576,
      md: 768,
      lg: 992,
      xl: 1200,
    };
    
    const checkIsMobile = () => {
      setIsMobile(window.innerWidth < breakpoints[breakpoint]);
    };
    
    checkIsMobile();
    window.addEventListener('resize', checkIsMobile);
    
    return () => window.removeEventListener('resize', checkIsMobile);
  }, [breakpoint]);
  
  return isMobile;
};

// ================================
// SUB COMPONENTS
// ================================

const SubNav: React.FC<SubNavProps> = ({
  items,
  parentKey,
  level,
  onItemClick,
}) => {
  return (
    <NavigationList variant="vertical" layout="start" orientation="vertical" level={level}>
      {items.map((item) => (
        <NavigationItem
          key={item.id}
          variant="vertical"
          active={item.active}
          disabled={item.disabled}
          hasChildren={!!(item.children && item.children.length > 0)}
          level={level}
        >
          <NavigationLink
            variant="vertical"
            active={item.active}
            hasChildren={!!(item.children && item.children.length > 0)}
            href={item.href}
            target={item.target}
            onClick={(e) => {
              if (!item.href) e.preventDefault();
              onItemClick?.(item, e);
            }}
            className={item.className}
          >
            {item.icon && <span className="nav-icon">{item.icon}</span>}
            <span className="nav-label">{item.label}</span>
            {item.badge && <span className="nav-badge">{item.badge}</span>}
            {item.children && item.children.length > 0 && (
              <span className="nav-arrow">▶</span>
            )}
          </NavigationLink>
          
          {item.children && item.children.length > 0 && (
            <SubNav
              items={item.children}
              parentKey={item.id}
              level={level + 1}
              onItemClick={onItemClick}
            />
          )}
        </NavigationItem>
      ))}
    </NavigationList>
  );
};

// ================================
// MAIN COMPONENT
// ================================

export const Navigation: React.FC<NavigationProps> = ({
  items,
  variant = 'horizontal',
  size = 'medium',
  layout = 'start',
  orientation = 'horizontal',
  mode = 'light',
  collapsible = false,
  collapsed: controlledCollapsed,
  defaultCollapsed = false,
  sticky = false,
  bordered = false,
  elevated = false,
  fluid = false,
  animated = true,
  activeKey,
  defaultActiveKey,
  multiple = false,
  trigger = 'click',
  expandIcon,
  collapseIcon,
  logo,
  actions,
  footer,
  breakpoint = 'md',
  onItemClick,
  onActiveChange,
  onCollapse,
  onOpenChange,
  className,
  style,
  'data-testid': testId,
}) => {
  const [internalCollapsed, setInternalCollapsed] = useState(defaultCollapsed);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  const collapsed = controlledCollapsed !== undefined ? controlledCollapsed : internalCollapsed;
  const isMobile = useResponsive(breakpoint);
  
  const {
    activeKey: currentActiveKey,
    openKeys,
    setActiveKey,
    setOpenKeys,
    handleItemClick,
  } = useNavigation(items, activeKey || defaultActiveKey, multiple);
  
  const handleToggleCollapse = useCallback(() => {
    const newCollapsed = !collapsed;
    setInternalCollapsed(newCollapsed);
    onCollapse?.(newCollapsed);
  }, [collapsed, onCollapse]);
  
  const handleItemClickInternal = useCallback((item: NavigationItem, event: React.MouseEvent) => {
    handleItemClick(item, event);
    onItemClick?.(item, event);
    
    if (item.active !== undefined) {
      onActiveChange?.(item.id, item);
    }
    
    if (isMobile) {
      setMobileMenuOpen(false);
    }
  }, [handleItemClick, onItemClick, onActiveChange, isMobile]);
  
  const renderNavigationItems = (navItems: NavigationItem[], level = 0) => (
    <NavigationList
      variant={variant}
      layout={layout}
      orientation={orientation}
      level={level}
    >
      {navItems.map((item) => {
        const isActive = activeKey ? item.id === activeKey : item.active;
        const isOpen = openKeys.includes(item.id);
        const hasChildren = item.children && item.children.length > 0;
        
        return (
          <NavigationItem
            key={item.id}
            variant={variant}
            active={isActive}
            disabled={item.disabled}
            hasChildren={hasChildren}
            level={level}
          >
            <NavigationLink
              variant={variant}
              active={isActive}
              hasChildren={hasChildren}
              collapsed={collapsed}
              href={item.href}
              target={item.target}
              onClick={(e) => {
                if (!item.href) e.preventDefault();
                handleItemClickInternal(item, e);
              }}
              className={`${item.className || ''} ${isActive ? 'active' : ''}`}
              title={collapsed ? item.label : undefined}
            >
              {item.icon && <span className="nav-icon">{item.icon}</span>}
              <span className="nav-label">{item.label}</span>
              {item.badge && <span className="nav-badge">{item.badge}</span>}
              {hasChildren && (
                <span className={`nav-arrow ${isOpen ? 'expanded' : ''}`}>
                  {expandIcon || '▶'}
                </span>
              )}
            </NavigationLink>
            
            {hasChildren && isOpen && (variant === 'vertical' || variant === 'sidebar') && (
              <SubNavigation
                variant={variant}
                initial={animated ? { height: 0, opacity: 0 } : false}
                animate={animated ? { height: 'auto', opacity: 1 } : false}
                exit={animated ? { height: 0, opacity: 0 } : false}
                transition={{ duration: 0.2 }}
              >
                {renderNavigationItems(item.children!, level + 1)}
              </SubNavigation>
            )}
            
            {hasChildren && trigger === 'hover' && variant === 'horizontal' && (
              <SubNavigation
                variant={variant}
                initial={animated ? { opacity: 0, y: -10 } : false}
                animate={animated ? { opacity: 1, y: 0 } : false}
                exit={animated ? { opacity: 0, y: -10 } : false}
                transition={{ duration: 0.15 }}
              >
                {renderNavigationItems(item.children!, level + 1)}
              </SubNavigation>
            )}
          </NavigationItem>
        );
      })}
    </NavigationList>
  );
  
  // Mobile view
  if (isMobile && (variant === 'sidebar' || variant === 'vertical')) {
    return (
      <>
        <NavigationContainer
          variant="horizontal"
          size={size}
          mode={mode}
          orientation="horizontal"
          sticky={sticky}
          bordered={bordered}
          elevated={elevated}
          fluid={fluid}
          className={className}
          style={style}
          data-testid={testId}
        >
          <NavigationHeader>
            {logo && <div className="nav-logo">{logo}</div>}
            <button
              className="nav-toggle"
              onClick={() => setMobileMenuOpen(true)}
              aria-label="Open menu"
            >
              ☰
            </button>
          </NavigationHeader>
          {actions && <div style={{ marginLeft: 'auto' }}>{actions}</div>}
        </NavigationContainer>
        
        <AnimatePresence>
          {mobileMenuOpen && (
            <>
              <MobileOverlay
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setMobileMenuOpen(false)}
              />
              <MobileDrawer
                mode={mode}
                initial={{ x: '-100%' }}
                animate={{ x: 0 }}
                exit={{ x: '-100%' }}
                transition={{ type: 'tween', duration: 0.3 }}
              >
                <NavigationHeader>
                  {logo && <div className="nav-logo">{logo}</div>}
                  <button
                    className="nav-toggle"
                    onClick={() => setMobileMenuOpen(false)}
                    aria-label="Close menu"
                  >
                    ✕
                  </button>
                </NavigationHeader>
                {renderNavigationItems(items)}
                {footer && <NavigationFooter>{footer}</NavigationFooter>}
              </MobileDrawer>
            </>
          )}
        </AnimatePresence>
      </>
    );
  }
  
  return (
    <NavigationContainer
      variant={variant}
      size={size}
      mode={mode}
      orientation={orientation}
      sticky={sticky}
      bordered={bordered}
      elevated={elevated}
      fluid={fluid}
      collapsed={collapsed}
      className={className}
      style={style}
      data-testid={testId}
    >
      {(variant === 'sidebar' || variant === 'vertical') && (logo || collapsible) && (
        <NavigationHeader collapsed={collapsed}>
          {logo && <div className="nav-logo">{logo}</div>}
          {collapsible && (
            <button
              className="nav-toggle"
              onClick={handleToggleCollapse}
              aria-label={collapsed ? 'Expand menu' : 'Collapse menu'}
            >
              {collapsed ? (expandIcon || '→') : (collapseIcon || '←')}
            </button>
          )}
        </NavigationHeader>
      )}
      
      {renderNavigationItems(items)}
      
      {actions && variant === 'horizontal' && (
        <div style={{ marginLeft: 'auto' }}>{actions}</div>
      )}
      
      {footer && (variant === 'sidebar' || variant === 'vertical') && (
        <NavigationFooter>{footer}</NavigationFooter>
      )}
    </NavigationContainer>
  );
};

// ================================
// UTILITY COMPONENTS
// ================================

export const HorizontalNav: React.FC<Partial<NavigationProps>> = (props) => (
  <Navigation variant="horizontal" layout="start" {...props} />
);

export const Sidebar: React.FC<Partial<NavigationProps>> = (props) => (
  <Navigation
    variant="sidebar"
    orientation="vertical"
    collapsible
    elevated
    {...props}
  />
);

export const TabsNav: React.FC<Partial<NavigationProps>> = (props) => (
  <Navigation variant="tabs" layout="start" bordered {...props} />
);

export const PillsNav: React.FC<Partial<NavigationProps>> = (props) => (
  <Navigation variant="pills" layout="start" {...props} />
);

export const Breadcrumb: React.FC<Partial<NavigationProps>> = (props) => (
  <Navigation variant="breadcrumb" size="small" {...props} />
);

// ================================
// EXPORTS
// ================================

export default Navigation;

export type {
  NavigationProps,
  NavigationItem,
  SubNavProps,
};

/**
 * 🧭 Example Usage:
 * 
 * ```tsx
 * const navigationItems: NavigationItem[] = [
 *   {
 *     id: 'dashboard',
 *     label: 'Dashboard',
 *     href: '/dashboard',
 *     icon: '📊',
 *     active: true
 *   },
 *   {
 *     id: 'products',
 *     label: 'Products',
 *     icon: '📦',
 *     badge: '12',
 *     children: [
 *       { id: 'all-products', label: 'All Products', href: '/products' },
 *       { id: 'add-product', label: 'Add Product', href: '/products/new' }
 *     ]
 *   },
 *   {
 *     id: 'settings',
 *     label: 'Settings',
 *     href: '/settings',
 *     icon: '⚙️'
 *   }
 * ];
 * 
 * // Horizontal Navigation
 * <Navigation
 *   items={navigationItems}
 *   variant="horizontal"
 *   logo={<img src="/logo.png" alt="Logo" />}
 *   actions={<button>Login</button>}
 * />
 * 
 * // Sidebar Navigation
 * <Sidebar
 *   items={navigationItems}
 *   logo="My App"
 *   collapsible
 *   defaultCollapsed={false}
 * />
 * 
 * // Tabs Navigation
 * <TabsNav
 *   items={navigationItems}
 *   activeKey="dashboard"
 * />
 * ```
 */