/**
 * 🏗️ SIDEBAR LAYOUT TEMPLATE - ENTERPRISE NAVIGATION
 * ==================================================
 * 
 * Advanced Sidebar Layout for Ainflue Creator Economy
 * Collapsible navigation, hierarchical menus, responsive design
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

import React, { useState, useEffect, createContext, useContext } from 'react';
import styled, { css } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

// Sidebar Interfaces
export interface SidebarProps {
  navigation: SidebarSection[];
  collapsed?: boolean;
  collapsible?: boolean;
  position?: 'left' | 'right';
  variant?: 'standard' | 'rail' | 'modal' | 'mini';
  width?: number;
  collapsedWidth?: number;
  overlay?: boolean;
  persistent?: boolean;
  className?: string;
  children?: React.ReactNode;
  onToggle?: (collapsed: boolean) => void;
  onItemClick?: (item: SidebarItem) => void;
}

export interface SidebarSection {
  id: string;
  title?: string;
  items: SidebarItem[];
  collapsible?: boolean;
  defaultExpanded?: boolean;
}

export interface SidebarItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  href?: string;
  badge?: string | number;
  active?: boolean;
  disabled?: boolean;
  children?: SidebarItem[];
  metadata?: {
    tooltip?: string;
    shortcut?: string;
    description?: string;
  };
  onClick?: () => void;
}

// Context for Sidebar State
interface SidebarContextType {
  collapsed: boolean;
  toggle: () => void;
  activeItem: string | null;
  setActiveItem: (id: string | null) => void;
}

const SidebarContext = createContext<SidebarContextType | undefined>(undefined);

// Styled Components
const SidebarContainer = styled(motion.aside)<{
  $collapsed: boolean;
  $position: string;
  $width: number;
  $collapsedWidth: number;
  $variant: string;
  $overlay: boolean;
}>`
  position: ${props => props.$overlay ? 'fixed' : 'relative'};
  top: 0;
  ${props => props.$position}: 0;
  bottom: 0;
  z-index: var(--z-sidebar, 1200);
  
  width: ${props => props.$collapsed ? `${props.$collapsedWidth}px` : `${props.$width}px`};
  min-height: 100vh;
  
  background: var(--color-surface, #f8fafc);
  border-${props => props.$position === 'left' ? 'right' : 'left'}: 1px solid var(--color-border, #e2e8f0);
  
  transition: width var(--motion-duration-moderate, 200ms) var(--motion-easing-standard, ease-in-out);
  
  ${props => props.$variant === 'rail' && css`
    width: ${props.$collapsed ? '72px' : '256px'};
  `}
  
  ${props => props.$variant === 'modal' && css`
    position: fixed;
    box-shadow: var(--shadow-xl, 0 20px 25px -5px rgb(0 0 0 / 0.1));
    background: var(--color-background, #ffffff);
  `}
  
  ${props => props.$variant === 'mini' && css`
    width: 72px;
  `}
  
  @media (max-width: 768px) {
    position: fixed;
    z-index: var(--z-modal, 1400);
    box-shadow: var(--shadow-xl, 0 20px 25px -5px rgb(0 0 0 / 0.1));
    background: var(--color-background, #ffffff);
  }
`;

const SidebarOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: var(--z-overlay, 1300);
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  
  @media (min-width: 769px) {
    display: none;
  }
`;

const SidebarHeader = styled.div<{ $collapsed: boolean }>`
  display: flex;
  align-items: center;
  justify-content: ${props => props.$collapsed ? 'center' : 'space-between'};
  padding: var(--spacing-4, 1rem) var(--spacing-4, 1rem);
  border-bottom: 1px solid var(--color-border, #e2e8f0);
  min-height: 64px;
`;

const SidebarLogo = styled.div<{ $collapsed: boolean }>`
  display: flex;
  align-items: center;
  gap: var(--spacing-3, 0.75rem);
  color: var(--color-text-primary, #0f172a);
  font-weight: var(--typography-weight-bold, 700);
  font-size: var(--typography-title-large, 1.125rem);
  
  ${props => props.$collapsed && css`
    .logo-text {
      display: none;
    }
  `}
`;

const SidebarToggle = styled.button<{ $collapsed: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: var(--radius-md, 0.375rem);
  color: var(--color-text-secondary, #475569);
  cursor: pointer;
  
  transition: all var(--motion-duration-fast, 150ms);
  
  &:hover {
    background: var(--color-surface, #f8fafc);
    border-color: var(--color-primary-500, #0ea5e9);
    color: var(--color-primary-500, #0ea5e9);
  }
  
  ${props => props.$collapsed && css`
    transform: rotate(180deg);
  `}
`;

const SidebarContent = styled.div`
  display: flex;
  flex-direction: column;
  height: calc(100vh - 64px);
  overflow-y: auto;
  overflow-x: hidden;
  padding: var(--spacing-4, 1rem) 0;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--color-border, #e2e8f0);
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb:hover {
    background: var(--color-secondary-400, #94a3b8);
  }
`;

const SidebarSection = styled.div<{ $collapsed: boolean }>`
  margin-bottom: var(--spacing-6, 1.5rem);
`;

const SidebarSectionTitle = styled.h3<{ $collapsed: boolean; $expanded: boolean }>`
  display: ${props => props.$collapsed ? 'none' : 'flex'};
  align-items: center;
  justify-content: space-between;
  margin: 0 0 var(--spacing-2, 0.5rem) 0;
  padding: 0 var(--spacing-4, 1rem);
  color: var(--color-text-muted, #94a3b8);
  font-size: var(--typography-label-small, 0.75rem);
  font-weight: var(--typography-weight-semibold, 600);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  
  &::after {
    content: '${props => props.$expanded ? '−' : '+'}';
    font-size: var(--typography-body-medium, 1rem);
  }
`;

const SidebarNav = styled.nav`
  display: flex;
  flex-direction: column;
`;

const SidebarItemContainer = styled.div<{ $level: number; $collapsed: boolean }>`
  padding-left: ${props => 
    props.$collapsed ? '0' : `${props.$level * 16 + 16}px`
  };
`;

const SidebarItemLink = styled.a<{
  $active: boolean;
  $disabled: boolean;
  $collapsed: boolean;
  $hasChildren: boolean;
}>`
  display: flex;
  align-items: center;
  gap: var(--spacing-3, 0.75rem);
  padding: var(--spacing-2, 0.5rem) var(--spacing-4, 1rem);
  margin: 0 var(--spacing-2, 0.5rem);
  text-decoration: none;
  color: var(--color-text-secondary, #475569);
  font-weight: var(--typography-weight-medium, 500);
  font-size: var(--typography-body-medium, 1rem);
  border-radius: var(--radius-md, 0.375rem);
  position: relative;
  
  transition: all var(--motion-duration-fast, 150ms);
  
  ${props => props.$collapsed && css`
    justify-content: center;
    padding: var(--spacing-3, 0.75rem);
    margin: var(--spacing-1, 0.25rem) var(--spacing-2, 0.5rem);
    
    .item-label,
    .item-badge,
    .item-arrow {
      display: none;
    }
  `}
  
  ${props => props.$active && css`
    background: var(--color-primary-50, #f0f9ff);
    color: var(--color-primary-700, #0369a1);
    
    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 3px;
      background: var(--color-primary-500, #0ea5e9);
      border-radius: 0 2px 2px 0;
    }
  `}
  
  ${props => props.$disabled && css`
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
  `}
  
  &:hover:not(:disabled) {
    background: ${props => 
      props.$active ? 
      'var(--color-primary-100, #e0f2fe)' : 
      'var(--color-surface-hover, #f1f5f9)'
    };
    color: ${props => 
      props.$active ? 
      'var(--color-primary-800, #075985)' : 
      'var(--color-text-primary, #0f172a)'
    };
  }
`;

const SidebarItemIcon = styled.div<{ $collapsed: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  
  svg {
    width: 100%;
    height: 100%;
  }
`;

const SidebarItemLabel = styled.span`
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const SidebarItemBadge = styled.span`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 6px;
  background: var(--color-primary-500, #0ea5e9);
  color: white;
  font-size: 11px;
  font-weight: var(--typography-weight-bold, 700);
  border-radius: 9px;
`;

const SidebarItemArrow = styled.div<{ $expanded: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  color: var(--color-text-muted, #94a3b8);
  transform: ${props => props.$expanded ? 'rotate(90deg)' : 'rotate(0deg)'};
  transition: transform var(--motion-duration-fast, 150ms);
  
  &::before {
    content: '›';
    font-size: 14px;
    font-weight: bold;
  }
`;

const SidebarTooltip = styled.div<{ $show: boolean }>`
  position: absolute;
  left: calc(100% + 12px);
  top: 50%;
  transform: translateY(-50%);
  z-index: var(--z-tooltip, 1800);
  
  padding: var(--spacing-2, 0.5rem) var(--spacing-3, 0.75rem);
  background: var(--color-text-primary, #0f172a);
  color: var(--color-text-inverse, #ffffff);
  font-size: var(--typography-label-small, 0.75rem);
  border-radius: var(--radius-md, 0.375rem);
  white-space: nowrap;
  pointer-events: none;
  
  opacity: ${props => props.$show ? 1 : 0};
  visibility: ${props => props.$show ? 'visible' : 'hidden'};
  transition: all var(--motion-duration-fast, 150ms);
  
  &::before {
    content: '';
    position: absolute;
    right: 100%;
    top: 50%;
    transform: translateY(-50%);
    border: 4px solid transparent;
    border-right-color: var(--color-text-primary, #0f172a);
  }
`;

// Sidebar Item Component
const SidebarItemComponent: React.FC<{
  item: SidebarItem;
  level: number;
  parentId?: string;
}> = ({ item, level, parentId }) => {
  const context = useContext(SidebarContext);
  const [expanded, setExpanded] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);
  
  if (!context) {
    throw new Error('SidebarItem must be used within SidebarLayoutTemplate');
  }
  
  const { collapsed, activeItem, setActiveItem } = context;
  const isActive = activeItem === item.id;
  const hasChildren = item.children && item.children.length > 0;
  
  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    
    if (item.disabled) return;
    
    if (hasChildren) {
      setExpanded(!expanded);
    } else {
      setActiveItem(item.id);
      item.onClick?.();
    }
  };
  
  return (
    <>
      <SidebarItemContainer $level={level} $collapsed={collapsed}>
        <SidebarItemLink
          href={item.href || '#'}
          $active={isActive}
          $disabled={!!item.disabled}
          $collapsed={collapsed}
          $hasChildren={hasChildren}
          onClick={handleClick}
          onMouseEnter={() => collapsed && setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
        >
          {item.icon && (
            <SidebarItemIcon $collapsed={collapsed}>
              {item.icon}
            </SidebarItemIcon>
          )}
          
          <SidebarItemLabel className="item-label">
            {item.label}
          </SidebarItemLabel>
          
          {item.badge && (
            <SidebarItemBadge className="item-badge">
              {item.badge}
            </SidebarItemBadge>
          )}
          
          {hasChildren && (
            <SidebarItemArrow 
              className="item-arrow"
              $expanded={expanded} 
            />
          )}
          
          {collapsed && item.metadata?.tooltip && (
            <SidebarTooltip $show={showTooltip}>
              {item.metadata.tooltip}
            </SidebarTooltip>
          )}
        </SidebarItemLink>
      </SidebarItemContainer>
      
      <AnimatePresence>
        {hasChildren && expanded && !collapsed && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            style={{ overflow: 'hidden' }}
          >
            {item.children?.map((child) => (
              <SidebarItemComponent
                key={child.id}
                item={child}
                level={level + 1}
                parentId={item.id}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

// Main Sidebar Component
export const SidebarLayoutTemplate: React.FC<SidebarProps> = ({
  navigation,
  collapsed: controlledCollapsed,
  collapsible = true,
  position = 'left',
  variant = 'standard',
  width = 256,
  collapsedWidth = 72,
  overlay = false,
  persistent = true,
  className,
  children,
  onToggle,
  onItemClick,
}) => {
  const [internalCollapsed, setInternalCollapsed] = useState(false);
  const [activeItem, setActiveItem] = useState<string | null>(null);
  const [sectionStates, setSectionStates] = useState<Record<string, boolean>>({});
  
  const collapsed = controlledCollapsed !== undefined ? controlledCollapsed : internalCollapsed;
  
  useEffect(() => {
    // Initialize section states
    const initialStates: Record<string, boolean> = {};
    navigation.forEach(section => {
      initialStates[section.id] = section.defaultExpanded !== false;
    });
    setSectionStates(initialStates);
  }, [navigation]);
  
  const handleToggle = () => {
    const newCollapsed = !collapsed;
    if (controlledCollapsed === undefined) {
      setInternalCollapsed(newCollapsed);
    }
    onToggle?.(newCollapsed);
  };
  
  const toggleSection = (sectionId: string) => {
    setSectionStates(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId],
    }));
  };
  
  const contextValue: SidebarContextType = {
    collapsed,
    toggle: handleToggle,
    activeItem,
    setActiveItem: (id) => {
      setActiveItem(id);
      if (id) {
        const findItem = (items: SidebarItem[]): SidebarItem | null => {
          for (const item of items) {
            if (item.id === id) return item;
            if (item.children) {
              const found = findItem(item.children);
              if (found) return found;
            }
          }
          return null;
        };
        
        for (const section of navigation) {
          const item = findItem(section.items);
          if (item) {
            onItemClick?.(item);
            break;
          }
        }
      }
    },
  };
  
  return (
    <SidebarContext.Provider value={contextValue}>
      <>
        {overlay && !persistent && (
          <AnimatePresence>
            {!collapsed && (
              <SidebarOverlay
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={handleToggle}
              />
            )}
          </AnimatePresence>
        )}
        
        <SidebarContainer
          $collapsed={collapsed}
          $position={position}
          $width={width}
          $collapsedWidth={collapsedWidth}
          $variant={variant}
          $overlay={overlay}
          className={className}
          initial={false}
          animate={{
            width: collapsed ? collapsedWidth : width,
          }}
          transition={{ duration: 0.2 }}
        >
          <SidebarHeader $collapsed={collapsed}>
            <SidebarLogo $collapsed={collapsed}>
              <div className="logo-icon">🎨</div>
              <span className="logo-text">Ainflue</span>
            </SidebarLogo>
            
            {collapsible && (
              <SidebarToggle
                $collapsed={collapsed}
                onClick={handleToggle}
                aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
              >
                ←
              </SidebarToggle>
            )}
          </SidebarHeader>
          
          <SidebarContent>
            {navigation.map((section) => (
              <SidebarSection key={section.id} $collapsed={collapsed}>
                {section.title && (
                  <SidebarSectionTitle
                    $collapsed={collapsed}
                    $expanded={sectionStates[section.id]}
                    onClick={() => section.collapsible && toggleSection(section.id)}
                  >
                    {section.title}
                  </SidebarSectionTitle>
                )}
                
                <AnimatePresence>
                  {(sectionStates[section.id] || !section.collapsible) && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      style={{ overflow: 'hidden' }}
                    >
                      <SidebarNav>
                        {section.items.map((item) => (
                          <SidebarItemComponent
                            key={item.id}
                            item={item}
                            level={0}
                          />
                        ))}
                      </SidebarNav>
                    </motion.div>
                  )}
                </AnimatePresence>
              </SidebarSection>
            ))}
            
            {children}
          </SidebarContent>
        </SidebarContainer>
      </>
    </SidebarContext.Provider>
  );
};

// Hook for using sidebar context
export const useSidebar = () => {
  const context = useContext(SidebarContext);
  if (!context) {
    throw new Error('useSidebar must be used within SidebarLayoutTemplate');
  }
  return context;
};

// Export types and utilities
export { SidebarContainer, SidebarContent, SidebarNav };
export default SidebarLayoutTemplate;